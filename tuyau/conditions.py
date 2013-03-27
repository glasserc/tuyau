"""
Conditions to be used in listeners lists
"""

class Condition(object):
    def match(self, document):
        return False

class Always(Condition):
    def match(self, document):
        return True

class Filter(Condition):
    def __init__(self, **kwargs):
        self.attributes = kwargs

    def match(self, document):
        for k, v in self.attributes.iteritems():
            if not hasattr(document, k):
                return False
            if getattr(kwargs, k) != v:
                return False

        return True
