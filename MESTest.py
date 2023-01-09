from Executable import Part, Job
from ResourceManager import *
from MES import MES
import random


class MESTest:
    def __init__(self):
        self.mes = MES()
        self.rsrc()
        self.execs(num_parts=10,
                   print_time_min=4,
                   print_time_max=4)

    def rsrc(self):
        self.mes.resources["printer"] = PrintManager(1)
        self.mes.resources["robot"] = RobotManager(1)
        self.mes.resources["qi"] = QIManager(1)

    def execs(self, num_parts, print_time_min, print_time_max):
        random.seed(90210)
        for i in range(num_parts):
            i_d = f"part{i}"
            self.mes.executables[i_d] = Part(i_d, print_time=random.randint(print_time_min, print_time_max))

        self.mes.executables["job1"] = Job("job1", [f"part{i}" for i in range(1)])
        self.mes.executables["job2"] = Job("job2", [f"part{i}" for i in range(3, 4)])
        self.mes.executables["job3"] = Job("job3", [f"part{i}" for i in range(4, 10)])

    def run(self, max_clock: int = 1000):
        for i in range(max_clock):
            self.mes.sys_tick(i)
        # print(self.mes.report())
