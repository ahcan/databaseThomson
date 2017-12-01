import threading
import MySQLdb as mdb
from setting.config import *

class Database:
    def __init__(self):
        self.db = DATABASE_NAME
        self.user = DATABASE_USER
        self.password = DATABASE_PASSWORD
        self.host = DATABASE_HOST
        self.port = DATABASE_PORT

    def connect(self):
        return mdb.connect(host=self.host, port=self.port, user=self.user, passwd=self.password, db=self.db)

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
            
