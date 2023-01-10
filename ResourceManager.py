from MES import MES
from Resource import *
from Tickable import Tickable


class ResourceManager(Tickable):
    def __init__(self, no_units: int, rsrc_type: str):
        self.resources: list[Resource] = []
        self.queue: list[str] = []
        self.rsrc_type: str = rsrc_type
        self.no_units = no_units
        self.set_up_resources()

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

    def default_ready_action(self, rsrc: Resource, mes: MES, clock: int):
        rsrc.task_id = self.grab_next(mes, clock)
        if rsrc.task_id is not None:
            rsrc.state = 1
            new_task = mes.task_lookup(rsrc.task_id)
            new_task.resources_used.append(rsrc.rsrc_id)
            print(f"Time: {clock}\t{rsrc.task_id} started on {rsrc.rsrc_id}")

    def current(self) -> list[str]:
        ret = []
        for rsrc in self.resources:
            ret.append(rsrc.task_id)
        return ret


class PrintManager(ResourceManager):
    def __init__(self, no_units: int):
        super().__init__(no_units, "printer")

    def set_up_resources(self):
        for i in range(self.no_units):
            self.resources.append(Printer(f"{self.rsrc_type}{i}"))

    def tick(self, mes: MES, clock: int):
        for printer in self.resources:
            printer.set_state()
            if printer.state == 0:
                self.default_ready_action(printer, mes, clock)
            elif printer.state == 1:
                print(f"Time: {clock}\t{printer.task_id} being printed on {printer.rsrc_id}")
            elif printer.state == 2:
                mes.task_lookup(printer.task_id).set_done(mes, clock)
                print(f"Time: {clock}\t{printer.task_id} waiting for robot pickup on {printer.rsrc_id}")
            elif printer.state == 3:
                printer.state = 0  # For now, bed empty is the same as ready.


class RobotManager(ResourceManager):
    def __init__(self, no_units: int):
        super().__init__(no_units, "robot")

    def set_up_resources(self):
        for i in range(self.no_units):
            self.resources.append(Robot(f"{self.rsrc_type}{i}"))

    def tick(self, mes: MES, clock: int):
        for robot in self.resources:
            robot.set_state()
            if robot.state == 0:
                self.default_ready_action(robot, mes, clock)
            elif robot.state == 1:
                print(f"Time: {clock}\t{robot.rsrc_id} working on {robot.task_id}")
            elif robot.state == 2:
                mes.task_lookup(robot.task_id).set_done(mes, clock)
                print(f"Time: {clock}\t{robot.rsrc_id} is done {robot.task_id}")

    def default_ready_action(self, rsrc: Resource, mes: MES, clock: int):
        rsrc.task_id = self.grab_next(mes, clock)
        if rsrc.task_id is not None:
            rsrc.state = 1
            new_task = mes.task_lookup(rsrc.task_id)
            new_task.resources_used.append(rsrc.rsrc_id)

            print(f"Time: {clock}\t{rsrc.task_id} started on {rsrc.rsrc_id}")


class QIManager(ResourceManager):
    def __init__(self, no_units: int):
        super().__init__(no_units, "qi")

    def set_up_resources(self):
        for i in range(self.no_units):
            self.resources.append(InspectionStation(f"{self.rsrc_type}{i}"))

    def tick(self, mes: MES, clock: int):
        for station in self.resources:
            station.set_state()
            if station.state == 0:
                self.default_ready_action(station, mes, clock)
            elif station.state == 1:
                print(f"Time: {clock}\t{station.rsrc_id} working on {station.task_id}")
            elif station.state == 2:
                mes.task_lookup(station.task_id).set_done(mes, clock)
                print(f"Time: {clock}\t{station.rsrc_id} declares QI pass for {station.task_id}")
