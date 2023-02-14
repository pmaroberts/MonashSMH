from database import CursorFromConnectionPool
from database import Database
import urllib
import psycopg2
import datetime


def main():
    connection = psycopg2.connect(database='DTLSQLV2', user='postgres', password='4321', host='172.31.1.163')
    cursor = connection.cursor()
    Database.initialise(database="DTLSQLV2", user="postgres", password="4321", host='172.31.1.163')


if __name__ == '__main__':
    main()
    print("hi")
