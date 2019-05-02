#-*- encoding: utf-8
import io
import json
import logging, logging.config

def getLog(loggerName):
    with open("Redit/setting/logging_configuration.json", 'r') as configuration_file:
        config_dict = json.load(configuration_file)
    logging.config.dictConfig(config_dict)
    # Log that the logger was configured
    return logging.getLogger(loggerName)