"""
Actions to be used as callbacks
"""
import logging

class Action(object):
    def __call__(self, msg):
        pass

class LogWithLogging(Action):
    def __init__(self, logger):
        if isinstance(logger, (str, unicode)):
            logger = logging.getLogger(logger)
        self.logger = logger

    def __call__(self, msg):
        self.logger.info("Message: {}".format(msg.to_json()))

class LogToFile(Action):
    def __init__(self, fp):
        if isinstance(fp, str):
            fp = file(fp)
        self.file = fp

    def __call__(self, msg):
        self.file.write("Message: {}\n".format(msg.to_json()))
