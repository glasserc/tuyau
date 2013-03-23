from . import connection

class Remote(object):
    """Configuration object representing places to exchange messages with"""

    DUMB = 'dumb'
    TUYAU = 'tuyau'
    MAPPING = {DUMB: connection.DumbServer,
               TUYAU: connection.SmartServer}

    def __init__(self, type):
        pass

    def connect(self):
        return self.MAPPING[self.type](self)

class Configuration(object):
    """Configuration object for an instance of Tuyau"""

    name = 'laptop'
    """Name for this instance to be referred to by other instances

    Typically this is the name of the machine."""

    remotes = []
    """Remotes to connect to"""
