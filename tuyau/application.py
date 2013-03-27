from __future__ import print_function
import sys
import collections
import couchdb
import urlparse

# To debug paramiko
import logging
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
#logger.setLevel(logging.DEBUG)

class Application(object):
    """Class for an instance of Tuyau"""

    def __init__(self, name, couchurl, config=None):
        """couchdb is the URL of the Couch DB specific to this instance.

        One of couchurl and config must be specified."""
        self.name = name
        self.config = config
        self.couch = None
        if couchurl:
            parsed = urlparse.urlsplit(couchurl)
            no_path = (parsed.scheme, parsed.netloc, '', '', '')
            couch = couchdb.Server(urlparse.urlunsplit(no_path))
            self.couch = couch[parsed.path.strip('/')]
        self.syncinfo_sent = {}
        """Remote -> {machine -> last_seq sent on that remote}

        Helps us from resending same messages on the same remote"""
        self.incoming = []

    def enqueue(self, message):
        if not self.couch:
            raise ValueError, "Cannot send a message on a non-couch instance"
        message.store(self.couch)

    def sync(self):
        connections = []
        for remote in self.config.remotes[self.name]:
            connection = remote.connect()
            connection.hello(self)
            connections.append(connection)

        for connection in connections:
            incoming = connection.get_messages(self.name)
            self.process(incoming)

        for connection in connections:
            for machine in self.config.listeners.iterkeys():
                messages = self.changes_for(connection.remote, machine)
                if messages:
                    connection.send_messages(machine, messages)
            connection.close()

    def changes_for(self, remote, machine):
        changes_args = dict(style='all_docs')
        last_sent_dict = self.syncinfo_sent.setdefault(remote, {})
        last_sent = last_sent_dict.get(machine, None)
        if last_sent:
            changes_args['since'] = last_sent
        changes = self.couch.changes(**changes_args)
        self.syncinfo_sent[remote][machine] = changes['last_seq']
        docs = []
        for change in changes['results']:
            id = change['id']
            docs.append(self.couch.get(id, attachments=True, revs=True))
        return docs

    def fetch(self):
        """Get, but don't process, messages from all connections"""
        incoming = {}
        for remote in self.config.remotes[self.name]:
            connection = remote.connect()
            connection.hello(self)
            self.incoming.extend(connection.get_messages(self.name))

        return self.incoming

    def process(self, messages):
        if self.name not in self.config.listeners:
            return None
        listeners = self.config.listeners[self.name]
        for message in messages:
            for (cond, action) in listeners:
                if cond.match(message):
                    action(message)
