"""
Actions to be used as callbacks
"""
import os.path
import logging
from tuyau.registry import TypeRegistry

class Action(TypeRegistry):
    CLASSES = {} # for TypeRegistry

    def __call__(self, doc):
        pass

@Action.register_class
class LogWithLogging(Action):
    def __init__(self, logger):
        self.logger_name = None
        if isinstance(logger, (str, unicode)):
            self.logger_name = logger
            logger = logging.getLogger(logger)
        self.logger = logger

    def __call__(self, doc):
        self.logger.info("Message: {}".format(doc.to_json()))

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

    def __call__(self, doc):
        self.file.write("Message: {}\n".format(doc.to_json()))

@Action.register_class
class SaveToMaildir(Action):
    def __init__(self, path):
        self.path = path

    def __call__(self, doc):
        # Verify that we have everything we need
        if not (doc.folder and doc.filename and doc.content):
            return

        if ':' in doc.filename:
            subdir = 'cur'
        else:
            subdir = 'new'

        # FIXME: remove old versions of this message

        fp = file(os.path.join(self.path, doc.folder, subdir, doc.filename), 'w')
        fp.write(doc.content)
        fp.close()
