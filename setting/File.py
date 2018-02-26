#-*- encoding: utf-8
import io
import json
import logging, logging.config
class File:
    def __init__(self, path):
        self.file_path = path

    def read(self, filename):
        #print self.file_path + filename
        f = open(self.file_path + filename , 'r')
        lines=f.read()
        f.close()
        #return data
        return lines

    def append(self, filename, text):
        f = open(self.file_path + filename, 'a')
        f.write(text+"\n")
        f.close()

    def get_response(self, filename):
        response = self.read(filename)
        return response

    def write_log(self, filename, content):
        f = io.open(self.file_path + filename, 'w')
        f.write(content)
        f.close()

def getLog(loggerName):
    with open("setting/logging_configuration.json", 'r') as configuration_file:
        config_dict = json.load(configuration_file)
    logging.config.dictConfig(config_dict)
    # Log that the logger was configured
    return logging.getLogger(loggerName)