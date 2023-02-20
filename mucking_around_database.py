from database import *
import urllib
import psycopg2
import datetime
from Executable import *


def test_adding_all():
    execs_mock: dict = {}
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
            execs_mock[new_part.exec_id] = new_part
            parts_for_job.append(new_part)
        new_job = Job(job[0], parts_for_job)
        execs_mock[new_job.exec_id] = new_job

    print(execs_mock.items())


def test_qi():
    with CursorFromConnectionPool() as cursor:
        cursor.execute('SELECT confirm_result FROM inspection WHERE partid = %s', (14,))
        print(cursor.fetchone()[0])


def main():
    Database.initialise(database="MES_testing", user="postgres", password="1234", host='localhost')
    test_qi()


if __name__ == '__main__':
    main()
    print("hi")
