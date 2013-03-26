import json_wrapper

@json_wrapper.JSONDecoder.register_type
class Message(object):
    """Class representing a message"""
    def __init__(self, *args, **kwargs):
        pass

    def to_json(self):
        cpy = self.__dict__.copy()
        cpy['type'] = 'Message'
        return cpy

    @classmethod
    def from_json(cls, o):
        self = cls()
        # This is kind of hacky, only necessary because I don't have
        # any real message types yet
        for k, v in o.iteritems():
            setattr(self, k, v)
        return self

    def __cmp__(self, rhs):
        return type(self) == type(rhs) and self.__dict__ == rhs.__dict__
