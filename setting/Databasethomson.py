import threading
import MySQLdb as mdb
from setting.config import *
from setting import config as osDb
import logging, logging.config
from File import getLog
import time
import json

class Database:
    def __init__(self, log = 'Sync_Data', logerror = 'Error_Sync_Data'):
        self.db = osDb.DATABASE_NAME
        self.user = osDb.DATABASE_USER
        self.password = osDb.DATABASE_PASSWORD
        self.host = osDb.DATABASE_HOST
        self.port = osDb.DATABASE_PORT
        self.logger = getLog(log)
        self.logerr = getLog(logerror)

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

    def execute_nonquery(self, session, query):
        if not query:
            print 'No query!'
            return 0
        #session = self.connect()
        cur=session.cursor()
        cur.execute(query)
        #session.commit()
        #self.close_connect(session)
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
            val +='%s,'
        val = val[1:-1]
        col = col[1:-1]
        sql = "insert into {0} ({1}) values({2})".format(table, col, val)
        session = self.connect()
        cur = session.cursor()
        start = time.time()
        logger = getLog('Sync_Data')
        try:
            for item in data:
                cur.execute(sql, item)
                #host = item[2]
                cur.execute('commit;')
            #cur.execute('select * from workflow where host = \'{0}\''.format(host))
            #results = cur.fetchall()
            session.commit()
            self.close_connect(session)
            logger.info('Insert workflow complited in %s.'%(time.time()-start))
        except Exception as e:
            logerr = getLog('Error_Sync_Data')
            self.close_connect(session)
            logerr.error('Insert workflow error: %s.'%(e))
            return 0
        finally:
            return 0

    def many_insert(self, session, table, data, *args):
        """
        session: session connect database
        table: name table
        data: array tuple
        *args: chua cac filed
        """
        col = ','
        val = ','
        flag = True
        count = 0
        for item in args:
            col +='%s,'%(item)
            val +='%s,'
        val = val[1:-1]
        col = col[1:-1]
        sql = "insert into {0} ({1}) values({2})".format(table, col, val)
        #session = self.connect()
        cur = session.cursor()
        start = time.time()
        while flag and count <= 3:
             ccommit = 0
             try:
                 host = ''
                 tmpsql = ','
                 for item in data:
                     tmpsql += '{0},'.format(json.dumps(item).replace('[','(').replace(']',')'))
                     host = item[1]
                 tmpsql = tmpsql[1:-1]
                 sql = "insert into {0} ({1}) values{2};".format(table, col, tmpsql)
		 cur.execute(sql)
                 #cur.execute('select * from workflow where host = \'{0}\''.format(host))
                 #results = cur.fetchall()
                 #print "{0}-{1}".format(host, len(results))
                 session.commit()
                 #self.close_connect(session)
                 self.logger.info('Insert {0} - {1} complited in {2}.'.format(table, host, time.time()-start))
                 flag = False
                 count +=1
                 return 1
             except Exception as e:
                 #self.close_connect(session)
                 self.logger.error('Insert {0} error'.format(table))
                 self.logerr.error('Insert {0} error: {1}.'.format(table, e))
                 flag = True
                 count +=1
                 raise
             print "+++++++++++raise++++++++++"
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
        except:
            self.close_connect(session)
            return 0
