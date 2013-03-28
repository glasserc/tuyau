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

    def __init__(self, name, couchurl, global_config=None):
        """couchdb is the URL of the Couch DB specific to this instance.

        One of couchurl and global_config must be specified."""
        self.name = name
        self.global_config = global_config
        self.couch = None
        if couchurl:
            parsed = urlparse.urlsplit(couchurl)
            no_path = (parsed.scheme, parsed.netloc, '', '', '')
            couch = couchdb.Server(urlparse.urlunsplit(no_path))
            self.couch = couch[parsed.path.strip('/')]
        self.syncinfo_sent = {}
        """Remote -> {machine -> last_seq sent on that remote}

        Helps us from resending same documents on the same remote"""
        self.incoming = []

    def configuration(self, configuration):
        pass

    def save(self, document):
        if not self.couch:
            raise ValueError, "Cannot send a document on a non-couch instance"
        document.store(self.couch)

    def remotes(self):
        global_remotes = self.global_config.remotes
        local_remotes = self.global_config[self.name].remotes
        return global_remotes + local_remotes

    def sync(self):
        connections = []
        for remote in self.remotes():
            connection = remote.connect()
            connection.hello(self)
            connections.append(connection)

        for connection in connections:
            incoming = connection.get_documents(self.name)
            self.process(incoming)

        for connection in connections:
            for machine in self.global_config.iterkeys():
                documents = self.changes_for(connection.remote, machine)
                if documents:
                    connection.send_documents(machine, documents)
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
            doc = self.couch.get(id, attachments=True, revs=True)
            for cond, action in self.global_config[machine].listeners:
                if cond.match(doc):
                    docs.append(doc)
                    break
        return docs

    def fetch(self):
        """Get, but don't process, documents from all connections"""
        incoming = {}
        for remote in self.remotes():
            connection = remote.connect()
            connection.hello(self)
            self.incoming.extend(connection.get_documents(self.name))

        return self.incoming

    def process(self, documents):
        listeners = self.global_config[self.name].listeners
        if not listeners:
            return None
        for document in documents:
            for (cond, action) in listeners:
                if cond.match(document):
                    action(document)
