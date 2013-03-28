"""
Conditions to be used in listeners lists
"""

import json

class Condition(object):
    def match(self, document):
        return False

    def to_javascript(self):
        """Return a bit of code that will test true iff this condition would.

        This bit of JS code will refer to a variable called "doc"."""
        return ""


class Always(Condition):
    def match(self, document):
        return True

    def to_javascript(self):
        return "true"

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

    def to_javascript(self):
        js_conds = []
        for k, v in self.attributes.iteritems():
            cond = "doc['{}'] == {}".format(k, json.dumps(v))
            js_conds.append(cond)
        return "&&".join(map("({})".format, js_conds))
