from database import Database, CursorFromConnectionPool
from Executable import Part, Job


class DBInterface:
    Database.initialise(database="MES_testing", user="postgres", password="1234", host='localhost')

    @staticmethod
    def exec_injector() -> dict[str]:
        execs: dict = {}
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
                execs[new_part.exec_id] = new_part
                parts_for_job.append(new_part.exec_id)
            new_job = Job(job[0], parts_for_job)
            execs[new_job.exec_id] = new_job
        return execs

    @staticmethod
    def mark_part_done(part_db_id):
        with CursorFromConnectionPool() as cursor:
            cursor.execute(f"UPDATE part SET part_done_stamp = Now() WHERE partid = {part_db_id}")

    @staticmethod
    def check_qi(part_db_id) -> bool:
        with CursorFromConnectionPool() as cursor:
            cursor.execute('SELECT confirm_result FROM inspection WHERE partid = %s', (part_db_id,))
            return cursor.fetchone()[0]


