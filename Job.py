from Databasethomson import Database
import threading

def create_tbJob():
    db = Database()
    sql='''create table job(jid int, host nvarchar(20))'''
    if db.execute_query(sql) == 1:
        print "success"
    else:
        print "error"
def add_Job(jid, host):
    db = Database();
    sql = '''insert into job (jid, host) values(%d, %s)'''%(jid, host)
    if db.execute_query(sql):
        print "success"
    else:
        print "error"

def get_Job():
    