from DBInterface import DBInterface
from MES import MES
from Resource import *
from Tickable import Tickable


class ResourceManager(Tickable):
    """
    This abstract class represents a resource manager. A resource manager holds a collection of an individual resource
    and allocates tasks to each resource.
    For example, a PrintManager has a collection of Printers and allocates Tasks to those printers.

    Attributes:
        resources (list[Resource]): a list of resources that the ResourceManager manages
        queue (list[str]): a list of task ids. The tasks are queuing for access to the resource.
        rsrc_type (str): a string for the type of resource (e.g. printer, robot etc)
        no_units: the number of resources managed.
    """

    def __init__(self, no_units: int, rsrc_type: str):
        """
        Constructor for the ResourceManager
        :param no_units: the number of resources managed
        :param rsrc_type: a string for the type of resource (e.g. printer, robot etc)
        """
        self.resources: list[Resource] = []
        self.queue: list[str] = []
        self.rsrc_type: str = rsrc_type  # Can get rid of this by having it start as a default value then having it set by the child class. 
        self.no_units = no_units
        self.set_up_resources()

    def set_up_resources(self):
        """
        This method runs inside the ResourceManager constructor, adding each resource to the managers list of resources
        :return: None
        """
        pass

    def tick(self, mes: MES, clock: int):  # You can write one of these for each of the subclasses, they're different
        """
        Tick method signature for Resource Managers
        :param mes: the manufacturing execution system
        :param clock: the current time
        :return: None
        """
        pass

    def grab_next(self, mes: MES, clock: int) -> str:
        """
        This method grabs the next task from the task list. The default implementation uses FIFO, this can be overriden
        in subclasses for optimisation. The clock and the mes aren't currently used, but would be necessary for
        optimisation. 
        :param mes: the manufacturing execution system
        :param clock: the current time
        :return: string id of the next task
        """
        if not len(self.queue) == 0:
            return self.queue.pop(0)

    def default_ready_action(self, rsrc: Resource, mes: MES, clock: int):
        """
        If a resource is in the ready state, the ResourceManager needs to allocate it a task (if tasks are available).
        This method plays that role. 
        :param rsrc: the resource in the ready state
        :param mes:  the manufacturing execution system
        :param clock: the current time
        :return: None
        """
        rsrc.task_id = self.grab_next(mes, clock)
        if rsrc.task_id is not None:
            new_task = mes.task_lookup(rsrc.task_id)
            new_task.resources_used.append(rsrc.rsrc_id)
            rsrc.put_to_work(new_task.filename)
            print(f"Time: {clock}\t{rsrc.task_id} started on {rsrc.rsrc_id}")

    def current(self) -> list[str]:
        """
        A getter to allow others to see what task the resources are currently working on.
        :return: A list of string task ids.
        """
        ret = []
        for rsrc in self.resources:
            ret.append(rsrc.task_id)
        return ret


class PrintManager(ResourceManager):
    """
    PrintManager is a child class of ResourceManager, set up to manage the 3d printers.
    """

    def __init__(self, no_units: int):
        super().__init__(no_units, "printer")

    def set_up_resources(self):
        """
        See base class documentation.
        :return: None
        """
        for i in range(self.no_units):
            printer = Printer(f"{self.rsrc_type}{i}")
            printer.state_node = f"ns={11 + i};s=P{i + 1}d_State"
            printer.file_node = f"ns={11 + i};s=P{i + 1}c_File"
            printer.start_node = f"ns={11 + i};s=P{i + 1}c_Start"
            printer.part_removed_node = f"ns={11 + i};s=P{i + 1}c_PartRemoved"
            asyncio.get_event_loop().run_until_complete(OPCUA.set_data(printer.state_node, printer.state))
            self.resources.append(printer)

    def tick(self, mes: MES, clock: int):
        """
        Implementation of the tick method for the PrintManager. Basic structure is as follows:
        For each printer:
        1. Ask the user (OPCUA mimic) to set the printers state.
        2. If the state is ready, run the default ready action.
        3. If the state is printing, print to console what is printing.
        4. If the state is finished printing, print to console that the task is waiting for robot pickup.
        5. If the state is bed empty, not ready, set state back to ready. (This will change to a cleaning
           cycle in the future
        :param mes: the manufacturing execution system
        :param clock: current time
        :return: None
        """
        for printer in self.resources:
            printer.get_state()  # This will change to a get state from the printer.
            if printer.state == "Operational":
                self.default_ready_action(printer, mes, clock)
            elif printer.state == "Printing":
                print(f"Time: {clock}\t{printer.task_id} being printed on {printer.rsrc_id}")
            elif printer.state == "Part on Bed":
                mes.task_lookup(printer.task_id).set_done(mes, clock)
                print(f"Time: {clock}\t{printer.task_id} waiting for robot pickup on {printer.rsrc_id}")


