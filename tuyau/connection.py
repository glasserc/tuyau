from __future__ import print_function
import sys
import time
import uuid
import os.path
from . import json_wrapper
import paramiko
import urlparse

class Connection(object):
    """Class to represent a connection to another Tuyau instance."""

    def __init__(self, remote):
        pass

    def hello(self, application):
        self.application = application

    def get_messages(self):
        """Gets messages for this instance"""
        raise NotImplementedError

    def send_messages(self, msgs):
        raise NotImplementedError

class DumbServer(Connection):
    """Class to represent a connection to a server not running tuyau locally

    Communication with a DumbServer is typically done by dropping
    blocks of messages in a file in a directory via SSH.
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

    def get_messages(self):
        incoming = []
        for filename in self.pmconnection.listdir('.'):
            if filename.startswith('messages-'):
                block = self.pmconnection.file(filename)
                incoming.extend(json_wrapper.load(block))
                block.close()

        return incoming

    def send_messages(self, msgs):
        blockname = 'messages-{}'.format(uuid.uuid4())
        block = self.pmconnection.file(blockname, 'w')
        json_wrapper.dump(list(msgs), block)
        block.close()

class SmartServer(Connection):
    """Class to represent a connection to another instance of Tuyau"""
    pass
