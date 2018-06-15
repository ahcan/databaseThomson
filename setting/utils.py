from thomsonapi import Workflow, Log
import config
import json
import logging, logging.config
from File import getLog

def get_worlkflow(host):
    """
    host: name thomson
    """
    Worf = Workflow(host = host['host'], user = host['user'], passwd = host['passwd'])
    args =[]
    logerr = getLog('data_error_handler')
    try:
        lstWorf = Worf.get_workflow()
        lstWorf = json.loads(lstWorf)
        for item in lstWorf:
            tup = (item['id'], item['name'], host['host'])
            args.append(tup)
    except Exception as e:
        logerr.error("Get worlkfow %s"%(e))
        raise
    return args
