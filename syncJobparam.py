#-*- encoding: utf-8
from setting.Databasethomson import Database
from setting.File import File, getLog
from setting import config as osDb
import os
import threading
import time
import logging, logging.config #ghi log
from setting.utils import *
from Redit import Redit #cache redis
import json

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
    def insert_job_param(self):
        start = time.time()
        try:
            self.logger.info('Get job param %s' %(self.cfghost['host']))
            dataJobParam = get_job_param(self.cfghost)
            self.logger.info('%s completed in %s and len %s' %(self.cfghost['host'] ,time.time() - start, len(dataJobParam)))
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

    # Cache data to redis
    def set_cache(self, redis_key):
        self.cache = Redit(key = redis_key)
        try:
            result = self.get_job_host()
            if not result:
                time.sleep(1)
                result = self.get_job_host()
            self.logger.info("Get job list OK -{0}".format(len(result)))
        except Exception as e:
            self.logerr.error("Get job list Error {0}".format(e))
        try:
            tmp = self.json_job_host(result)
        except Exception as e:
            self.logerr.error("Convert Json Error {0}".format(e))
        try:
            self.cache.set_data(name= osDb.REDIS_NAME[0], val = tmp)
            self.logger.info("Set data cache OK")
        except Exception as e:
            self.logerr.error("Set data cache Error {0}".format(e))

    def get_job_host(self):
        host = self.cfghost['host']
        sql =" SELECT j.jid, pw.name, pw.wname, j.state, j.status, j.startdate, j.enddate, pw.wid, j_a.auto, pw.backup\
               FROM (SELECT  w.name as wname, p.name, w.wid, p.jid, p.host, p.backup FROM job_param p, (Select wid, name, host from workflow where host = '{0}') w WHERE p.host = '{1}' and w.wid= p.wid) pw, job j LEFT JOIN job_auto j_a ON j.jid = j_a.jid AND j.host = j_a.host WHERE pw.jid = j.jid;".format(host,host)
        #print host
        return self.db.execute_query(sql)

    def json_job_host(self, lstjob):
        args = []
        for item in lstjob:
            JId,jobname,workflow_name,State,Status,StartDate,EndDate,workflowIdRef,backMain,isBackup = item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9]
            args.append({'jname'    : jobname,
                        'wid'       : workflowIdRef,
                        'wname'     : workflow_name,
                        'state'     : State,
                        'status'    : Status,
                        'jid'       : JId,
                        # 'prog'      : int(Prog),
                        'startdate' : StartDate \
                        if StartDate else None,
                        # 'ver'       : int(Ver),
                        'enddate'   : EndDate \
                        if EndDate else None,
                        'iauto'     : backMain,
                        'iBackup'  : isBackup
                })
        return json.dumps(args)

def start_insert(host = None, index= 0):
    obj =  syncJobparam(host)
    obj.insert_job_param()
    obj.set_cache(osDb.REDIS_KEY[index])

def main():
    for host in osDb.THOMSON_HOST:
        thread_param = threading.Thread(target=start_insert, kwargs={'host':host, 'index':osDb.THOMSON_HOST.index(host)})
        #thread_param.daemon = True
        thread_param.start()
        #thread_param.join()

if __name__ == '__main__':
    main()
    time.sleep(2)
