from __future__ import print_function
import sys
import time
import uuid
import os.path
import json
import paramiko
import urlparse

class Connection(object):
    """Class to represent a connection to another Tuyau instance."""

    def __init__(self, remote):
        self.remote = remote

    def hello(self, application):
        self.application = application

    def get_documents(self, name):
        """Gets documents for this instance"""
        raise NotImplementedError

    def send_documents(self, for_name, msgs):
        raise NotImplementedError

class DumbServer(Connection):
    """Class to represent a connection to a server not running tuyau locally

    Communication with a DumbServer is typically done by dropping
    blocks of documents in a file in a directory via SSH.
    """
    def __init__(self, remote):
        super(DumbServer, self).__init__(remote)
        parsed = urlparse.urlparse(remote.url)

        connectargs = {}
        netloc = parsed.hostname
        if parsed.port:
            connectargs['port'] = parsed.port
        if parsed.username:
            connectargs['username'] = parsed.username

        keys_file = os.path.join(os.path.expanduser('~'), '.ssh/known_hosts')

        sshclient = paramiko.SSHClient()
        sshclient.load_host_keys(keys_file)
        sshclient.connect(parsed.netloc, **connectargs)
        self.sshclient = sshclient
        self.pmconnection = pmconnection = sshclient.open_sftp()
        self.pmconnection.chdir(parsed.path)

    def __del__(self):
        self.close()

    def close(self):
        self.sshclient.close()
        self.pmconnection.close()

    def get_documents(self, name):
        incoming = []
        for filename in self.pmconnection.listdir('.'):
            if filename.startswith('documents-{}-'.format(name)):
                lfile = self.pmconnection.file(filename)
                if self.application.gpg:
                    decrypted = self.application.gpg.decrypt_file(lfile)
                    block = json.loads(decrypted.data)
                else:
                    block = json.load(lfile)
                incoming.extend(block)
                lfile.close()
                self.pmconnection.unlink(filename)

        return incoming

    def send_documents(self, for_name, msgs):
        blockname = 'documents-{}-{}'.format(for_name, uuid.uuid4())
        block = self.pmconnection.file(blockname, 'w')

        if self.application.gpg:
            keyid = self.application.global_config[for_name].key_id
            encrypted = self.application.gpg.encrypt(json.dumps(list(msgs)),
                                                     keyid,
                                                     armor=False)
            block.write(encrypted.data)
        else:
            json.dump(list(msgs), block)
        block.close()

class SmartServer(Connection):
    """Class to represent a connection to another instance of Tuyau"""
    pass
