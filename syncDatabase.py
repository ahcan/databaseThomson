#-*- encoding: utf-8
from setting.Databasethomson import Database
from setting.File import File, getLog
from setting import config as osDb
import os
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
    # create logger
    #logger = getLog('Get query insert Job %s'%(host['host']))
    logger = getLog('Sync_Data')
    logger.setLevel(logging.INFO)
    start = time.time()
    # strQuery = "insert into job (jid, host, state, status, prog, ver, startdate, enddate) values"
    try:
        dataJob, dataPara = get_job(host)
        logger.info('Get query insert Job %s completed %s'%(host['host'], time.time() - start))
        db = Database()
        db.many_insert(session, 'job', dataJob, 'jid', 'host', 'state', 'status', 'prog', 'ver', 'startdate', 'enddate')
        db.many_insert(session, 'job_param', dataPara, 'jib', 'host', 'jname', 'wid')
        return 1
    except Exception as e:
        logerr = getLog('Error_Sync_Data')
        logerr.error('Get Log %s'%(e))
        return 0
    finally:
        return 0

#insert workflow table
def insert_workflow(session = None, host=None):
    logger = getLog('Sync_Data')
    logger.setLevel(logging.INFO)
    #logger.info('Get query insert Workflow %s'%(host['host']))
    start = time.time()
    try:
        data = get_workflow(host)
        logger.info('Get query insert Workflow %s Completed in %s.' %(host['host'], time.time() - start))
        db = Database()
        db.many_insert(session, 'workflow',data, 'wid', 'name', 'host')
        return 1
    except Exception as e:
        logerr = getLog('Error_Sync_Data')
        logerr.error('Get workflow error %s.'%(e))
        raise
    finally:
        return 0
 
#insert node table
def insert_node(session, host=None):
    #create logger
    #logger = getLog('Get query insert Node %s'%(host['host']))
    logger = getLog('Sync_Data')
    logger.setLevel(logging.INFO)
    start = time.time()
    #strQueryDetail = "insert into node_detail(nid, host, jid) values"
    try:
        data_node = get_node(host)
        logger.info(' Get query insert Node %s Completed in %s.' %(host['host'] ,time.time() - start))
        db = Database()
        db.many_insert(session, 'node', data_node, 'nid', 'host', 'cpu', 'alloccpu', 'mem', 'allocmem', 'status', 'state', 'uncreachable')
        data_nodedetail = get_node_detail(host)
        print data_nodedetail
        db.many_insert(session, 'node_detail', data_nodedetail, 'nid','host','jid')
        return 1
    except Exception as e:
        logerr = getLog('Error_Sync_Data')
        logerr.error('Get Node %s' %(e))
        raise
    finally:
        return 0

def command_sql(sql):
    return """mysql --default-character-set=utf8 -u%s -p'%s' %s -h %s -e "%s" """%(osDb.DATABASE_USER, osDb.DATABASE_PASSWORD, osDb.DATABASE_NAME, osDb.DATABASE_HOST,sql)

def main():
    list_Jobs = []
    db =  Database()
    session = db.connect()
    sqlTruncate =["truncate job;", "truncate workflow;", "truncate node;", "truncate node_detail;", "alter table job auto_increment = 1;", "alter table workflow auto_increment = 1;", "alter table node auto_increment = 1;", " alter table node_detail auto_increment = 1;"]
    try:
        for ite in sqlTruncate:
            db.execute_nonquery(session, ite)
        session.commit()
    except Exception as e:
        logerr = getLog('Error_Sync_Data')
        logerr.error('Truncate table %s'%(e))
    finally:
        logger = getLog('Sync_Data')
        logger.info('Final truncate table')
    for host in osDb.THOMSON_HOST:
        thread_job = threading.Thread(target=insert_job, kwargs={'session': session, 'host':host})
        list_Jobs.append(thread_job)
        #thread_workflow = threading.Thread(target=insert_workflow, kwargs={'session':session, 'host':host})
        #list_Jobs.append(thread_workflow)
        #thread_node = threading.Thread(target=insert_node, kwargs={'session':session, 'host':host})
        #list_Jobs.append(thread_node)
    for job in list_Jobs:
        job.daemon = True
        job.start()
        job.join()
    # main_Q.join()
    time.sleep(10)
    #strQuery = "truncate job; truncate workflow; truncate node; truncate node_detail; alter table job auto_increment = 1;\
     #alter table workflow auto_increment = 1; alter table node auto_increment = 1; alter table node_detail auto_increment = 1;"
    # os.system(command_sql(strQuery.encode('utf-8')))
    # while not main_Q.empty():
    #     tmp= main_Q.get()
    #     if tmp.find('job') != -1: 
    #         logger = getLog('Sync_Data')
    #         logger.info('Insert Job')
    #     elif tmp.find('node') != -1:
    #         logger = getLog('Sync_Data')
    #         logger.info('Insert Node')
    #     elif tmp.find('workflow') != -1:
    #         logger = getLog('Sync_Data')
    #         logger.info('Inster Workflow')
    #     #logger = getLog('Insert Job')
    #     logger.setLevel(logging.INFO)
    #     start = time.time()
    #     # execute query
    #     try:
    #        os.system(command_sql(tmp.encode('utf-8')))
    #        logger.info('completed in %s' %( time.time() - start))
    #     except Exception as e:
    #        logerr = getLog('Error_Sync_Data')
    #        logerr.error('insert job-node-workflow %s' %e)


if __name__ == '__main__':
    main()
