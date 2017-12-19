#-*- encoding: utf-8
from xml.dom import minidom
import requests
from requests.auth import HTTPDigestAuth
from setting.DateTime import *
from setting.File import *
from setting import config as osDb

class Thomson:
    def __init__(self):
        self.user = osDb.THOMSON_USER
        self.passwd = osDb.THOMSON_PASSWORD
        self.url = osDb.THOMSON_URL

    def get_response(self, headers, body):
        response = requests.post(self.url, data=body, headers=headers, \
            auth=HTTPDigestAuth(self.user, self.passwd))
        #print response.content
        response_xml = response.content[response.content.find('<soapenv:Envelope') :\
         response.content.find('</soapenv:Envelope>') + len('</soapenv:Envelope>')]
        return response_xml

class Job:
    def __init__(self, host):
        from setting.xmlReq.JobReq import HEADERS
        self.headers = HEADERS
        self.host = host

    def parse_dom_object(self, dom_object):
        str_tmp = str(dom_object.attributes.items())
        State = dom_object.attributes['State'].value if "'State'" in str_tmp else ''
        Status = dom_object.attributes['Status'].value if "'Status'" in str_tmp else ''
        JId = dom_object.attributes['JId'].value if "'JId'" in str_tmp else ''
        Prog = dom_object.attributes['Prog'].value if "'Prog'" in str_tmp else ''
        StartDate =  dom_object.attributes['StartDate'].value \
        if "'StartDate'" in str_tmp else 'null'
        Ver = dom_object.attributes['Ver'].value if "'Ver'" in str_tmp else ''
        EndDate = dom_object.attributes['EndDate'].value if "'EndDate'" in str_tmp else 'null'
        return State,Status,JId,Prog,StartDate,EndDate,Ver

    def parse_xml_2_query(self, xml):
        xmldoc = minidom.parseString(xml)
        itemlist = xmldoc.getElementsByTagName('jGetList:JItem')
        sql=''
        for s in itemlist:
            State,Status,JId,Prog,StartDate,EndDate,Ver = self.parse_dom_object(s)
            
            sql += "(%d,'%s','%s','%s',%d,%d,%d,%d),"%(int(JId), self.host, State, Status, int(Prog), int(Ver), DateTime().conver_UTC_2_unix_timestamp(StartDate), DateTime().conver_UTC_2_unix_timestamp(EndDate)) 
        return sql.encode('utf-8')
    
    def get_job_xml(self):
        from setting.xmlReq.JobReq import BODY
        body = BODY
        # response_xml = Thomson().get_response(self.headers, body)
        response_xml = File('setting/').get_response('JobGetListRsp.xml')
        return response_xml


######################################
#-----------Job Detail---------------#
######################################
class JobDetail:
    def __init__(self, jid, host):
        from setting.xmlReq.JobDetailReq import HEADERS, BODY
        self.headers = HEADERS
        self.body = BODY
        self.jid = jid
        self.host = host
    def get_param_xml(self):
        body = self.body.replace('JobID', str(self.jid))
        # response_xml = Thomson().get_response(self.headers, body)
        response_xml = File('setting/responseXml/').get_response('JobGetParamsRsp.xml')
        return response_xml
    def parse_xml_2_query(self, xml):
        xmldoc = minidom.parseString(xml)
        joblist = xmldoc.getElementsByTagName('wd:Job')
	try:
            job = joblist[0]
            jobname = job.attributes['name'].value if "'name'" in str(job.attributes.items()) else ''
            workflowIdRef = job.attributes['workflowIdRef'].value if "'workflowIdRef'" in str(job.attributes.items()) else ''
            return """(%d, '%s', '%s', '%s'),"""%(int(self.jid), self.host, jobname.encode('utf-8'), workflowIdRef.encode('utf-8'))
        except Exception as e:
            print e
            return ""

    def get_param(self):
        response_xml = self.get_param_xml()
        return response_xml

######################################
#-----------WORKFLOW-----------------#
######################################
class Workflow:
    def __init__(self, host):
        from setting.xmlReq.WorkflowReq import HEADERS
        self.headers = HEADERS
        self.host = host

    def parse_xml_2_query(self, xml):
        xmldoc = minidom.parseString(xml)
        itemlist = xmldoc.getElementsByTagName('wGetList:WItem')
        sql =''
        for s in itemlist:
            str_tmp = str(s.attributes.items())
            Name = s.attributes['Name'].value if "'Name'" in str_tmp else ''
            WId = s.attributes['WId'].value if "'WId'" in str_tmp else ''
            PubVer = s.attributes['PubVer'].value if "'PubVer'" in str_tmp else ''
            PriVer = s.attributes['PriVer'].value if "'PriVer'" in str_tmp else ''
            sql += "('%s','%s','%s',%d,%d),"%(WId.encode('utf-8'), Name.encode('utf-8'), self.host, int(PubVer), int(PriVer))
        return sql

    def get_workflow_xml(self):
        from setting.xmlReq.WorkflowReq import BODY
        body = BODY
        # response_xml = Thomson().get_response(self.headers, body)
        response_xml = File("setting/responseXml/").get_response('WorklowGetListRsp.xml')
        return response_xml
    def get_workflow(self):
        response_xml = self.get_workflow_xml()
        return response_xml
