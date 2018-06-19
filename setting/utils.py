from thomsonapi import Workflow, Log
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
        print host['host']
    except Exception as e:
        logerr.error("Get worlkfow %s"%(e))
        raise
    return args
