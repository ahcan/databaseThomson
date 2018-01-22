#-*- encoding: utf-8
from setting.Databasethomson import Database
from thomson_api import Job, JobDetail, Workflow, Node
from setting.File import File
from setting import config as osDb
import os
import threading
from Queue import Queue
import time

class syncJobparam():
    """docstring for syncJobparam"""
    def __init__(self, cfghost=None):
        self.cfghost = cfghost
        self.jobp_Q = Queue()
    #insert param to database
    def insert_param(self):
    # time.sleep(2)
        start = time.time()
        lstJob = self.get_lstJob_id(self.cfghost)
        strQuery ="""delete from job_param where host = '%s'; insert into job_param(jid, host, name, wid, backup) values """%(self.cfghost['host'])
        for job in lstJob:
            param = JobDetail(job['jid'], job['host'])
            job = threading.Thread(target=self.thread_sql, kwargs={'jobDetail':param})
            job.daemon = True
            job.start()
            job.join()
        self.jobp_Q.join()
        print len(lstJob)
        print self.jobp_Q.qsize()
        while not self.jobp_Q.empty():
            strQuery += self.jobp_Q.get()
        sql = strQuery[:-1] + ";commit;"
        File("sql/").write_log("param_job.sql", sql)
        os.system(self.command_sql(sql.encode('utf-8')))
        print ('End insert job_param: ', time.time() - start)

    
    #connect to mysqld
    def command_sql(self, sql):
        return """mysql -u%s -p'%s' %s -h %s -e "%s" """%(osDb.DATABASE_USER, osDb.DATABASE_PASSWORD, osDb.DATABASE_NAME, osDb.DATABASE_HOST, sql)
    
    #get list jobid by host
    def get_lstJob_id(self, host):
        response_xml = Job(host).get_job_xml()
        return Job(host).count_job(response_xml)
    
    #thread add query
    def thread_sql(self,jobDetail=None):
        self.jobp_Q.put(jobDetail.parse_xml_2_query(jobDetail.get_param()))
        # time.sleep(10)
        self.jobp_Q.task_done() 

    def truncate_table(self):
        #time.sleep(1800)
        time.sleep(10)
        strQuery = 'truncate job_param;alter table job_param auto_increment = 1;'
        os.system(command_sql(strQuery))
        print "truncate complie"


def start_insert(host = None):
    obj =  syncJobparam(host)
    obj.insert_param()

def main():
    for host in osDb.THOMSON_HOST:
        thread_param = threading.Thread(target=start_insert, kwargs={'host':host})
        #thread_param.daemon = True
        thread_param.start()

if __name__ == '__main__':
    main()
