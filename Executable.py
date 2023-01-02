from MES import MES
from Task import *
from Tickable import Tickable


class Executable(Tickable):
    def __init__(self, i_d: str):
        self.tasks: list[Task] = []
        self.up_to: int = 0
        self.done_stamp: int = 0
        self.i_d = i_d

    def tick(self, mes: MES, clock: int):
        if self.up_to == len(self.tasks):
            if self.done_stamp == 0:
                self.done_stamp = clock - 1
            return
        if not self.tasks[self.up_to].released:
            self.tasks[self.up_to].release(mes)
        elif self.tasks[self.up_to].time_til_done == 1:  # Could be an off by one error, we'll see
            self.up_to += 1

    def task_lookup(self, task_id: str) -> Task:
        for task in self.tasks:
            if task.task_id == task_id:
                return task


class Part(Executable):
    def __init__(self, i_d: str, print_time: int = 1):
        super().__init__(i_d)
        self.tasks = [Print(self.i_d, print_time), QI(self.i_d), Store(self.i_d)]
