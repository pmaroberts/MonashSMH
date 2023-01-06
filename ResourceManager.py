from MES import MES
from Tickable import Tickable


class ResourceManager(Tickable):
    """
    Parent class to represent the manufacturing resources (or a group of resources) in the system (the machines).
    Attributes:
        current (list[str]): list of task_ids corresponding to the task each unit of the machine group is working on.
            e.g. ["part0_print", "part1_print", "part2_print"] would be the current list for a 3 printer system with
            part0 on printer0, part1 on printer1 and part2 on printer2
        busy: (list[bool]): list to represent whether units are busy or not.
    """

    def __init__(self, no_units: int):
        self.current: list[str] = ["" for _ in range(no_units)]  # Replace this with actual Unit classes
        self.busy = [False for _ in range(no_units)]  # This no longer needs to exist, just poll the Unit classes
        self.queue: list[str] = []
        self.rsrc_type: str = ""
        self.no_units = no_units

    def tick(self, mes: MES, clock: int):
        for i in range(self.no_units):
            if not self.busy[i]:
                self.current[i] = self.grab_next(mes, clock)
                if self.current[i] is not None:
                    self.busy[i] = True
                    print(f"Time: {clock}\t{self.rsrc_type}{i} starting {self.current[i]}")
            elif mes.task_lookup(self.current[i]).done():
                if mes.check_pickup(self.current[i]):  # Making sure part has been picked up before setting to not busy
                    print(f"Time: {clock}\t{self.current[i]} is done on {self.rsrc_type}{i}.")
                    self.busy[i] = False
                else:
                    print(f"Time: {clock}\t{self.current[i]} is waiting for pickup on {self.rsrc_type}{i}.")
            else:
                print(self.summary(clock, i))

    # Definitely can override this method in the subclasses to better optimise
    def grab_next(self, mes: MES, clock: int) -> str:  # May need the mes and the clock in the future for optimisation
        if not len(self.queue) == 0:
            return self.queue.pop(0)

    def summary(self, clock: int, unit: int) -> str:
        return f"Time: {clock}\t{self.rsrc_type}{unit} working on {self.current[unit]}"


class Printer(ResourceManager):
    def __init__(self, no_units: int):
        self.rsrc_type = "printer"
        super().__init__(no_units)

    # def tick(self, mes: MES, clock: int):
    #     super().tick(mes, clock)
    #     for i in range(self.no_units):
    #         if self.current[i] not in mes.resources["robot"].current and not self.busy[i]:
    #             print(f"Time: {clock}\t{self.rsrc_type}{i} waiting for robot to pick up {self.current[i]}")
    #             self.busy[i] = True


class Robot(ResourceManager):
    def __init__(self, no_units: int):
        self.robot = "robot"
        super().__init__(no_units)


class InspectionStation(ResourceManager):
    def __init__(self, no_units: int):
        self.rsrc_type = "qi"
        super().__init__(no_units)


