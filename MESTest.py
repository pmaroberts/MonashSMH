import time
from database import CursorFromConnectionPool, Database
from Executable import Part, Job
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
        Database.initialise(database="MES_testing", user="postgres", password="1234", host='localhost')
        self.execs()
        # self.execs(num_parts=10,
        #            print_time_min=3,
        #            print_time_max=12)

    def rsrc(self):
        self.mes.resource_managers["printer"] = PrintManager(1)
        self.mes.resource_managers["robot"] = RobotManager(1)
        self.mes.resource_managers["qi"] = QIManager(1)

    def execs(self):
        with CursorFromConnectionPool() as cursor:
            cursor.execute('SELECT jobid FROM jobs')
            jobs = cursor.fetchall()
            print(jobs)
        for job in jobs:
            with CursorFromConnectionPool() as cursor:
                cursor.execute('SELECT partid, part_no FROM part WHERE jobid = %s', job)
                parts = cursor.fetchall()
            parts_for_job = []
            for part in parts:
                new_part = Part(part[0], part[1])
                self.mes.executables[new_part.exec_id] = new_part
                parts_for_job.append(new_part.exec_id)
            new_job = Job(job[0], parts_for_job)
            self.mes.executables[new_job.exec_id] = new_job

    # def get_parts_from_db(self):
    #     with CursorFromConnectionPool() as cursor:
    #         cursor.execute('SELECT * FROM part')
    #         parts = cursor.fetchall()
    #     for part in parts:
    #         new_part = Part(part[0])
    #         self.mes.executables[new_part.exec_id] = new_part

    def run(self, max_clock: int = 1000):
        for i in range(max_clock):
            self.mes.sys_tick(i)
            time.sleep(1)
        # print(self.mes.report())
