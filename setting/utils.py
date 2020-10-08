from thomsonapi import Workflow, Log, Node, NodeDetail, Job, JobDetail
import config
import json
import logging, logging.config
from File import getLog
from setting.Databasethomson import Database

def get_workflow(host):
    """
    host: thomson name
    """
    Worf = Workflow(host = host['host'], user = host['user'], passwd = host['passwd'])
    args =[]
    logerr = getLog('Error_Data')
    try:
        lstWorf = Worf.get_workflow()
        lstWorf = json.loads(lstWorf)
        for item in lstWorf:
            args.append((item['wid'], host['host'], item['name']))
    except Exception as e:
        logerr.error("Get worlkfow %s"%(e))
        raise
    return args

def get_node(host):
    """
    host: thomson name
    """
    node = Node(host = host['host'], user = host['user'], passwd = host['passwd'])
    args =[]
    logerr = getLog('Error_Data')
    #print host['host']
    try:
        lstNode = node.get_nodes()
        lstNode = json.loads(lstNode)
        #print len(lstNode)
        for item in lstNode:
            #print item
            args.append((item['nid'], host['host'], item['cpu'], item['alloccpu'], item['mem'], item['allocmem'], item['status'], item['state'], item['uncreahable']))
            #print len(args)
    except Exception as e:
        logerr.error("Get node %s"%(e))
        raise
    finally:
        #print len(args)
        return args 

def get_node_detail(host):
    """
    return array node detail
    host : thomson name
    """
    args = []
    lstnodeId = get_list_node_id(host['host'])
    try:
        for item in lstnodeId:
            node = NodeDetail(host['host'], host['user'], host['passwd'], item)
            array_jid = node.get_array_job_id()
            for ite in array_jid:
                args.append((int(item), host['host'], ite))
    except Exception as e:
        logerr = getLog('Error_Data')
        logerr.error("Get node %s"%(e))
    finally:
        return args

def get_list_node_id(host):
    """
    return array node id
    host: ip thomson
    """
    args = []
    db = Database()
    sql = "select nid from node where host = '{0}'".format(host)
    try:
         res = db.execute_query(sql)
         for item in res:
             args.append(item[0])
    except Exception as e:
        logerr = getLog("Error_Sync_Data")
        logerr.error("Get node id  %s"%(e))
    finally:
        return args

def get_job(host):
    """
    return array tuple, job, job param
    host : thomson name
    """
    argsJob = []
    #argsJobPara = []
    obJob = Job(host['host'], host['user'], host['passwd'])
    try:
        #lstjId = obJob.get_jobid_list()
        lstJob = obJob.get_job_non_jname()
        for item in lstJob:
            #isBackup = get_backup_job(host, item['jid'])
            tmp = (item['jid'], host['host'], item['state'], item['status'], item['prog'], item['ver'], item['startdate'], item['enddate'])
            argsJob.append(tmp)
            #logerr = getLog('Error_Sync_Data')
            #logerr.error("Get Job %s"%(argsJob))
            #argsJobPara.append((item['jid'], host['host'], item['jname'], item['wid'],"{0}".format(isBackup)))
    except Exception as e:
        logerr = getLog('Error_Sync_Data')
        logerr.error("Get Job %s"%(e))
    finally:
        return argsJob

def get_job_param(host):
    """
     return array tuple(job param)
    """
    argsJobparam = []
    obJob = Job(host['host'], host['user'], host['passwd'])
    try:
        lstjId = obJob.get_jobid_list()
        for item in lstjId:
            jname, wid, backup = JobDetail(host['host'], host['user'], host['passwd'],item).get_job_name_w_backup()
            argsJobparam.append((item, host['host'], jname, wid, backup))
            print item
            #argsJobPara.append((item['jid'], host['host'], item['jname'], item['wid'],"{0}".format(isBackup)))
    except Exception as e:
        logerr = getLog('Error_Sync_Data')
        logerr.error("Get Job Param %s"%(e))
    finally:
        return argsJobparam

def get_backup_job(host, jid):
    """
    return true/ flase
    get define backup of job
    """
    jDetail = JobDetail(host['host'], host['user'], host['passwd'], jid)
    args = json.loads(jDetail.get_param())
    for item in args[0]["params"]:
        return item['value'] if item['name'] == 'Define backup input' else 'flase'
    return 'flase'
