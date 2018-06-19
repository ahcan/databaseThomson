from thomsonapi import Workflow, Log, Node, NodeDetail
import config
import json
import logging, logging.config
from File import getLog
from setting.Databasethomson import Database

def get_workflow(host):
    """
    host: name thomson
    """
    Worf = Workflow(host = host['host'], user = host['user'], passwd = host['passwd'])
    args =[]
    logerr = getLog('Error_Data')
    try:
        lstWorf = Worf.get_workflow()
        lstWorf = json.loads(lstWorf)
        for item in lstWorf:
            args.append((item['wid'], item['name'], host['host']))
    except Exception as e:
        logerr.error("Get worlkfow %s"%(e))
        raise
    return args

def get_node(host):
    """
    host: name thomson
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
    host : name thomson
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
        logerr = getLog("Error_Data")
        logerr.error("Get node id  %s"%(e))
    finally:
        return args
