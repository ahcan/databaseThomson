from thomsonapi import Workflow, Log, Node, NodeDetail
import config
import json
import logging, logging.config
from File import getLog

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
    try:
        lstNode = node.get_nodes_xml()
        lstNode = json.loads(node.parse_xml(lstNode))
        for item in lstNode:
            args.append((item['nid'], item['host'], item['cpu'], item['alloccpu'], item['mem'], item['allocmem'], item['status'], item['state'], item['uncreachable']))
    except Exception as e:
        logerr.error("Get node %s"%(e))
        raise
    finally:
        return 0
