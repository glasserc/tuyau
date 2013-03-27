"""Tests for Tuyau"""

import os.path
from tuyau.document import Document

TESTDIR = os.path.dirname(__file__)

class DocumentFuzzy(Document):
    def __eq__(self, other):
        if isinstance(other, Document):
            return self.id == other.id and self.rev == other.rev
        return False

    @classmethod
    def wrap_all(cls, others):
        return map(cls.wrap, others)
