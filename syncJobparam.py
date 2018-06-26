#-*- encoding: utf-8
from setting.Databasethomson import Database
from setting.File import File, getLog
from setting import config as osDb
import os
import threading
import time
import logging, logging.config #ghi log
from setting.utils import *

class syncJobparam():
    """docstring for syncJobparam"""
    def __init__(self, cfghost=None):
        self.cfghost = cfghost
        #self.jobp_Q = Queue()
        #self.logger = getLog('Sync job param %s' %(cfghost['host']))
        self.logger = getLog('Job_Param')
        self.logger.setLevel(logging.INFO)
        self.logerr = getLog('Error_Job_Param')
        self.db = Database(log = 'Job_Param', logerror = 'Error_Job_Param')
        self.session = self.db.connect()
    #insert param to database
    def insert_param(self):
    # time.sleep(2)
        try:
            lstJob = self.get_lstJob_id(self.cfghost)
        except Exception as e:
            self.logerr.error('Get list Job: %s' %(e))
        strQuery ="""delete from job_param where host = '%s'; insert into job_param(jid, host, name, wid, backup) values """%(self.cfghost['host'])
        for job in lstJob:
            param = JobDetail(job['jid'], job['host'])
            job = threading.Thread(target=self.thread_sql, kwargs={'jobDetail':param})
            job.daemon = True
            job.start()
            job.join()
        self.jobp_Q.join()
        self.logger.info('Job: %s Job inserted: %s' %(len(lstJob), self.jobp_Q.qsize()))
        while not self.jobp_Q.empty():
            strQuery += self.jobp_Q.get()
        sql = strQuery[:-1] + ";commit;"
        File("sql/").write_log("param_job.sql", sql)
        try:
            os.system(self.command_sql(sql.encode('utf-8')))
            self.logger.info('Completed in %s' %(time.time() - start))
        except Exception as e:
            self.logerr.error("Insert Job list %s"%(e))
            return 1
        return 0
    def insert_job_param(self):
        start = time.time()
        try:
            self.logger.info('Get job param %s' %(self.cfghost['host']))
            dataJobParam = get_job_param(self.cfghost)
            self.logger.info('Completed in %s' %(time.time() - start))
            self.truncate_table(["delete from job_param where host = '{0}';".format(self.cfghost['host'])])
            self.db.many_insert(self.session, 'job_param', dataJobParam, 'jid', 'host', 'name', 'wid', 'backup')
        except Exception as e:
            self.logerr.error('Get job param error {0}'.format(e))
            raise
        finally:
            self.db.close_connect(self.session)
    #connect to mysqld
    def command_sql(self, sql):
        return """mysql -u%s -p'%s' %s -h %s -e "%s" """%(osDb.DATABASE_USER, osDb.DATABASE_PASSWORD, osDb.DATABASE_NAME, osDb.DATABASE_HOST, sql)
    
    #get list jobid by host
    def get_lstJob_id(self, host):
        try:
            response_xml = Job(host).get_job_xml()
            return Job(host).count_job(response_xml)
        except Exception as e:
            self.logerr.error(e)
            return 1
    
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

    def truncate_table(self, argsql):
        db = Database()
        flag = True
        count = 0
        while flag and count <= 3 :
            try:
                for ite in argsql:
                    time.sleep(1)
                    db.execute_nonquery(self.session, ite)
                self.session.commit()
                flag = False
                count +=1
                return 1
            except Exception as e:
                self.logerr.error('Truncate table %s'%(e))
                flag = True
                count += 1
            finally:
                self.logger.info('Final truncate table')
        return 0
def start_insert(host = None):
    obj =  syncJobparam(host)
    obj.insert_job_param()

def main():
    for host in osDb.THOMSON_HOST:
        thread_param = threading.Thread(target=start_insert, kwargs={'host':host})
        #thread_param.daemon = True
        thread_param.start()
        #thread_param.join()

if __name__ == '__main__':
    main()
    time.sleep(20)
