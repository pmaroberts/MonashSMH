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
        self.start_stamp = None

    def release(self, mes: MES):
        self.released = True
        for rsrc_id in self.resources:
            mes.resource_push(rsrc_id, self.task_id)

    def summary(self, clock: int) -> str:
        pass

    def tick(self, mes: MES, clock: int):
        dec_flag = True
        for rsrc_id in self.resources:
            if self.task_id not in mes.resources[rsrc_id].current:
                dec_flag = False
                break
        if self.time_til_done != 0:
            if dec_flag:
                self.time_til_done -= 1
                if self.start_stamp is None:
                    self.start_stamp = clock
            elif self.released:
                self.wait_time += 1

    def set_id(self, action: str):
        self.task_id = f"{self.exec_id}_{action}"

    def get_wait_time(self):
        return type(self).__name__, self.wait_time

    def started(self) -> bool:
        return self.start_stamp is not None

    def done(self) -> bool:
        return self.time_til_done == 0


class Print(Task):
    def __init__(self, exec_id, proc_time):
        super().__init__(exec_id, proc_time)
        self.resources = ["printer"]
        self.set_id("print")

    # def summary(self, clock: int) -> str:  # Potentially to delete
    #     return f"Time: {clock}\t{self.exec_id} print task printing."


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
    def __init__(self, exec_id, part_list: list, proc_time: int = 13):
        super().__init__(exec_id, 2 * len(part_list))
        self.set_id("assemble")
        self.resources = ["robot"]
        self.part_list = part_list

    def release(self, mes: MES):
        for part_id in self.part_list:
            part = mes.executables[part_id]
            if part.done_stamp == 0:
                return
        super().release(mes)
