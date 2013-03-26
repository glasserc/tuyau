"""
Actions to be used as callbacks
"""

class Action(object):
    def __call__(self, msg):
        pass

class Log(Action):
    pass
