from MES import MES
from Tickable import Tickable


class Resource(Tickable):
    def __init__(self, rsrc_id: str):
        self.current: str = ""
        self.busy: bool = False
        self.queue: list[str] = []
        self.rsrc_id = rsrc_id

    def tick(self, mes: MES, clock: int):
        if not self.busy:
            self.current = self.grab_next(mes, clock)
            if self.current is not None:
                self.busy = True
                print(f"Time: {clock}\t{self.rsrc_id} starting {self.current}")
        elif mes.task_lookup(self.current).time_til_done == 0:
            self.busy = False
            print(f"Time: {clock}\t{self.current} is done.")
        else:
            print(self.summary(clock))

    # Definitely can override this method in the subclasses to better optimise
    def grab_next(self, mes: MES, clock: int) -> str:  # May need the mes and the clock in the future for optimisation
        if not len(self.queue) == 0:
            return self.queue.pop(0)

    def summary(self, clock: int) -> str:
        return f"Time: {clock}\t{self.rsrc_id} working on {self.current}"


class Printer(Resource):
    def __init__(self, rsrc_id: str):
        super().__init__(rsrc_id)

    # def summary(self, clock: int) -> str:
    #     return f"Time: {clock}\t {self.rsrc_id} printing {self.current}"


class Robot(Resource):
    def __init__(self, rsrc_id: str):
        super().__init__(rsrc_id)


class InspectionStation(Resource):
    def __init__(self, rsrc_id: str):
        super().__init__(rsrc_id)
