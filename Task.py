from MES import MES
from Tickable import Tickable


class Task(Tickable):
    def __init__(self, exec_id, proc_time: int):
        self.resources: list[str] = []
        self.proc_time: int = proc_time
        self.time_til_done: int = self.proc_time
        self.released: bool = False
        self.exec_id = exec_id
        self.task_id = ""
        self.wait_time = -1

    def release(self, mes: MES):
        self.released = True
        for rsrc_id in self.resources:
            mes.resource_push(rsrc_id, self.task_id)

    def summary(self, clock: int) -> str:
        pass

    def tick(self, mes: MES, clock: int):
        dec_flag = True
        for rsrc_id in self.resources:
            if mes.resources[rsrc_id].current != self.task_id:
                dec_flag = False
                break
        if self.time_til_done != 0:
            if dec_flag:
                self.time_til_done -= 1
            elif self.released:
                self.wait_time += 1

    def set_id(self, action: str):
        self.task_id = f"{self.exec_id}_{action}"


class Print(Task):
    def __init__(self, exec_id, proc_time: int = 10):
        super().__init__(exec_id, proc_time)
        self.resources = ["printer"]
        self.set_id("print")

    def summary(self, clock: int) -> str:  # Potentially to delete
        return f"Time: {clock}\t{self.exec_id} print task printing."


class QI(Task):
    def __init__(self, exec_id, proc_time: int = 5):
        super().__init__(exec_id, proc_time)
        self.set_id("qi")
        self.resources = ["qi", "robot"]


class Store(Task):
    def __init__(self, exec_id, proc_time: int = 3):
        super().__init__(exec_id, proc_time)
        self.set_id("store")
        self.resources = ["robot"]


class Assemble(Task):
    def __init__(self, exec_id, proc_time: int):
        super().__init__(exec_id, proc_time)
        self.set_id("assemble")
