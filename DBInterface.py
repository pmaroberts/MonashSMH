"""
File: DBInterface.py
Author: Peter Roberts
"""

from database import Database, CursorFromConnectionPool


class DBInterface:
    """
    This class acts as an interface for the MES to use the database. All calls MES calls from the database use this class
    to avoid many classes depending on the database, psycopg2, database credentials etc.
    """

    # This line initialises the database. The DB credentials can be replaced.
    Database.initialise(database="MES_testing", user="postgres", password="1234", host='localhost')

    @staticmethod
    def get_jobs() -> list[tuple]:
        """
        Method used to get jobs from the database.
        :return: A list of jobids, in the form [(1,), (2,)]
        """
        with CursorFromConnectionPool() as cursor:
            cursor.execute('SELECT jobid FROM jobs')
            jobs = cursor.fetchall()
        return jobs

    @staticmethod
    def get_parts(job):
        """
        Method used to get parts from the database
        :param job:
        :return:
        """
        with CursorFromConnectionPool() as cursor:
            cursor.execute('SELECT partid, part_no FROM part WHERE jobid = %s', job)
            parts = cursor.fetchall()
        return parts

    @staticmethod
    def mark_part_done(part_db_id):
        with CursorFromConnectionPool() as cursor:
            cursor.execute(f"UPDATE part SET part_done_stamp = Now() WHERE partid = {part_db_id}")
            print('attempted to stamp done in db')

    @staticmethod
    def check_qi(part_db_id) -> bool:
        with CursorFromConnectionPool() as cursor:
            cursor.execute('SELECT confirm_result FROM inspection WHERE partid = %s', (part_db_id,))
            return cursor.fetchone()[0]

    @staticmethod
    def filename_getter(part_db_id):
        with CursorFromConnectionPool() as cursor:
            cursor.execute(f"SELECT gcode_file FROM part WHERE partid = {part_db_id}")
            return cursor.fetchone()[0]
