import time

from ResourceManager import *
from MES import MES
import random
import asyncio


class MESTest:
    """
    This is a driver class for the MES system, allowing for testing and development.
    """

    def __init__(self):
        self.mes = MES()
        self.rsrc()
        self.execs()
        # self.execs(num_parts=10,
        #            print_time_min=3,
        #            print_time_max=12)

    def rsrc(self):
        self.mes.resource_managers["printer"] = PrintManager(1)
        self.mes.resource_managers["robot"] = RobotManager(1)
        self.mes.resource_managers["qi"] = QIManager(1)

    def execs(self):
        self.mes.executables = DBInterface.exec_injector().copy()

    def run(self, max_clock: int = 1000):
        for i in range(max_clock):
            self.mes.sys_tick(i)
            time.sleep(3)
        # print(self.mes.report())
