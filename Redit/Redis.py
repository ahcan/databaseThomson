import redis
from setting.settings import REDIS
import logging, logging.config
from setting import getLog

class Redit(object):
    def __init__(self, key):
        self.logger = getLog("Redit")
        self.logger.setLevel(logging.DEBUG)
        super(Redit, self).__init__()
        self.key = key
        POOL = redis.ConnectionPool(host=REDIS['host'], 
                                    port=REDIS['port'], 
                                    db=REDIS['db'])
        self.conn = redis.Redis(connection_pool=POOL)

    def set_data(self, name, val):
        """
        name: string key to get value in main key
        """
        try:
            # return self.conn.hset(name= self.key, key = name, value = val)
            # print("name {0}".format(name))
            self.conn.hmset(self.key, {'{0}'.format(name): val})
            self.logger.debug("Set data Redit {0} OK".format(self.key))
            return True
        except Exception as e:
            self.logger.error(e)
            self.logger.debug("Set data Redit {0} Fail".format(self.key))

    def get_all(self):
        try:
            result = self.conn.hgetall(self.key)
            result = result if result else ''
            self.logger.debug("Get all data {0} OK".format(self.key))
            return result
        except Exception as e:
            self.logger.error(e)
            self.logger.debug("Get all data {0} Fail".format(self.key))
            return False

    def get_data(self, name):
        """
        name is key to get data
        """
        try:
            result = self.conn.hget(name=self.key, key=name)
            result = result if result else ''
            return result
        except Exception as e:
            self.logger.error(e)
            self.logger.debug("Get data {0}".format(self.key))
            return False