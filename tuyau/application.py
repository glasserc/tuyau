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
        outgoing_by_machine = self.filter_by_machine(self.outgoing)

        connections = []
        for remote in self.config.remotes:
            connection = remote.connect()
            connection.hello(self)
            connections.append(connection)

        print(connections, file=sys.stderr)
        for connection in connections:
            incoming = connection.get_messages(self.name)
            self.process(incoming)

        for connection in connections:
            for machine, messages in outgoing_by_machine.iteritems():
                connection.send_messages(machine, messages)
            connection.close()
        self.outgoing.clear()

    def filter_by_machine(self, msgs):
        """Returns machine -> [msgs] according to its parameters"""
        outgoing_by_server = {}
        for msg in msgs:
            for machine, parameters in self.config.listeners.iteritems():
                for (cond, action) in parameters:
                    if cond.match(msg):
                        if machine not in outgoing_by_server:
                            outgoing_by_server[machine] = []
                        outgoing_by_server[machine].append(msg)
                        break

        return outgoing_by_server


    def fetch(self):
        """Get, but don't process, messages from all connections"""
        for remote in self.config.remotes:
            connection = remote.connect()
            connection.hello(self)
            self.incoming.extend(connection.get_messages(self.name))
        return self.incoming

    def process(self, messages):
        pass
