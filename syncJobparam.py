#-*- encoding: utf-8
from setting.Databasethomson import Database
from thomson_api import Job, JobDetail, Workflow, Node
from setting.File import File
from setting import config as osDb
import os
import threading
from Queue import Queue
import time

# strQuery = ""
jobp_Q = Queue()
main_Q = Queue()
def thread_sql(jobDetail=None):
    jobp_Q.put(jobDetail.parse_xml_2_query(jobDetail.get_param()))
    # time.sleep(10)
    jobp_Q.task_done()  

#################################
#---------insert table----------#
#################################
#insert param table
def insert_param_thread(host=None):
    # time.sleep(2)
    start = time.time()
    lstJob = get_lstJob_id(host)
    strQuery = "insert into job_param(jid, host, name, wid) values "
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
    sql = strQuery[:-1] + ";\ncommit;"
    File("sql/").write_log("param_job.sql", sql)
    main_Q.put(sql)
    main_Q.task_done()
    print ('End job_param: ', time.time() - start)
#array list jid
def get_lstJob_id(host):
    response_xml = Job(host).get_job_xml()
    return Job(host).count_job(response_xml)

def command_sql(sql):
    return """mysql -u%s -p'%s' %s -h %s -e "%s" """%(osDb.DATABASE_USER, osDb.DATABASE_PASSWORD, osDb.DATABASE_NAME, osDb.DATABASE_HOST, sql)

def main():
    list_Jobs = []
    for host in osDb.THOMSON_HOST:
        thread_param = threading.Thread(target=insert_param_thread, kwargs={'host':host})
        thread_param.start()
        thread_param.join()
    main_Q.join()
    strQuery = 'truncate job_param;alter table job_param auto_increment = 1;\n'
    while not main_Q.empty():
        # print strQuery
        tmp= main_Q.get()
        strQuery +=tmp
        # print tmp
    os.system(command_sql(strQuery))
    start = time.time()
    File("sql/").write_log("all-param.sql", strQuery)
    print ('End-inser-param', time.time() - start)

# def mai():

if __name__ == '__main__':
    main()