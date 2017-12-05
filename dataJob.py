from Databasethomson import Database
from thomson_api import Job, JobDetail, Workflow
from File import File
from setting import config as osDb
import os
import threading
from Queue import Queue
import time


threadLimiter = threading.BoundedSemaphore(10)
class threadparam(threading.Thread):
    """docstring for threadparam"""
    def __init__(self, job):
        super(threadparam, self).__init__()
        self.queue = Queue()
        # self.daemon  = daem
        self.job = job

    def run(self):
        threadLimiter.acquire()
        try:
            self.work()
        finally:
            threadLimiter.release()
        
    def work(self):
        time.sleep(0.1)
        self.queue.put(self.job.parse_xml_2_query(self.job.get_param()))
        self.queue.task_done()

strQuery = ""
mainQ = Queue()

def thread_sql(jobDetail=None):
    time.sleep(1)
    global strQuery
    strQuery += jobDetail.parse_xml_2_query(jobDetail.get_param())
    mainQ.task_done()    

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
def insert_job(host=None):
    start = time.time()
    global strQuery
    strQuery += "truncate job; insert into job (jid, host, state, status, prog, ver, startdate, enddate) values"
    response_xml = Job().get_job_xml()
    sql = Job().parse_xml_2_query(response_xml, host)[:-1]
    sql = strQuery + sql + ";\n commit"
    command = command_sql(sql)
    try:
        os.system(command)
        print "insert table job\n#####success#####"
    except Exception as e:
        raise e
    finally:
        strQuery =''
    File('sql/').write_log("job.sql", sql)
    print ('End Job: ', time.time() - start)

#insert param table
def insert_param_thread(lstJid=None):
    start = time.time()
    lstJob = lstJid
    global strQuery
    strQuery += "truncate job_param; insert into job_param(jid, host, name, wid) values "
    for job in lstJob:
        mainQ.put(job)
        param = JobDetail(job['jid'], job['host'])
        job = threading.Thread(target=thread_sql, kwargs={'jobDetail':param})
        job.daemon = True
        job.start()
    mainQ.join()
    sql = strQuery[:-1] + ";\ncommit"
    command = command_sql(sql)
    try:
        os.system(command)
        print "insert table job_param\n#####success#####"
    except Exception as e:
        print e
    finally:
        strQuery = ''
    File("sql/").write_log("param_job.sql", sql)
    print ('End job_param: ', time.time() - start)

def insert_param(lstJid):
    sql = """truncate job_param;"""
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
def get_lstJob_id():
    db = Database()
    sql = """select jid, host from job;"""
    lstJob = db.execute_query(sql)
    args = []
    for job in lstJob:
        args.append({'jid'      :job[0], 'host'     :job[1]})
    return args

#insert workflow table
def insert_workflow(host=None):
    start = time.time()
    sql = "truncate workflow; insert into  workflow(wid, name, host, pubver, priver) values"
    response_xml = Workflow(host)
    sql += response_xml.parse_xml_2_query(response_xml.get_workflow())[:-1]+";\ncommit"
    # print sql
    command = command_sql(sql)
    try:
        os.system(command)
        print "insert table workflow\n#####success#####"
    except Exception as e:
        print e
    File("sql/").write_log("workflow.sql", sql)
    print ('End workflow: ', time.time() - start)

def command_sql(sql):
    return """mysql -u%s -p'%s' %s -h %s -e "%s" """%(osDb.DATABASE_USER, osDb.DATABASE_PASSWORD, osDb.DATABASE_NAME, osDb.DATABASE_HOST, sql)

#create_tbJob()
#create_tbParam()
#create_tbWorkflow()
# insert_job(osDb.THOMSON_HOST)
# insert_param_thread(get_lstJob_id())
# insert_workflow(osDb.THOMSON_HOST)
#insert_param(get_lstJob_id())
def main():
    # threads = []
    # thread_job = threading.Thread(target='insert_job', kwargs={'host':osDb.THOMSON_HOST})
    # thread_job.start()
    # # thread_param = threading.Thread(target='insert_param_thread', kwargs={get_lstJob_id()})
    # # thread_param.start()
    # # thread_workflow = threading.Thread(target='insert_workflow', kwargs={osDb.THOMSON_HOST})
    # # thread_workflow.start()
    # # threads.append(thread_workflow)
    # threads.append(thread_job)
    # # threads.append( thread_param)
    # for t in threads:
    #     t.join()
    insert_job(osDb.THOMSON_HOST)
    time.sleep(0.02)
    insert_param_thread(get_lstJob_id())
    insert_workflow(osDb.THOMSON_HOST)
if __name__ == '__main__':
    while True:
        main()
        time.sleep(1.5)