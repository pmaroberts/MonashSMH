from MES import MES
from Tickable import Tickable


class Task(Tickable):
    def __init__(self, exec_id, proc_time: int):
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
        self.released = True
        self.position = position
        self.task_id += str(self.position)
        for rsrc_id in self.resources_needed:
            mes.resource_push(rsrc_id, self.task_id)

    def summary(self, clock: int) -> str:
        pass

    def tick(self, mes: MES, clock: int):
        dec_flag = True
        for rsrc_id in self.resources_needed:
            if self.task_id not in mes.resource_managers[rsrc_id].current():
                dec_flag = False
                break
        if dec_flag:
            self.time_til_done -= 1
            if not self.started():
                self.start_stamp = clock
                self.start_action(mes, clock)
        elif self.released:
            self.wait_time += 1

    def set_id(self, action: str):
        self.task_id = f"{self.exec_id}_{action}"

    def get_wait_time(self):
        return type(self).__name__, self.wait_time

    def started(self) -> bool:
        return self.start_stamp is not None

    def start_action(self, mes: MES, clock: int):
        pass

    def is_done(self) -> bool:
        return self.done

    def set_done(self, mes: MES, clock: int):
        self.done = True
        # Release your resource_managers lol
        self.release_resources(mes, clock)
        mes.executables[self.exec_id].tick(mes, clock)

    def release_resources(self, mes: MES, clock: int):
        for rsrc_id in self.resources_used:
            mes.resource_release(rsrc_id)


class Print(Task):
    def __init__(self, exec_id, proc_time):
        super().__init__(exec_id, proc_time)
        self.resources_needed = ["printer"]
        self.set_id("print")


class QI(Task):
    def __init__(self, exec_id, proc_time: int = 5):
        super().__init__(exec_id, proc_time)
        self.set_id("qi")
        self.resources_needed = ["qi", "robot"]


class Store(Task):
    def __init__(self, exec_id, prev_loc: str, proc_time: int = 3):
        super().__init__(exec_id, proc_time)
        self.set_id("store")
        self.resources_needed = ["robot"]
        self.prev_loc = prev_loc

    def start_action(self, mes: MES, clock: int):
        # Releasing the resources that the last task is holding
        last_task_used_rsrc = mes.executables[self.exec_id].tasks[self.position - 1].resources_used
        for rsrc in mes.resource_managers[self.prev_loc].resources:
            if rsrc.rsrc_id in last_task_used_rsrc:
                rsrc.part_pickup_handler()


class Assemble(Task):
    def __init__(self, exec_id, part_list: list, proc_time: int = 13):
        super().__init__(exec_id, 2 * len(part_list))
        self.set_id("assemble")
        self.resources_needed = ["robot"]
        self.part_list = part_list

    def release(self, mes: MES, position: int):
        for part_id in self.part_list:
            part = mes.executables[part_id]
            if part.done_stamp == 0:
                return
        super().release(mes, position)


class Finish(Task):
    def __init__(self, exec_id, proc_time: int = 3):
        super().__init__(exec_id, proc_time)
        self.set_id("finish")
        self.resources_needed = ["robot"]
