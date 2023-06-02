from Task import *
from Tickable import Tickable


class Executable(Tickable):
    """
    This class is to represent executables (jobs and parts at the moment, extendable in the future)

    Attributes:
        tasks (list): a list of tasks that make up the executable
        up_to (int): representation of where the task is up to in the tasks list
        done_stamp (int): a time stamp for when the task completes
        exec_id (str): the tasks id
    """

    def __init__(self, exec_id: str, db_id: int):
        """
        Constructor for the Executable class
        :param exec_id: the tasks' id
        """
        self.tasks: list[Task] = []
        self.up_to: int = 0
        self.done = False
        self.exec_id = exec_id
        self.db_id = db_id

    def tick(self, mes: MES, clock: int):
        """
        Tick method implementation for executables
        :param mes: manufacturing execution system
        :param clock: Current Time
        :return: None
        """
        # If all tasks are complete, record the done timestamp and return (do not continue with the tick)
        # Note: Tick still runs on execs that are complete (potential improvement)
        if self.up_to == len(self.tasks):
            self.done = True
            self.mark_done_in_db()
            return
        # If the current task is not released, release it.
        if not self.tasks[self.up_to].released:
            self.tasks[self.up_to].release(mes, self.up_to)
        # If the current task is done, increment  up to
        elif self.tasks[self.up_to].is_done():
            self.up_to += 1

    def task_lookup(self, task_id: str) -> Task:
        """
        Method for finding a task within an executable
        :param task_id: task id for the sought after task
        :return: the task
        """
        for task in self.tasks:
            if task.task_id == task_id:
                return task

    def mark_done_in_db(self):
        pass


class Part(Executable):
    """
    This class is used to represent parts in the system.
    """

    def __init__(self, part_id: int, part_no: int):
        """
        Constructor for the Part class. The tasks associated with parts are pre-filled in the task list:
        Print, Quality Inspect and Store
        :param part_id: id for the part (will come from the database)
        :param print_time: approximation of the print time for the part. Default is 10 for testing, but this value will
        be overridden by database values (approximations from the STL file)
        """
        super().__init__(f"part{part_id}", part_id)
        self.part_no = part_no
        self.tasks = [Print(self.exec_id), Store(self.exec_id, "printer"), QI(self.exec_id),
                      Store(self.exec_id, "qi")]
        # self.tasks = [QI(self.exec_id)]

    def mark_done_in_db(self):
        DBInterface.mark_part_done(self.db_id)


class Job(Executable):
    """
    Class for jobs (groups of parts to be assembled). Assemble and Store tasks are already pre-filled.
    Attributes:
        parts (list[str]): List of part ids the job needs to be printed to assemble
    """

    def __init__(self, exec_id: int, parts=None):
        """
        Constructor for the Job class
        :param exec_id: The id for the job (different to the id for the parts in it)
        :param parts: List of part ids that belong to the job
        """
        super().__init__(f"job{exec_id}", exec_id)
        if parts is None:
            parts = []
        self.parts = parts
        self.tasks = [Assemble(self.exec_id, self.parts), Finish(self.exec_id)]

    def mark_done_in_db(self):
        pass
