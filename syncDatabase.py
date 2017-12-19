#-*- encoding: utf-8
from setting.Databasethomson import Database
from thomson_api import Job, JobDetail, Workflow
from setting.File import File
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
    sql= """create table workflow(wid varchar(50) CHARACTER SET utf8, name varchar(50) CHARACTER SET utf8, host nvarchar(20), pubver int unsigned, priver int unsigned);"""
    command = command_sql(sql)
    print "create table Workflow\n#####success#####"
    try:
        os.system(command)
    except Exception as e:
        print e
#################################
#---------insert table----------#
#################################

#insert job table
def insert_job(host=None):
    start = time.time()
    strQuery = "\ntruncate job; insert into job (jid, host, state, status, prog, ver, startdate, enddate) values"
    response_xml = Job(host).get_job_xml()
    sql = Job(host).parse_xml_2_query(response_xml)[:-1]
    sql = strQuery + sql + ";\n commit;"
    # command = command_sql(sql)
    # try:
    #     os.system(command)
    #     print "insert table job\n#####success#####"
    # except Exception as e:
    #     raise e
    # finally:
    #     strQuery =''
    File('sql/').write_log("job.sql", sql)
    main_Q.put(sql)
    main_Q.task_done()
    print ('End Job: ', time.time() - start)

#insert param table
def insert_param_thread(lstJid=None):
    start = time.time()
    lstJob = lstJid
    strQuery = "\ntruncate job_param; insert into job_param(jid, host, name, wid) values "
    for job in lstJob:
        param = JobDetail(job['jid'], job['host'])
        job = threading.Thread(target=thread_sql, kwargs={'jobDetail':param})
        job.daemon = True
        job.start()
    jobp_Q.join()
    print jobp_Q.qsize()
    print len(lstJob)
    while not jobp_Q.empty():
        strQuery += jobp_Q.get()
    sql = strQuery[:-1] + ";\ncommit;"
    File("sql/").write_log("param_job.sql", sql)
    main_Q.put(sql.encode('utf-8'))
    main_Q.task_done()
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
    sql = "\ntruncate workflow; insert into  workflow(wid, name, host, pubver, priver) values"
    response_xml = Workflow(host)
    sql += response_xml.parse_xml_2_query(response_xml.get_workflow())[:-1]+";\ncommit;"
    File("sql/").write_log("workflow.sql", sql)
    main_Q.put(sql)
    main_Q.task_done()
    print ('End Workflow: ', time.time() - start)

def command_sql(sql):
    return """mysql -u%s -p'%s' %s -h %s -e "%s" """%(osDb.DATABASE_USER, osDb.DATABASE_PASSWORD, osDb.DATABASE_NAME, osDb.DATABASE_HOST, sql)

def main():
    list_Jobs = []
    thread_job = threading.Thread(target=insert_job, kwargs={'host':osDb.THOMSON_HOST})
    list_Jobs.append(thread_job)
    thread_param = threading.Thread(target=insert_param_thread, kwargs={'lstJid':get_lstJob_id()})
    list_Jobs.append(thread_param)
    thread_workflow = threading.Thread(target=insert_workflow, kwargs={'host':osDb.THOMSON_HOST})
    list_Jobs.append(thread_workflow)
    for job in list_Jobs:
        job.daemon = True
        job.start()
        job.join()
    main_Q.join()
    strQuery = ''
    while not main_Q.empty():
        # print strQuery
        strQuery += main_Q.get()
    start = time.time()
    # print strQuery
    command = command_sql(strQuery)
    try:
        os.system(command)
        print "insert table #####success#####"
    except Exception as e:
        print e
    finally:
        strQuery = ''
    print ('End ', time.time() - start)

if __name__ == '__main__':
    main()