import pytest
from _pytest.monkeypatch import monkeypatch
import py
import couchdb

class CouchFixture(object):
    """A port of tmpdir to CouchDB"""
    def mktemp(self, name, numbered=True):
        server = couchdb.Server('http://localhost:5984')
        return self.make_numbered_db('pytest-', server)


    def make_numbered_db(self, prefix, server, keep=10):
        def parse_num(dbname):
            """Parse the number out of a DB name"""
            if dbname.startswith(prefix):
                try:
                    return int(dbname[len(prefix):])
                except ValueError:
                    pass

        maxnum = -1
        for dbname in server:
            num = parse_num(dbname)
            if num is not None:
                maxnum = max(maxnum, num)
        ret_dbname = prefix+str(maxnum+1)
        ret_db = server.create(ret_dbname)

        for dbname in server:
            num = parse_num(dbname)
            if num is not None and num <= (maxnum - keep):
                server.delete(dbname)

        return ret_dbname

    def finish(self):
        pass

def pytest_configure(config):
    mp = monkeypatch()
    c = CouchFixture()
    config._cleanup.extend([mp.undo, c.finish])
    mp.setattr(config, '_couchfixture', c, raising=False)

@pytest.fixture()
def couch(request):
    name = request.node.name
    name = py.std.re.sub("[\W]", "_", name)
    x = request.config._couchfixture.mktemp(name, numbered=True)
    return couchdb.Server('http://localhost:5984')[x]

@pytest.fixture()
def couchurl(request):
    name = request.node.name
    name = py.std.re.sub("[\W]", "_", name)
    x = request.config._couchfixture.mktemp(name, numbered=True)
    return 'http://localhost:5984/'+x
