#Database
DATABASE_NAME = 'thomson'
#DATABASE_NAME = 'thomson_test'
DATABASE_USER = 'thomson'
#DATABASE_USER = 'root'
DATABASE_PASSWORD = 'thomson@$@'
#DATABASE_PASSWORD = 'root'
DATABASE_HOST = 'localhost'
DATABASE_PORT = 3306
#Thomson
# THOMSON_HOST = '172.29.3.189'
# THOMSON_USER = 'nguyennt9'
# THOMSON_PASSWORD = '123456'
# THOMSON_URL = 'http://%s/services/Maltese'%(THOMSON_HOST)
THOMSON_HOST=[
    {
        'user' : 'iptv_tool', #hcm
        'passwd' : '123456',
        'host'  : '172.29.3.189',
        'url' : 'http://%s/services/Maltese' % ('172.29.3.189'),
    },
    {
        'user' : 'iptv_tool', #hni
        'passwd' : '123456',
        'host'  :   '172.29.70.189',
        'url' : 'http://%s/services/Maltese' % ('172.29.70.189'),
    },
    #{
    #    'user' : 'iptv_tool', #lab
    #    'passwd' : '123456',
    #    'host'  : '172.17.5.110',
    #    'url' : 'http://%s/services/Maltese' % ('172.17.5.110'),
    #},
]
