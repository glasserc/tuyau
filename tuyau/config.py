from __future__ import print_function
import sys
from . import connection

class Remote(object):
    """Configuration object representing places to exchange messages with"""

    DUMB = 'dumb'
    TUYAU = 'tuyau'
    MAPPING = {DUMB: connection.DumbServer,
               TUYAU: connection.SmartServer}

    def __init__(self, type):
        self.type = type

    def connect(self):
        conn = self.MAPPING[self.type](self)
        return conn

class Configuration(object):
    """Configuration object for an instance of Tuyau"""

    name = 'laptop'
    """Name for this instance to be referred to by other instances

    Typically this is the name of the machine."""

    remotes = []
    """Remotes to connect to"""
