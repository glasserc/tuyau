import collections

class Application(object):
    """Class for an instance of Tuyau"""

    def __init__(self, config):
        self.config = config
        self.name = config.name
        self.outgoing = collections.deque()

    def enqueue(self, message):
        self.outgoing.append(message)

    def sync(self):
        pass

    def fetch(self):
        return []
