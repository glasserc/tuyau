from __future__ import print_function
import sys
import collections

# To debug paramiko
import logging
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
#logger.setLevel(logging.DEBUG)

class Application(object):
    """Class for an instance of Tuyau"""

    def __init__(self, config):
        self.config = config
        self.name = config.name
        self.outgoing = collections.deque()
        self.incoming = []  # might need to be a priority queue or something?
        """Contains incoming messages that haven't been processed yet"""

    def enqueue(self, message):
        self.outgoing.append(message)

    def sync(self):
        connections = []
        for remote in self.config.remotes:
            connection = remote.connect()
            connection.hello(self)
            connections.append(connection)

        print(connections, file=sys.stderr)
        for connection in connections:
            incoming = connection.get_messages()
            self.process(incoming)

        for connection in connections:
            connection.send_messages(self.outgoing)
            connection.close()
        self.outgoing.clear()

    def fetch(self):
        """Get, but don't process, messages from all connections"""
        for remote in self.config.remotes:
            connection = remote.connect()
            connection.hello(self)
            self.incoming.extend(connection.get_messages())
        return self.incoming

    def process(self, messages):
        pass