class RobotManager(ResourceManager):
    """
    RobotManager is a child class of ResourceManager, with the purpose of managing robots.
    """

    def __init__(self, no_units: int):
        super().__init__(no_units, "robot")

    def set_up_resources(self):
        """
        See base class documentation.
        :return: None
        """
        for i in range(self.no_units):
            robot = Robot(f"{self.rsrc_type}{i}")
            robot.ready_node = f"ns=21;s=R1f_Ready"
            robot.end_node = f"ns=21;s=R1f_End"
            robot.start_node = f"ns=21;s=R1c_Start"
            robot.prog_id_node = f"ns=21;s=R1c_ProgID"
            self.resources.append(robot)

    def tick(self, mes: MES, clock: int):
        """
        Implementation of the tick method for RobotManager. Basic Structure:
        For each robot:
        1. Get the robot's state from the user (mimicking the OPCUA)
        2. If the robot is ready, run the default ready action
        3. If the robot is busy, print to console what it is working on
        4. If the robot is done, print that the robot is done.
        :param mes: the manufacturing execution system
        :param clock: the current time
        :return: None
        """
        for robot in self.resources:
            robot.get_state()
            if robot.state == "Ready":
                self.default_ready_action(robot, mes, clock)  # This is going to be pushing a program ID
            elif robot.state == "Busy":
                print(f"Time: {clock}\t{robot.rsrc_id} working on {robot.task_id}")
            elif robot.state == "Done":
                mes.task_lookup(robot.task_id).set_done(mes, clock)
                print(f"Time: {clock}\t{robot.rsrc_id} is done {robot.task_id}")
                asyncio.get_event_loop().run_until_complete(OPCUA.set_data(robot.ready_node, True))

    def default_ready_action(self, rsrc: Resource, mes: MES, clock: int):
        rsrc.task_id = self.grab_next(mes, clock)
        if rsrc.task_id is not None:
            new_task = mes.task_lookup(rsrc.task_id)
            new_task.resources_used.append(rsrc.rsrc_id)
            rsrc.prog_id = new_task.robot_prog
            rsrc.put_to_work()
            print(f"Time: {clock}\t{rsrc.task_id} started on {rsrc.rsrc_id}")


class QIManager(ResourceManager):
    """
    This is the child class of ResourceManager to manage Quality Inspection stations
    """

    def __init__(self, no_units: int):
        super().__init__(no_units, "qi")

    def set_up_resources(self):
        """
        See base class.
        :return: None
        """
        for i in range(self.no_units):
            self.resources.append(InspectionStation(f"{self.rsrc_type}{i}"))

    def tick(self, mes: MES, clock: int):
        for station in self.resources:
            if station.state == "Ready":
                self.default_ready_action(station, mes, clock)
            elif station.state == "Busy":
                curr_task = mes.task_lookup(station.task_id)
                curr_exec = curr_task.exec_id
                print(f"Time: {clock}\t{station.rsrc_id} working on {station.task_id}")
                if self.check_db_result(mes.executables[curr_exec].db_id):
                    station.upon_task_completion()
                    mes.task_lookup(station.task_id).set_done(mes, clock)
                    print(f"Time: {clock}\t{station.rsrc_id} is done {station.task_id}")

    def check_db_result(self, part_db_id) -> bool:
        passed_qi = DBInterface.check_qi(part_db_id)
        if passed_qi is None:
            return False
        elif passed_qi:
            return True
        elif not passed_qi:
            raise NotImplementedError("haven't built fails yet!!")

    # def tick(self, mes: MES, clock: int):
    #     """
    #     Tick method for the QIManager. Basic Structure:
    #     1. Get the station's state from the user (mimicking OPCUA)
    #     2. If the station is ready, run the default ready action
    #     3. If the station is busy, print what it is working on
    #     4. If the station is done, print to console what is just finished/passed.
    #     To do in the future: Add in ability for the parts to fail QI.
    #     :param mes: the manufacturing execution system
    #     :param clock: the current time
    #     :return: None
    #     """
    #     for station in self.resources:
    #         station.get_state()
    #         if station.state == 0:
    #             self.default_ready_action(station, mes, clock)
    #         elif station.state == 1:
    #             print(f"Time: {clock}\t{station.rsrc_id} working on {station.task_id}")
    #         elif station.state == 2:
    #             mes.task_lookup(station.task_id).set_done(mes, clock)
    #             print(f"Time: {clock}\t{station.rsrc_id} declares QI pass for {station.task_id}")
