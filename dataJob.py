from Databasethomson import Database
from thomson_api import Job
from File import File
import threading

def create_tbJob():
    db = Database()
    sql='''create table job(jid int, host nvarchar(20))'''
    if db.execute_query(sql) == 1:
        print "success"
    else:
        print "error"
def insert_job(host):
    response_xml = File().get_response('JobGetListRsp.xml')
    db = Database();
    sql = Job().parse_xml(response_xml, host)
    if db.execute_query(sql):
        print "success"
    else:
        print "error"

insert_job("local")