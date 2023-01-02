from Executable import Part
from Resource import *
from MES import MES


class MESTest:
    def __init__(self):
        self.mes = MES()
        self.rsrc()
        self.execs(10)

    def rsrc(self):
        self.mes.resources["printer"] = Printer("printer")
        self.mes.resources["robot"] = Robot("robot")
        self.mes.resources["qi"] = InspectionStation("qi")

    def execs(self, num):
        for i in range(num):
            i_d = f"part{i}"
            self.mes.executables[i_d] = Part(i_d)

    def run(self, max_clock: int = 1000):
        for i in range(max_clock):
            self.mes.sys_tick(i)
        print(self.mes.report())
