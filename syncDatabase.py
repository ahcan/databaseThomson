#-*- encoding: utf-8
from setting.Databasethomson import Database
from thomson_api import Job, JobDetail, Workflow, Node
from setting.File import File, getLog
from setting import config as osDb
import os
import threading
from Queue import Queue
import time
import logging, logging.config

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
def insert_job(host=None):
    # create logger
    logger = getLog('Get query insert Job %s'%(host['host']))
    logger.setLevel(logging.INFO)
    start = time.time()
    strQuery = "insert into job (jid, host, state, status, prog, ver, startdate, enddate) values"
    response_xml = Job(host).get_job_xml()
    sql = Job(host).parse_xml_2_query(response_xml)[:-1]
    if len(sql):
       sql = strQuery + sql + ";commit;"
       main_Q.put(sql)
       main_Q.task_done()
    else:
       main_Q.put(sql)
       main_Q.task_done()
    File('sql/').write_log("job.sql", sql)
    logger.info('Completed %s.' %(time.time() - start))

#insert param table
def insert_param_thread(host=None):
    # time.sleep(2)
    start = time.time()
    lstJob = get_lstJob_id(host)
    strQuery = "delete from job_param where host = '%s';ALTER TABLE job AUTO_INCREMENT = 1; insert into job_param(jid, host, name, wid) values "%(host['host'])
    for job in lstJob:
        param = JobDetail(job['jid'], job['host'])
        job = threading.Thread(target=thread_sql, kwargs={'jobDetail':param})
        job.daemon = True
        job.start()
        job.join()
    jobp_Q.join()
    print jobp_Q.qsize()
    print len(lstJob)
    while not jobp_Q.empty():
        strQuery += jobp_Q.get()
    sql = strQuery[:-1] + ";commit;"
    File("sql/").write_log("param_job.sql", sql)
    main_Q.put(sql)
    main_Q.task_done()
    print ('End job_param: ', time.time() - start)

def insert_param(lstJid):
    # sql = """delete from job_param where host = '%s';"""%()
    lstJob = get_lstJob_id()    
    for job in lstJob:
        param = JobDetail(job['jid'], job['host'])
        sql += param.parse_xml_2_query(param.get_param())
    print sql
    command = command_sql(sql)
    try:
        os.system(command)
        print "###success###"
    except Exception as e:
        raise e
    File("sql/").write_log("param_log.sql", sql)

#array list jid
def get_lstJob_id(host):
    # db = Database()
    # sql = """select jid, host from job;"""
    # lstJob = db.execute_query(sql)
    # args = []
    # while not lstJob:
    #     lstJob = db.execute_query(sql)
    #     print lstJob
    # for job in lstJob:
    #     args.append({'jid'      :job[0], 'host'     :job[1]})
    # return args
    response_xml = Job(host).get_job_xml()
    return Job(host).count_job(response_xml)


#insert workflow table
def insert_workflow(host=None):
    #create logger
    logger = getLog('Get query insert Workflow %s'%(host['host']))
    logger.setLevel(logging.INFO)
    start = time.time()
    sql = "insert into  workflow(wid, name, host, pubver, priver) values"
    response_xml = Workflow(host)
    sql += response_xml.parse_xml_2_query(response_xml.get_workflow())[:-1]+";commit;"
    sql = sql
    File("sql/").write_log("workflow.sql", sql)
    main_Q.put(sql)
    main_Q.task_done()
    logger.info('Completed in %s.' %(time.time() - start))

#insert node table
def insert_node(host=None):
    #create logger
    logger = getLog('Get query insert Node %s'%(host['host']))
    logger.setLevel(logging.INFO)
    start = time.time()
    strQueryNode = "insert into node(nid, host, cpu, alloccpu, mem, allocmem, status, state, uncreachable) values"
    strQueryDetail = "insert into node_detail(nid, host, jid) values"
    # response_xml = Node(host).get_job_xml()
    try:
        sql, sqlDetail = Node(host).get_node()    
    except Exception as e:
        logger.error('Get Node %s' %(e))
    sql = strQueryNode + sql[:-1] + ";commit;"
    sqlDetail = strQueryDetail + sqlDetail[:-1]+";commit;"
    # command = command_sql(sql)
    # try:
    #     os.system(command)
    #     print "insert table job\n#####success#####"
    # except Exception as e:
    #     raise e
    # finally:
    #     strQuery =''
    sql = sql
    sqlDetail = sqlDetail.decode('utf-8')
    #print sqlDetail
    File('sql/').write_log("node.sql", sql)
    File('sql/').write_log("node_detail.sql", sqlDetail)
    main_Q.put(sql)
    main_Q.task_done()
    main_Q.put(sqlDetail)
    main_Q.task_done()
    logger.info('Completed in %s.' %(time.time() - start))

def command_sql(sql):
    return """mysql --default-character-set=utf8 -u%s -p'%s' %s -h %s -e "%s" """%(osDb.DATABASE_USER, osDb.DATABASE_PASSWORD, osDb.DATABASE_NAME, osDb.DATABASE_HOST,sql)

def main():
    
    list_Jobs = []
    for host in osDb.THOMSON_HOST:
        thread_job = threading.Thread(target=insert_job, kwargs={'host':host})
        list_Jobs.append(thread_job)
        thread_workflow = threading.Thread(target=insert_workflow, kwargs={'host':host})
        list_Jobs.append(thread_workflow)
        thread_node = threading.Thread(target=insert_node, kwargs={'host':host})
        list_Jobs.append(thread_node)
    for job in list_Jobs:
        job.daemon = True
        job.start()
        job.join()
    main_Q.join()
    strQuery = "truncate job; truncate workflow; truncate node; truncate node_detail; alter table job auto_increment = 1;\
     alter table workflow auto_increment = 1; alter table node auto_increment = 1; alter table node_detail auto_increment = 1;"
    os.system(command_sql(strQuery.encode('utf-8')))
    while not main_Q.empty():
        tmp= main_Q.get()
        if tmp.find('job') != -1: 
            logger = getLog('Insert Job')
        elif tmp.find('node') != -1:
            logger = getLog('Insert Node')
        elif tmp.find('workflow') != -1:
            logger = getLog('Inster Workflow')
        #logger = getLog('Insert Job')
        logger.setLevel(logging.INFO)
        #strQuery +=tmp
        # print tmp
        #os.system(command_sql(tmp))
        #print tmp
        start = time.time()
        try:
           os.system(command_sql(tmp.encode('utf-8')))
           logger.info('completed in %s' %( time.time() - start))
           #print('insert finished')
        except exception as e:
           logger.error('insert job-node-workflow %s' %e)

    
    # File("sql/").write_log("all.sql", strQuery)
    # command = command_sql(strQuery)
    # try:
    #     os.system(command)
    #     print "insert table #####success#####"
    # except Exception as e:
    #     print e
    # finally:
    #     strQuery = ''


if __name__ == '__main__':
    main()
