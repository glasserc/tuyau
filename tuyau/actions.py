"""
Actions to be used as callbacks
"""
import os.path
import glob
import logging
from tuyau.registry import TypeRegistry

class Action(TypeRegistry):
    CLASSES = {} # for TypeRegistry

    def __call__(self, doc, couchdb):
        pass

@Action.register_class
class LogWithLogging(Action):
    def __init__(self, logger):
        self.logger_name = None
        if isinstance(logger, (str, unicode)):
            self.logger_name = logger
            logger = logging.getLogger(logger)
        self.logger = logger

    def __call__(self, doc, couchdb):
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

    def __call__(self, doc, couchdb):
        self.file.write("Message: {}\n".format(doc.to_json()))

@Action.register_class
class SaveToMaildir(Action):
    def __init__(self, path):
        self.path = path

    def __call__(self, doc, couchdb):
        # Verify that we have everything we need
        if not (doc.folder and doc.filename and doc.content):
            return

        # Filename without any info/flags
        base_filename = doc.filename
        subdir = 'new'
        if ':' in doc.filename:
            base_filename = doc.filename[:doc.filename.index(':')]
            subdir = 'cur'

        new_filename = os.path.join(self.path, doc.folder, subdir,
                                    doc.filename)

        # Look to see if we need to move this file
        old_file = os.path.join(self.path, doc.folder,
                                'new/{}'.format(base_filename))
        if not os.path.exists(old_file):
            current = glob.glob(os.path.join(self.path, doc.folder,
                                             'cur/{}:*'.format(base_filename)))
            if current:
                old_file = current[0]
            else:
                old_file = None

        if old_file:
            os.rename(old_file, new_filename)
        else:
            fp = file(new_filename, 'w')
            fp.write(doc.content)
            fp.close()
