#-*- encoding: utf-8
from setting.Databasethomson import Database
from setting.File import File, getLog
from setting import config as osDb
import os
import sys
import threading
from Queue import Queue
import time
import logging, logging.config
from setting.utils import *
from thomson_api import Job, JobDetail, Workflow, Node

threadLimiter = threading.BoundedSemaphore(10)

# strQuery = ""
jobp_Q = Queue()
main_Q = Queue()
def thread_sql(jobDetail=None):
    jobp_Q.put(jobDetail.parse_xml_2_query(jobDetail.get_param()))
    # time.sleep(10)
    jobp_Q.task_done()  

#################################
#---------create table----------#
#################################
def create_tbJob():
    sql = "create table job(jid int unsigned, host nvarchar(20), state char(10), status char(10), prog int unsigned, ver int unsigned, startdate int unsigned, enddate int unsigned);"
    command = command_sql(sql)
    try:
        os.system(command)
        print "create table Job\n#####success#####"
    except Exception as e:
        raise e

def create_tbParam():
    sql = "create table job_param(jid int unsigned, host nvarchar(20), name nvarchar(50), wid nvarchar(50), backup nvarchar(5));"
    command = command_sql(sql)
    try:
        os.system(command)
        print "create table Param Job\n#####success#####"
    except Exception as e:
        print e

def create_tbWorkflow():
    sql= """create table workflow(wid varchar(50) CHARACTER SET utf8, name varchar(50) CHARACTER SET utf8, host nvarchar(20), pubver int unsigned, priver int unsigned);"""
    command = command_sql(sql)
    print "create table Workflow\n#####success#####"
    try:
        os.system(command)
    except Exception as e:
        print e

def create_tbNode():
    sql = "create table node(nid int unsigned, host nvarchar(20), cpu int unsigned, alloccpu int unsigned, mem int unsigned, allocmem int unsigned, status char(10), state char(10), uncreachable char(5));"
    command = command_sql(sql)
    print "create table Node\n#####success#####"
    try:
        os.system(command)
    except Exception as e:
        raise e

def create_tbNodeDetail():
    sql = "create table node_detail(nid int unsigned, host nvarchar(20), jid int unsigned);"
    command = command_sql(sql)
    print "create table Node Detail\n#####success#####"
    try:
        os.system(command)
    except Exception as e:
        raise e

#################################
#---------insert table----------#
#################################
#insert job table

def insert_job(session=None, host=None):
    logger = getLog('Sync_Data')
    logger.setLevel(logging.INFO)
    db =  Database()
    session = db.connect()
    start = time.time()
    try:
        dataJob, dataPara = get_job(host)
        logger.info('Get query insert Job %s completed %s'%(host['host'], time.time() - start))
        truncate_table(session, ["delete from job where host = '{0}';".format(host['host'])])
        truncate_table(session, ["delete from job_param where host = '{0}';".format(host['host'])])
        db = Database()
        db.many_insert(session, 'job', dataJob, 'jid', 'host', 'state', 'status', 'prog', 'ver', 'startdate', 'enddate')
        db.many_insert(session, 'job_param', dataPara, 'jid', 'host', 'name', 'wid', 'backup')
    except Exception as e:
        logerr = getLog('Error_Sync_Data')
        logerr.error('Get Log {0}'.format(e))
    finally:
        db.close_connect(session)
        print(session)
        return 0

#insert workflow table
def insert_workflow(session = None, host=None):
    logger = getLog('Sync_Data')
    logger.setLevel(logging.INFO)
    db =  Database()
    session = db.connect()
    start = time.time()
    try:
        data = get_workflow(host)
        logger.info('Get query insert Workflow %s Completed in %s.' %(host['host'], time.time() - start))
        truncate_table(session, ["delete from workflow where host = '{0}';".format(host['host'])])
        db = Database()
        db.many_insert(session, 'workflow',data, 'wid', 'host', 'name')
    except Exception as e:
        logerr = getLog('Error_Sync_Data')
        logerr.error('Get workflow error %s.'%(e))
        raise
    finally:
        db.close_connect(session)
        print(session)
        return 0
 
#insert node table
def insert_node(session = None, host=None):
    db =  Database()
    session = db.connect()
    logger = getLog('Sync_Data')
    logger.setLevel(logging.INFO)
    start = time.time()
    try:
        data_node = get_node(host)
        logger.info(' Get query insert Node %s Completed in %s.' %(host['host'] ,time.time() - start))
        truncate_table(session,["delete from node where host = '{0}';".format(host['host'])])
        db.many_insert(session, 'node', data_node, 'nid', 'host', 'cpu', 'alloccpu', 'mem', 'allocmem', 'status', 'state', 'uncreachable')
        data_nodedetail = get_node_detail(host)
        truncate_table(session,["delete from node_detail where host = '{0}';".format(host['host'])])
        db.many_insert(session, 'node_detail', data_nodedetail, 'nid','host','jid')
    except Exception as e:
        logerr = getLog('Error_Sync_Data')
        logerr.error('Get Node %s' %(e))
        raise
    finally:
        db.close_connect(session)
        print(session)
        return 0

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
    list_Jobs = []
    sqlTruncate =[ "truncate workflow;", "truncate node;", "truncate node_detail;","alter table workflow auto_increment = 1;", "alter table node auto_increment = 1;", " alter table node_detail auto_increment = 1;"]
    for host in osDb.THOMSON_HOST:
    #host = osDb.THOMSON_HOST[sys.argv[1]]
        thread_job = threading.Thread(target=insert_job, kwargs={'host':host})
        thread_job.start()
        list_Jobs.append(thread_job)
        thread_workflow = threading.Thread(target=insert_workflow, kwargs={'host':host})
        thread_workflow.start()
        list_Jobs.append(thread_workflow)
        thread_node = threading.Thread(target=insert_node, kwargs={'host':host})
        thread_node.start() 
        list_Jobs.append(thread_node)
    #for job in list_Jobs:
        #job.daemon = False
        #job.start()
    #    job.join()
    # main_Q.join()
    time.sleep(5)

if __name__ == '__main__':
    main()
