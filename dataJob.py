from Databasethomson import Database
from thomson_api import Job
from File import File
import threading

def create_tbJob():
    db = Database()
    sql='''create table job(jid int, host nvarchar(20), state char(10), status char(10), prog int, ver int, startdate bigint, enddate bigint)'''
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

# insert_job("local")
# create_tbJob()
def insert_1():
    db = Database();
    detable = "truncate job;"
    db.execute_query(detable)
    sql = '''insert into job (jid, host, state, status, prog, ver, startdate, enddate) values(13452,'local','Running','Ok',0,11,1507778546,0); COMMIT; insert into job (jid, host, state, status, prog, ver, startdate, enddate) values(13452,'local','Running','Ok',0,11,1507778546,0); COMMIT; insert into job (jid, host, state, status, prog, ver, startdate, enddate) values(13452,'local','Running','Ok',0,11,1507778546,0); COMMIT;'''
    if db.execute_query(sql):
        print "success"
    else:
        print "error"

insert_1()