import json_wrapper
from uuid import uuid4, UUID

@json_wrapper.JSONDecoder.register_type
class Message(object):
    """Class representing a message"""
    def __init__(self, uuid=None):
        if not uuid:
            uuid = uuid4()
        if isinstance(uuid, (str, unicode)):
            uuid = UUID(uuid)

        self.uuid = uuid

    def to_json(self):
        cpy = self.__dict__.copy()
        cpy['type'] = 'Message'
        cpy['uuid'] = str(self.uuid)
        return cpy

    @classmethod
    def from_json(cls, o):
        o.pop('type')
        self = cls(**o)
        return self

    def __eq__(self, rhs):
        return self.uuid == rhs.uuid
