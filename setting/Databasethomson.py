import threading
import MySQLdb as mdb
from setting.config import *
from setting import config as osDb

class Database:
    def __init__(self):
        self.db = osDb.DATABASE_NAME
        self.user = osDb.DATABASE_USER
        self.password = osDb.DATABASE_PASSWORD
        self.host = osDb.DATABASE_HOST
        self.port = osDb.DATABASE_PORT

    def connect(self):
        return mdb.connect(host=self.host, port=self.port, user=self.user, passwd=self.password, db=self.db, charset='utf8')

    def close_connect(self, session):
        return session.close()

    def execute_nonquery(self, query):
        if not query:
            print 'No query!'
            return 0
        session = self.connect()
        cur=session.cursor()
        cur.execute(query)
        session.commit()
        self.close_connect(session)
        return 1

    def execute_query(self, query):
        session = self.connect()
        try:
            cur =  session.cursor()
            cur.execute(query)
            results = cur.fetchall()
            self.close_connect(session)
            return results
        except Exception as e:
            raise e
            
