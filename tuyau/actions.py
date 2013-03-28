"""
Actions to be used as callbacks
"""
import logging
from tuyau.registry import TypeRegistry

class Action(TypeRegistry):
    CLASSES = {} # for TypeRegistry

    def __call__(self, msg):
        pass

@Action.register_class
class LogWithLogging(Action):
    def __init__(self, logger):
        self.logger_name = None
        if isinstance(logger, (str, unicode)):
            self.logger_name = logger
            logger = logging.getLogger(logger)
        self.logger = logger

    def __call__(self, msg):
        self.logger.info("Message: {}".format(msg.to_json()))

    def to_json(self):
        dct = super(LogWithLogging, self).to_json()
        dct.pop('logger')
        dct.pop('logger_name')
        if not self.logger_name:
            raise ValueError, "Can't serialize non-string based logger"
        dct['logger'] = self.logger_name
        return dct

@Action.register_class
class LogToFile(Action):
    def __init__(self, fp):
        if isinstance(fp, str):
            fp = file(fp)
        self.file = fp

    def __call__(self, msg):
        self.file.write("Message: {}\n".format(msg.to_json()))
