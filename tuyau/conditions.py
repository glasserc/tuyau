"""
Conditions to be used in listeners lists
"""

class Condition(object):
    def match(self, document):
        return False

class Always(Condition):
    def match(self, document):
        return True
