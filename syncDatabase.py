#-*- encoding: utf-8
from setting.Databasethomson import Database
from thomson_api import Job, JobDetail, Workflow, Node
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

def create_tbNode():
    sql = "create table node(nid int unsigned, host nvarchar(20), cpu int unsigned, alloccpu int unsigned, mem int unsigned, allocmem int unsigned, status char(10), state char(10), unreachable char(4))"
    command = command_sql(sql)
    print "create table Node\n#####success#####"
    try:
        os.system(command)
    except Exception as e:
        raise e

#################################
#---------insert table----------#
#################################

#insert job table
def insert_job(host=None):
    start = time.time()
    strQuery = "\ndelete from job where host = '%s'; insert into job (jid, host, state, status, prog, ver, startdate, enddate) values"%(host['host'])
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
def insert_param_thread(lstJid=None, host=None):
    start = time.time()
    lstJob = lstJid
    strQuery = "\ndelete from job_param where host = '%s'; insert into job_param(jid, host, name, wid) values "%(host['host'])
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
    sql = "\ndelete from workflow where host = '%s'; insert into  workflow(wid, name, host, pubver, priver) values"%(host['host'])
    response_xml = Workflow(host)
    sql += response_xml.parse_xml_2_query(response_xml.get_workflow())[:-1]+";\ncommit;"
    File("sql/").write_log("workflow.sql", sql)
    main_Q.put(sql)
    main_Q.task_done()
    print ('End Workflow: ', time.time() - start)

#insert node table
def insert_node(host=None):
    start = time.time()
    strQuery = "\ndelete from node where host = '%s'; insert into node(nid, host, cpu, alloccpu, mem, allocmem, status, state, unreachable) values"%(host['host'])
    # response_xml = Node(host).get_job_xml()
    sql = Node(host).get_node()[:-1]
    sql = strQuery + sql + ";\ncommit;"
    # command = command_sql(sql)
    # try:
    #     os.system(command)
    #     print "insert table job\n#####success#####"
    # except Exception as e:
    #     raise e
    # finally:
    #     strQuery =''
    File('sql/').write_log("node.sql", sql)
    main_Q.put(sql)
    main_Q.task_done()
    print ('End Node: ', time.time() - start)

def command_sql(sql):
    return """mysql -u%s -p'%s' %s -h %s -e "%s" """%(osDb.DATABASE_USER, osDb.DATABASE_PASSWORD, osDb.DATABASE_NAME, osDb.DATABASE_HOST, sql)

def main():
    list_Jobs = []
    for host in osDb.THOMSON_HOST:
        thread_job = threading.Thread(target=insert_job, kwargs={'host':host})
        list_Jobs.append(thread_job)
        thread_workflow = threading.Thread(target=insert_workflow, kwargs={'host':host})
        list_Jobs.append(thread_workflow)
        thread_node = threading.Thread(target=insert_node, kwargs={'host':host})
        list_Jobs.append(thread_node)
        thread_param = threading.Thread(target=insert_param_thread, kwargs={'lstJid':get_lstJob_id(),'host':host})
        list_Jobs.append(thread_param)
    for job in list_Jobs:
        job.daemon = True
        job.start()
        job.join()
    main_Q.join()
    strQuery = ''
    while not main_Q.empty():
        # print strQuery
        tmp= main_Q.get()
        os.system(command_sql(tmp))
        strQuery +=tmp
    start = time.time()
    File("sql/").write_log("all.sql", strQuery)
    # command = command_sql(strQuery)
    # try:
    #     os.system(command)
    #     print "insert table #####success#####"
    # except Exception as e:
    #     print e
    # finally:
    #     strQuery = ''
    print ('End ', time.time() - start)

# def mai():

if __name__ == '__main__':
    main()