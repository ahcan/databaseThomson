from Databasethomson import Database
from thomson_api import Job, JobDetail, Workflow
from File import File
import config as osDb
import os
import threading
from Queue import Queue
import time


class threadparam(threading.Thread):
    """docstring for threadparam"""
    def __init__(self, queue, job):
        super(threadparam, self).__init__()
        self.queue = queue
        # self.daemon  = daem
        self.job = job

    def run(self):
        # time.sleep()
        self.queue.put(self.job.parse_xml_2_query(self.job.get_param()))
        self.queue.task_done()

#################################
#---------create table----------#
#################################
def create_tbJob():
    sql = "create table job(jid int, host nvarchar(20), state char(10), status char(10), prog int unsigned, ver int unsigned, startdate int unsigned, enddate int unsigned);"
    command = command_sql(sql)
    try:
        os.system(command)
        print "create table Job\n#####success#####"
    except Exception as e:
        raise e

def create_tbParam():
    sql = "create table job_param(jid int unsigned, host nvarchar(20), name nvarchar(50), wid nvarchar(50));"
    command = command_sql(sql)
    try:
        os.system(command)
        print "create table Param Job\n#####success#####"
    except Exception as e:
        print e

def create_tbWorkflow():
    sql= """create table workflow(wid nvarchar(50), name nvarchar(50), host nvarchar(20), pubver int unsigned, priver int unsigned);"""
    command = command_sql(sql)
    print "create table Workflow\n#####success#####"
    try:
        os.system(command)
    except Exception as e:
        print e
#################################
#---------inaert table----------#
#################################

#insert job table
def insert_job(host):
    response_xml = Job().get_job_xml()
    sql = Job().parse_xml_2_query(response_xml, host)
    print sql
    command = command_sql(sql)
    try:
        os.system(command)
        print "success"
    except Exception as e:
        raise e

#insert param table
def insert_param_thread(lstJid):
    threads = []
    sql = """truncate job_param;"""
    lstJob = lstJid    
    for job in lstJob:
        param = JobDetail(job['jid'], job['host'])
        q = Queue()
        threads.append(threadparam(q, param))
        threads[lstJob.index(job)].setDaemon(True)
        threads[lstJob.index(job)].start()
    for t in threads:
        sql +=  t.queue.get()
    command = command_sql(sql)
    try:
        os.system(command)
        print "###success###"
    except Exception as e:
        print e

def insert_param(lstJid):
    sql = """truncate job_param;"""
    lstJob = get_lstJob_id()    
    for job in lstJob:
        param = JobDetail(job['jid'], job['host'])
        sql += param.parse_xml_2_query(param.get_param())
    command = command_sql(sql)
    try:
        os.system(command)
        print "###success###"
    except Exception as e:
        raise e

#array list jid
def get_lstJob_id():
    db = Database()
    sql = """select jid, host from job;"""
    lstJob = db.execute_query(sql)
    args = []
    for job in lstJob:
        args.append({'jid'      :job[0], 'host'     :job[1]})
    return args

#insert workflow table
def insert_workflow(host):
    sql = "truncate workflow;"
    response_xml = Workflow(host)
    sql = response_xml.parse_xml_2_query(response_xml.get_workflow())
    # print sql
    command = command_sql(sql)
    try:
        os.system(command)
        print "insert table workflow\n#####success#####"
    except Exception as e:
        print e

def command_sql(sql):
    return """mysql -u%s -p%s %s -h %s -e "%s" """%(osDb.DATABASE_USER, osDb.DATABASE_PASSWORD, osDb.DATABASE_NAME, osDb.DATABASE_HOST, sql)

# insert_job("localhost")
insert_param_thread(get_lstJob_id())
# create_tbParam()
# create_tbWorkflow()
# insert_workflow("localhost")