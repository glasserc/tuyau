class Connection(object):
    """Class to represent a connection to another Tuyau instance."""

    def __init__(self, application):
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
    def get_messages(self):
        pass

    def send_messages(self, msgs):
        pass
