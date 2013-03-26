"""
Conditions to be used in listeners lists
"""

class Condition(object):
    def match(self, message):
        return False

class Always(Condition):
    def match(self, message):
        return True
