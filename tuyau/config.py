from __future__ import print_function
import sys
from . import connection

class Remote(object):
    """Configuration object representing places to exchange messages with"""

    DUMB = 'dumb'
    TUYAU = 'tuyau'
    MAPPING = {DUMB: connection.DumbServer,
               TUYAU: connection.SmartServer}

    def __init__(self, name, type, url=None):
        self.name = name
        self.type = type
        self.url = url

    def connect(self):
        conn = self.MAPPING[self.type](self)
        return conn

class Configuration(object):
    """Configuration object for an instance of Tuyau"""

    name = 'laptop'
    """Name for this instance to be referred to by other instances

    Typically this is the name of the machine."""

    remotes = []
    """Remotes to connect to from this instance"""

    listeners = {}
    """name -> [(condition, action)]

    If a message matches any condition, send it to the remote named
    "name". If we are "name" and a message matches a condition,
    perform the corresponding action."""

    def __init__(self, name=None, remotes=None, listeners=None):
        self.name = name
        self.remotes = remotes
        self.listeners = listeners
