from __future__ import print_function
import sys
import collections
import couchdb
import urlparse

from tuyau.config import Remote, GlobalConfig, Configuration

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

        if not global_config:
            self.load_config()

        self.incoming = []


    def load_config(self):
        gc_doc = self.couch.get('_design/tuyau-global', None)
        if not gc_doc:
            return   # hope that someone configures us soon

        global_remotes = []
        for remote in gc_doc['remotes']:
            global_remotes.append(Remote(**remote))

        instance_map = {}
        for instance in gc_doc['nodes']:
            instance_doc = self.couch.get('_design/tuyau-{}'.format(instance), None)
            if not instance_doc:
                continue   # I guess??
            instance_map[instance] = Configuration.from_json(instance_doc)

        self.global_config = GlobalConfig(global_remotes=global_remotes,
                                          **instance_map)


    def save_config(self, global_config):
        self.global_config = global_config
        for instance in global_config.iterkeys():
            idict = global_config[instance].to_json()
            self.couch['_design/tuyau-{}'.format(instance)] = idict

        self.couch['_design/tuyau-global'] = global_config.to_json()

    def save(self, document):
        if not self.couch:
            raise ValueError, "Cannot send a document on a non-couch instance"
        document.store(self.couch)

    def remotes(self):
        if not self.global_config:
            raise ValueError, "unconfigured instance"
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
        changes_args = dict(style='all_docs',
                            filter='tuyau-{}/interested'.format(machine))
        last_sent_key = '_local/tuyau-sync-{}'.format(machine)
        if last_sent_key not in self.couch:
            self.couch[last_sent_key] = {}
        last_sent_dict = self.couch[last_sent_key]
        last_sent = last_sent_dict.get(remote.name, None)
        if last_sent:
            changes_args['since'] = last_sent
        changes = self.couch.changes(**changes_args)
        last_sent_dict[remote.name] = changes['last_seq']
        self.couch[last_sent_key] = last_sent_dict
        docs = []
        for change in changes['results']:
            id = change['id']
            doc = self.couch.get(id, attachments=True, revs=True)
            docs.append(doc)
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
                    action(document, self.couch)
