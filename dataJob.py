from Databasethomson import Database
from thomson_api import Job, JobDetail
from File import File
import config as osDb
import os
import threading
import Queue

# def create_tbJob():
#     db = Database()
#     sql='''create table job(jid int, host nvarchar(20), state char(10), status char(10), prog int, ver int, startdate bigint, enddate bigint)'''
#     if db.execute_query(sql) == 1:
#         print "success"
#     else:
#         print "error"

def create_tbJob():
    sql = "create table job(jid int, host nvarchar(20), state char(10), status char(10), prog int unsigned, ver int unsigned, startdate int unsigned, enddate int unsigned);"
    command = command_sql(sql)
    try:
        os.system(command)
        print "###success###"
    except Exception as e:
        raise e

def create_tbParam():
    sql = "create table job_param(jid int unsigned, host nvarchar(20), name nvarchar(50), wid nvarchar(50));"
    command = command_sql(sql)
    try:
        os.system(command)
    except Exception as e:
        raise e

def create_tbWorkflow():
    sql= """create table workflow(wid nvarchar(50), name nvarchar(50));"""

#insert job table
def insert_job(host):
    response_xml = Job().get_job_xml()
    sql = Job().parse_xml_2_query(response_xml, host)
    command = command_sql(sql)
    try:
        os.system(command)
        print "success"
    except Exception as e:
        raise e

#array list jid
def get_lstJob_id():
    db = Database()
    sql = """select jid, host from job;"""
    lstJob = db.execute_query(sql)
    args = []
    for job in lstJob:
        args.append({'jid'      :job[0], 'host'     :job[1]})
    return args

#insert param table
def insert_param(lstJid):
    sql = """truncate job_param;"""
    lstJob = get_lstJob_id()    
    for job in lstJob:
        param = JobDetail(job['jid'], job['host'])
        sql += param.parse_xml_2_query(param.get_param())
    command = command_sql(sql)
    try:
        os.system(command)
        print "###success###"
    except Exception as e:
        raise e

def command_sql(sql):
    return """mysql -u%s -p%s %s -h %s -e "%s" """%(osDb.DATABASE_USER, osDb.DATABASE_PASSWORD, osDb.DATABASE_NAME, osDb.DATABASE_HOST, sql)

# insert_job("localhost")
insert_param(get_lstJob_id())
# create_tbParam()