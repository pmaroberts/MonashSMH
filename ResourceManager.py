from MES import MES
from Resource import Resource
from Tickable import Tickable


class ResourceManager(Tickable):
    def __init__(self, no_units: int, rsrc_type: str):
        self.resources: list[Resource] = []
        self.queue: list[str] = []
        self.rsrc_type: str = rsrc_type
        self.no_units = no_units

    def set_up_resources(self):
        for i in range(self.no_units):
            self.resources.append(Resource(f"{self.rsrc_type}{i}"))

    def tick(self, mes: MES, clock: int):  # You can write one of these for each of the subclasses, they're different
        pass

    # Definitely can override this method in the subclasses to better optimise
    def grab_next(self, mes: MES, clock: int) -> str:  # May need the mes and the clock in the future for optimisation
        if not len(self.queue) == 0:
            return self.queue.pop(0)

    def summary(self, clock: int, unit: int) -> str:
        pass




class Printer(ResourceManager):
    def __init__(self, no_units: int):
        super().__init__(no_units, "printer")

    def tick(self, mes: MES, clock: int):
        for printer in self.resources:
            if printer.ready:
                printer.task_id = self.grab_next(mes, clock)
                mes.task_lookup(printer.task_id).resources_used.append(printer.rsrc_id)
                print(f"Time: {clock}\t{printer.task_id} started printing on {printer.rsrc_id}")
            elif printer.end:
                print(f"Time: {clock}\t{printer.task_id} waiting for robot pickup on {printer.rsrc_id}")
            else:
                print(f"Time: {clock}\t{printer.task_id} being printed on {printer.rsrc_id}")


class Robot(ResourceManager):
    def __init__(self, no_units: int):
        super().__init__(no_units, "robot")


class InspectionStation(ResourceManager):
    def __init__(self, no_units: int):
        super().__init__(no_units, "qi")
