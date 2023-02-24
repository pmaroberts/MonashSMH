import time
from MESInjector import MESInjector
from mucking_around_gui import MESGUI
from MES import MES
import os


class MESTest:
    """
    This is a driver class for the MES system, allowing for testing and development.
    """

    def __init__(self):
        self.mes = MES()
        self.rsrc()
        self.execs()

    def rsrc(self):
        self.mes.resource_managers = MESInjector.rsrc_injector()

    def execs(self):
        self.mes.executables = MESInjector.exec_injector().copy()

    def run(self, max_clock: int = 1000):
        # Clear the console at the start
        os.system('cls')
        for i in range(max_clock):
            print(f"Time is now: {i}")
            self.mes.sys_tick(i)
            time.sleep(3)
            os.system('cls')

    def run_gui(self):
        gui = MESGUI(self.mes)
        gui.run()
