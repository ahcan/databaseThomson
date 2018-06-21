#-*- coding: utf-8
from setting.Databasethomson import Database
from setting import config as osDb
import os
import time
from setting.utils import *

def truncate_table(session, argsql):
    db = Database()
    flag = True
    count = 0
    while flag and count <= 3 :
        try:
            for ite in argsql:
                time.sleep(1)
                db.execute_nonquery(session, ite)
            session.commit()
            flag = False
            count +=1
            return 1
        except Exception as e:
            logerr = getLog('Error_Sync_Data')
            logerr.error('Truncate table %s'%(e))
            flag = True
            count += 1
        finally:
            logger = getLog('Sync_Data')
            logger.info('Final truncate table')
    return 0
def main():
    #time.sleep(1800)
    sqlTruncate =[ "truncate workflow;", "alter table workflow auto_increment = 1;", "truncate node;", "alter table node auto_increment = 1;", "truncate node_detail;", "alter table node_detail auto_increment = 1;", "truncate job_param;", "alter table job_param auto_increment = 1;", "truncate job;", "alter table job auto_increment = 1;"]
    db = Database()
    session = db.connect()
    truncate_table(session, sqlTruncate)
    db.close_connect(session)
    # strQuery = 'truncate job_param;alter table job_param auto_increment = 1;'
    # os.system(command_sql(strQuery))
    # print "truncate complie"
if __name__ == '__main__':
    main()
