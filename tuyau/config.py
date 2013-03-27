from __future__ import print_function
import sys
from . import connection

class Remote(object):
    """Configuration object representing places to exchange documents with"""

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

    remotes = {}
    """name -> [remotes]

    Remotes that the instance named "name" can connect to.

    Remotes can of course be instances themselves.

    Sometimes different machines connect to the same Remote in
    different ways -- different filesystem paths, or over SSH vs on a
    local filesystem. In this case, it's only necessary that the
    remotes have the same name."""

    listeners = {}
    """name -> [(condition, action)]

    If a document matches any condition, send it to the remote named
    "name". If we are "name" and a document matches a condition,
    perform the corresponding action."""

    def __init__(self, remotes=None, listeners=None):
        self.remotes = remotes
        self.listeners = listeners
