#-*- encoding: utf-8
from xml.dom import minidom
import requests
from requests.auth import HTTPDigestAuth
from setting.DateTime import *
from setting.File import *
from setting import config as osDb

class Thomson:
    def __init__(self, host):
        self.user = host['user']
        self.passwd = host['passwd']
        self.url = host['url']

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
            
            sql += "(%d,'%s','%s','%s',%d,%d,%d,%d),"%(int(JId), self.host['host'], State, Status, int(Prog), int(Ver), DateTime().conver_UTC_2_unix_timestamp(StartDate), DateTime().conver_UTC_2_unix_timestamp(EndDate)) 
        return sql.encode('utf-8')
    
    def get_job_xml(self):
        from setting.xmlReq.JobReq import BODY
        body = BODY
        # response_xml = Thomson(self.host).get_response(self.headers, body)
        response_xml = File('setting/').get_response('JobGetListRsp.xml')
        return response_xml

    def count_job(self, xml):
        xmldoc = minidom.parseString(xml)
        itemlist = xmldoc.getElementsByTagName('jGetList:JItem')
        args = []
        for item in itemlist:
            State,Status,JId,Prog,StartDate,EndDate,Ver = self.parse_dom_object(item)
            args.append({'jid':JId,'host': self.host})
        return args


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
        # response_xml = Thomson(self.host).get_response(self.headers, body)
        response_xml = File('setting/responseXml/').get_response('JobGetParamsRsp.xml')
        return response_xml
    def parse_xml_2_query(self, xml):
        xmldoc = minidom.parseString(xml)
        joblist = xmldoc.getElementsByTagName('wd:Job')
    	try:
            job = joblist[0]
            jobname = job.attributes['name'].value if "'name'" in str(job.attributes.items()) else ''
            workflowIdRef = job.attributes['workflowIdRef'].value if "'workflowIdRef'" in str(job.attributes.items()) else ''
            return """(%d, '%s', '%s', '%s'),"""%(int(self.jid), self.host['host'], jobname.encode('utf-8'), workflowIdRef.encode('utf-8'))
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
            sql += "('%s','%s','%s',%d,%d),"%(WId.encode('utf-8'), Name.encode('utf-8'), self.host['host'], int(PubVer), int(PriVer))
        return sql

    def get_workflow_xml(self):
        from setting.xmlReq.WorkflowReq import BODY
        body = BODY
        # response_xml = Thomson(self.host).get_response(self.headers, body)
        response_xml = File("setting/responseXml/").get_response('WorklowGetListRsp.xml')
        return response_xml
    def get_workflow(self):
        response_xml = self.get_workflow_xml()
        return response_xml

######################################
#------------Node--------------------#
######################################
class Node:
    """docstring for Node"""
    def __init__(self, host):
            from setting.xmlReq import NodeReq
            headers = NodeReq.HEADERS
            body = NodeReq.BODY
            self.headers = headers
            self.body = body
            self.host = host

    def get_nodes_xml(self):
        #response_xml = Thomson(self.host).get_response(self.headers, self.body)
        response_xml = File('setting/responseXml/').get_response('SystemGetNodesStatsRsp.xml')
        return response_xml

    def parse_dom_object(self, dom_object):
        text = str(dom_object.attributes.items())
        NStatus = dom_object.attributes['NStatus'].value if "'NStatus'" in text else ''
        Cpu = dom_object.attributes['Cpu'].value if "'Cpu'" in text else '-1'
        AllocCpu = dom_object.attributes['AllocCpu'].value if "'AllocCpu'" in text else '-1'
        Unreachable = dom_object.attributes['Unreachable'].value if "'Unreachable'" in text else ''
        NId = dom_object.attributes['NId'].value if "'NId'" in text else '-1'
        NState = dom_object.attributes['NState'].value if "'NState'" in text else ''
        Mem =  dom_object.attributes['Mem'].value if "'Mem'" in text else '-1'
        AllocMem = dom_object.attributes['AllocMem'].value if "'AllocMem'" in text else '-1'
        return NStatus,Cpu,AllocCpu,Unreachable,NId,NState,Mem,AllocMem

    def parse_dom_object_nid(self, dom_object):
        text = str(dom_object.attributes.items())
        NId = dom_object.attributes['NId'].value if "'NId'" in text else '-1'
        return NId

    def parse_xml_2_query(self, xml):
        args = []
        xmldoc = minidom.parseString(xml)
        itemlist = xmldoc.getElementsByTagName('sGetNodesStats:RspSGNSOk')
        sql = ''
        for node in itemlist.item(0).childNodes:
            NStatus,Cpu,AllocCpu,Unreachable,NId,NState,Mem,AllocMem = self.parse_dom_object(node)
            sql += """(%d,'%s',%d,%d,%d,%d,'%s','%s','%s'),"""%(int(NId),self.host['host'],int(Cpu),int(AllocCpu),int(Mem),int(AllocMem),NStatus.encode('utf-8'),NState.encode('utf-8'),Unreachable.encode('utf-8'))
        return sql

    def get_node(self):
        xml = self.get_nodes_xml()
        # sql = 
        return self.parse_xml_2_query(xml), self.parse_detail_2_query(xml)

    def parse_detail_2_query(self, xml):
        args = []
        args_nodes = []
        xmldoc = minidom.parseString(xml)
        intemlist = xmldoc.getElementsByTagName('sGetNodesStats:RspSGNSOk')
        sql = ''
        for node in intemlist.item(0).childNodes:
            nid = self.parse_dom_object_nid(node)
            args.append(nid)
            args_nodes.append({nid:node})
        for nid in args:
            # args_jid = []
            # print args_nodes[args.index(nid)]
            # args_jid.append(self.get_array_job_id(args_nodes[args.index(nid)],nid))
            for jid in self.get_array_job_id(args_nodes[args.index(nid)],nid):
                # print jid
                sql +="""(%d,'%s',%d),"""%(int(nid), self.host['host'], int(jid))
        return sql

    def get_array_job_id(self, dom_node, nid):
        array_jid = []
        dom_node = dom_node[nid]
        for node_status_detail in dom_node.childNodes:
            text = str(node_status_detail.attributes.items())
            jid = node_status_detail.attributes['JId'].value if "'JId'" in text else ''
            if jid:
                array_jid.append(int(jid))
        return array_jid

    def get_dom_node(self, xml, nid):
        dom_node = None
        nodes_xml = xml
        xmldoc = minidom.parseString(nodes_xml)
        itemlist = xmldoc.getElementsByTagName('sGetNodesStats:RspSGNSOk')
        for node in itemlist.item(0).childNodes:
            text = str(node.attributes.items())
            NId = node.attributes['NId'].value if "'NId'" in text else -1
            if int(NId) == nid:
                dom_node = node
        return dom_node