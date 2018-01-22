#-*- coding: utf-8
from setting.Databasethomson import Database
from setting import config as osDb
import os
import time
def command_sql(sql):
    return """mysql -u%s -p'%s' %s -h %s -e "%s" """%(osDb.DATABASE_USER, osDb.DATABASE_PASSWORD, osDb.DATABASE_NAME, osDb.DATABASE_HOST, sql)

def main():
    #time.sleep(1800)
    time.sleep(10)
    strQuery = 'truncate job_param;alter table job_param auto_increment = 1;'
    os.system(command_sql(strQuery))
    print "truncate complie"
if __name__ == '__main__':
    main()
