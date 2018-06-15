import threading
import MySQLdb as mdb
from setting.config import *
from setting import config as osDb
import logging, logging.config
from File import getLog
import time

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
            self.close_connect(session)
            raise e
            
    def many_insert(self, table, data, *args):
        """
        table: name table
        data: array tuple
        *args: chua cac filed
        """
        col = ','
        val = ','
        for item in args:
            col +='%s,'%(item)
            val +='/%/s,'
        val = val[1:-1]
        col = col[1:-1]
        sql = "insert into %s(%s)values(%s)"%(table, col, val, data)
        session = self.connect()
        cur = session.cursor()
        start = time.time()
        logger = getLog('Sync_Data')
        try:
            cur.executemany(sql, data)
            results = cur.fetchall()
            self.close_connect(session)
            logger.info('Insert workflow complited in %s.'%(time.time()-start))
            return results
        except Exception as e:
            logerr = getLog('Error_Sync_Data')
            self.close_connect(session)
            logerr.error('Insert workflow error: %s.'%(e))
            return 0

    def many_update(self, table, data, *args):
        """
        table: name table
        data: array tuple
        *args: chua cac fiel
        """
        return 0

    def is_existed(self, key, table, **kwargs):
        """
        return true/false
        **kwargs: chua dieu kien where
        """
        tmp = 'and'
        for key, value in kwargs.iteritems():
            tmp += ' {0} = \'{1}\' and'.format(key, value)
        tmp = tmp[3:-3]
        sql = "select %s from %s where %s;"%(key, table, tmp)
        session = self.connect()
        try:
            cur = session.cursor()
            cur.execute(sql)
            results = cur.fetchall()
            self.close_connect(session)
            return results
        except Exception as e:
            self.close_connect(session)
            return 0