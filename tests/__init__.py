"""Tests for Tuyau"""

import os.path
from tuyau.document import Document
from tuyau.application import Application

TESTDIR = os.path.dirname(__file__)

class DocumentFuzzy(Document):
    def __eq__(self, other):
        if isinstance(other, Document):
            return self.id == other.id and self.rev == other.rev
        return False

    @classmethod
    def wrap_all(cls, others):
        return map(cls.wrap, others)

    @classmethod
    def strip_configs(cls, with_configs):
        no_config = [doc for doc in with_configs if doc.get('type') != "Config"]
        return cls.wrap_all(no_config)

    @classmethod
    def only_configs(cls, with_configs):
        config = [doc for doc in with_configs if doc.get('type') == "Config"]
        return cls.wrap_all(config)

def TestApplication(*args, **kwargs):
    kwargs.setdefault('insecure', True)
    return Application(*args, **kwargs)
