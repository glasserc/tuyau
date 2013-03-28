from __future__ import print_function
import sys
from . import connection
from .conditions import Condition
from .actions import Action

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

    def to_json(self):
        return self.__dict__

class Configuration(object):
    """Configuration object for an instance of Tuyau"""

    def __init__(self, listeners=None, remotes=None):
        self.remotes = remotes or []
        """[remotes]

        Remotes specific to the instance named "name".

        Remotes can of course be instances themselves.

        Sometimes different machines connect to the same Remote in
        different ways -- different filesystem paths, or over SSH vs
        on a local filesystem. In this case, it's only necessary that
        the remotes have the same name."""


        self.listeners = listeners or []
        """[(condition, action)]

        If a document matches any condition, send it to the remote
        named "name". If we are "name" and a document matches a
        condition, perform the corresponding action."""

    @classmethod
    def from_json(cls, doc):
        doc.pop('type')
        remotes = [Remote(**remote) for remote in doc['remotes']]
        listeners = []
        for (cond, act) in doc['listeners']:
            cond = Condition.from_json(cond)
            act = Action.from_json(act)
            listeners.append((cond, act))

        return cls(remotes=remotes, listeners=listeners)

    def to_json(self):
        conds_stanza = ''
        if self.listeners:
            conds_js = [c.to_javascript() for (c, a) in self.listeners]
            conds_stanza = 'if({}) return true;'.format('||'.join(conds_js))
            # Always interested in config and deleted
        interested = """function(doc, req) {{
  if(doc._deleted || doc.type == "Config") return true;
  {}
  return false;
}}""".format(conds_stanza)

        return {'remotes': [r.to_json() for r in self.remotes],
                'listeners': [(c.to_json(), a.to_json())
                              for (c, a) in self.listeners],
                'filters': {
                'interested': interested,
                },
                'type': 'Config'}

class GlobalConfig(object):

    def __init__(self, global_remotes=None, **instances):
        self.remotes = global_remotes or []
        """Global remotes"""

        self.instances = instances

    def __getitem__(self, item):
        return self.instances[item]

    def iterkeys(self):
        return self.instances.iterkeys()

    def to_json(self):
        return {'remotes': [r.to_json() for r in self.remotes],
                'nodes': self.instances.keys(),
                'type': 'Config'}
