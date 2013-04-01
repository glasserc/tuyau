from couchdb.mapping import Document
from uuid import uuid4, UUID

class Document(Document):
    """Base class for all Tuyau objects"""

class Mail(Document):
    def __init__(self, filename, folder='INBOX', content=None):
        super(Mail, self).__init__()
        self.filename = filename
        self.folder = folder
        self.content = content
