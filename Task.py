from MES import MES
from Tickable import Tickable


class Task(Tickable):
    """
    This class is used to represent tasks in the system. In this codebase, a "task" is something that an "executable"
    needs to be completed in order to be executed. Tasks include printing, quality inspection etc. but also
    storage and assembly.

    Attributes:
        resources_needed (list[str]): list of resource types that the task needs (matches ResourceManager.rsrc_type)
        resources_used (list[str]): list of resources that the task has used (matches Resource.rsrc_id)
            e.g. a print task would have resources_needed = ["printer"]. Once started on printer0,
            resources_used  = ["printer0"]
        proc_time (int): A guess as to how long the task will take (can use for optimisation)
        time_til_done (int): Starts off as the proc_time, then decrements every time the task runs
        done (bool): Is the task done or not?
        released (bool): Is the task released or not? Tasks are "released" when they are ready to be worked on.
            e.g. A part cannot be quality inspected before it prints, so the qi task is not released until the print
            task finishes
        exec_id (str): the id of the executable that owns the task. Used for lookup.
        task_id (str): id for the task.
        wait_time (int): increments every tick the task is waiting in a queue. Used for metrics.
        start_stamp (int): the time at which the task starts.
        position (int): where the task is in the executable's task list.
    """

    def __init__(self, exec_id, proc_time: int):
        """
        Constructor for the task class
        :param exec_id: passed in
        :param proc_time: passed in
        """
        self.resources_needed: list[str] = []
        self.resources_used: list[str] = []
        self.proc_time: int = proc_time
        self.time_til_done: int = self.proc_time
        self.done: bool = False
        self.released: bool = False
        self.exec_id: str = exec_id
        self.task_id: str = ""
        self.wait_time: int = 0
        self.start_stamp = None
        self.position = 0

    def release(self, mes: MES, position: int):
        """
        This method is used to allow tasks to be released. See above for description of task release.
        Release sets released to true, sets the position in the list, adds itself to the queues of resources it needs.
        :param mes: the manufacturing executing system
        :param position: the position in the executables task list
        :return: None
        """
        self.released = True
        self.position = position
        self.task_id += str(self.position)
        for rsrc_id in self.resources_needed:
            mes.resource_push(rsrc_id, self.task_id)

    def tick(self, mes: MES, clock: int):
        """
        Tick implementation for Tasks.
        :param mes: manufacturing execution system
        :param clock: the current time
        :return: None
        """
        dec_flag = True
        # Do you have all the resources that you need?
        for rsrc_id in self.resources_needed:
            if self.task_id not in mes.resource_managers[rsrc_id].current():
                dec_flag = False
                break
        if dec_flag:
            # If you have all the resources you need, you can decrement time_til_done
            self.time_til_done -= 1

            if not self.started():
                self.start_stamp = clock
                self.start_action(mes, clock)
        elif self.released:
            # If you don't have all the resources you need, but you are released, your wait time should increment.
            self.wait_time += 1

    def set_id(self, action: str):
        """
        Creates ids for the tasks.
        :param action: the nickname for the action
        :return: None
        """
        self.task_id = f"{self.exec_id}_{action}"

    def started(self) -> bool:
        """
        Getter to determine whether a task has been started.
        :return:
        """
        return self.start_stamp is not None

    def start_action(self, mes: MES, clock: int):
        """
        This method allows some code to run when a task starts.
        This is typically used to ensure that resources are released
        :param mes: management execution system
        :param clock: current time
        :return: None
        """
        pass

    def is_done(self) -> bool:
        """
        This method is a getter for the done attribute.
        :return: True if the task is done, False if not
        """
        return self.done

    def set_done(self, mes: MES, clock: int):
        """
        This method marks that a task is done, subsequently releasing its resources.
        :param mes: manufacturing execution system
        :param clock: current time
        :return: None
        """
        self.done = True
        self.release_resources(mes, clock)
        # After releasing the resources, we run the tick method for the executables, to allow them to start a new task
        # immediately
        mes.executables[self.exec_id].tick(mes, clock)

    def release_resources(self, mes: MES, clock: int):
        """
        Asks the mes to release the resources for the resources that have been used.
        :param mes: manufacturing execution system
        :param clock: current time
        :return: None
        """
        for rsrc_id in self.resources_used:
            mes.resource_release(rsrc_id)


class RobotRequester:
    def __init__(self):
        self.robot_prog = 0


class Print(Task):
    """
    Child of the Task class to represent the Print task.
    """

    def __init__(self, exec_id, proc_time):
        super().__init__(exec_id, proc_time)
        self.resources_needed = ["printer"]  # Print task needs a printer
        self.set_id("print")


class QI(Task, RobotRequester):
    """
    Child of the Task class to represent the QI task.
    """

    def __init__(self, exec_id, proc_time: int = 5):
        super().__init__(exec_id, proc_time)
        self.set_id("qi")
        self.resources_needed = ["qi", "robot"]  # QI task needs a qi station and a robot
        self.robot_prog = 4


class Store(Task, RobotRequester):
    """
    Child of the Task class to represent the Store task.
    """

    def __init__(self, exec_id, prev_loc: str, proc_time: int = 3):
        super().__init__(exec_id, proc_time)
        self.set_id("store")
        self.resources_needed = ["robot"]  # Store task needs a robot
        self.prev_loc = prev_loc
        self.robot_prog = 5

    def start_action(self, mes: MES, clock: int):
        """
        This implementation of the start_action method allows the Store task to release the resources for the
        task immediately previous.
        e.g. When we store a part after printing, we need to release the printer.
        :param mes: manufacturing execution system
        :param clock: current time
        :return: None
        """
        # Releasing the resources that the last task is holding
        last_task_used_rsrc = mes.executables[self.exec_id].tasks[self.position - 1].resources_used
        for rsrc in mes.resource_managers[self.prev_loc].resources:
            if rsrc.rsrc_id in last_task_used_rsrc:
                rsrc.part_pickup_handler()


class Assemble(Task, RobotRequester):
    """
    Class to represent the assembly step.

    Attributes:
        part_list: list of part ids of the parts that need to be assembled
    """

    def __init__(self, exec_id, part_list: list[str], proc_time: int = 13):
        super().__init__(exec_id, proc_time)
        self.set_id("assemble")
        self.resources_needed = ["robot"]  # We need a robot to assemble
        self.part_list = part_list
        self.robot_prog = 6

    def release(self, mes: MES, position: int):
        """
        This task requires a slight modification to the base class release method. It should not release until
        all the parts in the part list are ready.
        :param mes: manufacturing execution system
        :param position: the position in the task list for the executable
        :return: None
        """
        for part_id in self.part_list:
            part = mes.executables[part_id]
            if part.done_stamp == 0:
                return
        super().release(mes, position)


class Finish(Task):
    """
    This task class represents moving the completed job to a finished section, ready for customer pickup.
    """

    def __init__(self, exec_id, proc_time: int = 3):
        super().__init__(exec_id, proc_time)
        self.set_id("finish")
        self.resources_needed = ["robot"]  # Finish needs a robot to store


