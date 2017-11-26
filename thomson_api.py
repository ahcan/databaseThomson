from xml.dom import minidom
from setting.DateTime import *
from setting.File import *
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

    def parse_xml(self, xml, host):
        xmldoc = minidom.parseString(xml)
        itemlist = xmldoc.getElementsByTagName('jGetList:JItem')
        sql = ""
        for s in itemlist:
            State,Status,JId,Prog,StartDate,EndDate,Ver = self.parse_dom_object(s)
            
            sql += "insert into job (jid, host, state, status, prog, ver, startdate, enddate) values(%d,'%s','%s','%s',%d,%d,%d,%d);"%(int(JId), host, State, Status, int(Prog), int(Ver), DateTime().conver_UTC_2_unix_timestamp(StartDate), DateTime().conver_UTC_2_unix_timestamp(EndDate)) 
        print sql
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
