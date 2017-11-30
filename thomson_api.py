from xml.dom import minidom
from setting.DateTime import *
from setting.File import *

class Thomson:
    def __init__(self):
        self.user = settings.user
        self.passwd = settings.passwd
        self.url = settings.url

    def get_response(self, headers, body):
        response = requests.post(self.url, data=body, headers=headers, \
            auth=HTTPDigestAuth(self.user, self.passwd))
        #print response.content
        response_xml = response.content[response.content.find('<soapenv:Envelope') :\
         response.content.find('</soapenv:Envelope>') + len('</soapenv:Envelope>')]
        return response_xml

class Job:
    # def __init__(self):
        # from setting.xmlReq.JobReq import HEADERS
        # self.headers = HEADERS

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

    def parse_xml_2_query(self, xml, host):
        xmldoc = minidom.parseString(xml)
        itemlist = xmldoc.getElementsByTagName('jGetList:JItem')
        sql = "truncate job;"
        for s in itemlist:
            State,Status,JId,Prog,StartDate,EndDate,Ver = self.parse_dom_object(s)
            
            sql += "insert into job (jid, host, state, status, prog, ver, startdate, enddate) values(%d,'%s','%s','%s',%d,%d,%d,%d);"%(int(JId), host, State, Status, int(Prog), int(Ver), DateTime().conver_UTC_2_unix_timestamp(StartDate), DateTime().conver_UTC_2_unix_timestamp(EndDate)) 
        return sql
    
    # return json theo name id job
    def parse_xml_name(self, xml):
        xmldoc = minidom.parseString(xml)
        itemlist = xmldoc.getElementsByTagName('jGetList:JItem')
        args=[]
        workflow_list_json = Workflow().get_workflow()
        for s in itemlist:
            State,Status,JId,Prog,StartDate,EndDate,Ver,jobname,workflowIdRef,workflow_name = self.parse_dom_object(s, workflow_list_json)
            args.append({'jname'    : jobname,
                        'jid'       : int(JId),
                })
        return json.dumps(args)

    def count_object(self, xml):
        xmldoc = minidom.parseString(xml)
        itemlist = xmldoc.getElementsByTagName('jGetList:JItem')
        return len(itemlist)


    def get_job_xml(self):
        from setting.xmlReq.JobReq import BODY
        body = BODY
        #response_xml = Thomson().get_response(self.headers, body)
        response_xml = File().get_response('JobGetListRsp.xml')
        return response_xml

    def get_jobid_list(self):
        response_xml = self.get_job_xml()
        xmldoc = minidom.parseString(response_xml)
        itemlist = xmldoc.getElementsByTagName('jGetList:JItem')
        args=[]
        for s in itemlist:
            str_tmp = str(s.attributes.items())
            JId = s.attributes['JId'].value if "'JId'" in str_tmp else ''
            args.append(int(JId))
        return args

    def get_job(self):
        response_xml = self.get_job_xml()
        return self.parse_xml(response_xml)

    def get_job_name(self): # get name id job
        response_xml = self.get_job_xml()
        return self.parse_xml_name(response_xml)

    def count_job(self):
        response_xml = self.get_job_xml()
        return self.count_object(response_xml)

    def get_Waiting_xml(self):
        from setting.xmlReq.JobReq import WAITTING
        body = WAITTING
        #response_xml = Thomson().get_response(self.headers, body)
        response_xml = File().get_response('JobGetListRsp.xml')
        return response_xml

    def get_Waiting(self):
        response_xml = self.get_Waiting_xml()
        return self.parse_xml(response_xml)

    def count_Waiting(self):
        response_xml = self.get_Waiting_xml()
        return self.count_object(response_xml)

    def get_Running_xml(self):
        from setting.xmlReq.JobReq import RUNNING
        body = RUNNING
        #response_xml = Thomson().get_response(self.headers, body)
        response_xml = File().get_response('JobGetListRsp.xml')
        return response_xml

    def get_Running(self):
        xml = self.get_Running_xml()
        return self.parse_xml(xml)

    def count_Running(self):
        response_xml = self.get_Running_xml()
        return self.count_object(response_xml)

    def get_Paused_xml(self):
        from setting.xmlReq.JobReq import PAUSED
        body = PAUSED
        #response_xml = Thomson().get_response(self.headers, body)
        response_xml = File().get_response('JobGetListRsp.xml')
        return response_xml

    def get_Paused(self):
        response_xml = self.get_Paused_xml()
        return self.parse_xml(response_xml)

    def count_Paused(self):
        response_xml = self.get_Paused_xml()
        return self.count_object(response_xml)

    def get_Completed_xml(self):
        from setting.xmlReq.JobReq import COMPLETED
        body = COMPLETED
        #response_xml = Thomson().get_response(self.headers, body)
        response_xml = File().get_response('JobGetListRsp.xml')
        return response_xml

    def get_Completed(self):
        response_xml = self.get_Completed_xml()
        return self.parse_xml(response_xml)

    def count_Completed(self):
        response_xml = self.get_Completed_xml()
        return self.count_object(response_xml)

    def get_Aborted_xml(self):
        from setting.xmlReq.JobReq import ABORTED
        body = ABORTED
        #response_xml = Thomson().get_response(self.headers, body)
        response_xml = File().get_response('JobGetListRsp.xml')
        return response_xml

    def get_Aborted(self):
        response_xml = self.get_Aborted_xml()
        return self.parse_xml(response_xml)

    def count_Aborted(self):
        response_xml = self.get_Aborted_xml()
        return self.count_object(response_xml)

    def get_job_detail_by_job_id(self, arr_job_id):
        #print arr_job_id
        job_xml = self.get_job_xml()
        xmldoc = minidom.parseString(job_xml)
        itemlist = xmldoc.getElementsByTagName('jGetList:JItem')
        args=[]
        workflow_list_json = Workflow().get_workflow()
        for job in itemlist:
            str_tmp = str(job.attributes.items())
            JId = job.attributes['JId'].value if "'JId'" in str_tmp else '-1'
            if int(JId) in arr_job_id:
                State,Status,JId,Prog,StartDate,EndDate,Ver,jobname,workflowIdRef,workflow_name = self.parse_dom_object(job, workflow_list_json)
                args.append({'jname'    : jobname,
                            'wid'       : workflowIdRef,
                            'wname'     : workflow_name,
                            'state'     : State,
                            'status'    : Status,
                            'jid'       : JId,
                            'prog'      : Prog,
                            'startdate' : DateTime().conver_UTC_2_unix_timestamp(StartDate) \
                            if StartDate else '',
                            'ver'       : Ver,
                            'enddate'   : DateTime().conver_UTC_2_unix_timestamp(EndDate) \
                            if EndDate else ''
                    })
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
        # body = body.replace('JobID', str(self.jid))
        #response_xml = Thomson().get_response(self.headers, self.body)
        response_xml = File().get_response('responseXml/JobGetParamsRsp.xml')
        return response_xml
    def parse_xml_2_query(self, xml):
        xmldoc = minidom.parseString(xml)
        joblist = xmldoc.getElementsByTagName('wd:Job')
        job = joblist[0]
        jobname = job.attributes['name'].value if "'name'" in str(job.attributes.items()) else ''
        workflowIdRef = job.attributes['workflowIdRef'].value if "'workflowIdRef'" in str(job.attributes.items()) else ''
        return """insert into job_param(jid, host, name, wid) values(%d, '%s', '%s', '%s');"""%(int(self.jid), self.host, jobname.encode('utf-8'), workflowIdRef.encode('utf-8'))

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
        sql =""
        for s in itemlist:
            str_tmp = str(s.attributes.items())
            Name = s.attributes['Name'].value if "'Name'" in str_tmp else ''
            WId = s.attributes['WId'].value if "'WId'" in str_tmp else ''
            PubVer = s.attributes['PubVer'].value if "'PubVer'" in str_tmp else ''
            PriVer = s.attributes['PriVer'].value if "'PriVer'" in str_tmp else ''
            sql += "insert into  workflow(wid, name, host, pubver, priver) values('%s','%s','%s',%d,%d);"%(WId.encode('utf-8'), Name.encode('utf-8'), self.host, int(PubVer), int(PriVer))
            # print sql
        return sql

    def get_workflow_xml(self):
        from setting.xmlReq.WorkflowReq import BODY
        body = BODY
        #response_xml = Thomson().get_response(self.headers, body)
        response_xml = File().get_response('responseXml/WorklowGetListRsp.xml')
        return response_xml
    def get_workflow(self):
        response_xml = self.get_workflow_xml()
        return response_xml