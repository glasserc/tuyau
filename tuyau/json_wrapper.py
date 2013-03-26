"""
JSON utilities
"""
import json

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, 'to_json'):
            return o.to_json()

        return super(JSONEncoder, self).default(o)

class JSONDecoder(json.JSONDecoder):
    """JSONDecoder that knows about tuyau types"""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('object_hook', self.decode_obj)
        super(JSONDecoder, self).__init__(*args, **kwargs)

    KNOWN_TYPES = {}
    @classmethod
    def register_type(cls, user_type):
        type_name = user_type.__name__
        cls.KNOWN_TYPES[type_name] = user_type
        return user_type  # so it can be used as a decorator

    def decode_obj(self, o):
        if 'type' in o and o['type'] in self.KNOWN_TYPES:
            return self.KNOWN_TYPES[o['type']].from_json(o)
        return o



def dump(obj, fp):
    return json.dump(obj, fp, cls=JSONEncoder)


def load(fp):
    return json.load(fp, cls=JSONDecoder)
