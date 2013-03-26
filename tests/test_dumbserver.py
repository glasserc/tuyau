"""Test that two Tuyaus can communicate using DumbServers."""

import os.path
from tuyau import application
from tuyau.message import Message
from tuyau.config import Remote, Configuration as Config
from . import TESTDIR

TESTNAME = 'dumb_server'

def test_dumb_server_1(tmpdir):
    r = Remote(Remote.DUMB)
    r.url = 'ssh://localhost/{}'.format(tmpdir)

    c1 = Config()
    c1.name = 'laptop'
    c1.remotes = [r]

    a1 = application.Application(c1)

    c2 = Config()
    c2.name = 'desktop'
    c2.remotes = [r]
    a2 = application.Application(c2)

    m1 = Message()
    m1.x = 3
    a1.enqueue(m1)
    a1.sync()

    messages = a2.fetch()
    assert messages == [m1]
