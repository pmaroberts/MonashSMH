from DBInterface import DBInterface
from Executable import Job, Part
from ResourceManager import *


class MESInjector:
    @staticmethod
    def exec_injector() -> dict[str]:
        execs: dict = {}
        jobs = DBInterface.get_jobs()
        for job in jobs:
            parts = DBInterface.get_parts(job)
            parts_for_job = []
            for part in parts:
                new_part = Part(part[0], part[1])
                execs[new_part.exec_id] = new_part
                parts_for_job.append(new_part.exec_id)
            new_job = Job(job[0], parts_for_job)
            execs[new_job.exec_id] = new_job
        return execs

    @staticmethod
    def rsrc_injector() -> dict[str]:
        # noinspection PyDictCreation
        rsrcs: dict = {}
        rsrcs["printer"] = PrintManager(2)
        rsrcs["robot"] = RobotManager(1)
        rsrcs["qi"] = QIManager(1)
        return rsrcs
