"""Test that two Tuyaus can communicate using DumbServers."""

import os.path
from tuyau import application
from tuyau.message import Message
from tuyau.config import Remote, Configuration as Config
from tuyau.conditions import Always
from tuyau.actions import Log
from . import TESTDIR

def test_dumb_server_1(tmpdir):
    r1 = Remote('desktop', Remote.DUMB, url='ssh://localhost/{}'.format(tmpdir))

    c1 = Config('laptop', [r1], {'desktop': [(Always(), Log())]})
    a1 = application.Application(c1)

    r2 = Remote('laptop', Remote.DUMB, url='ssh://localhost/{}'.format(tmpdir))
    c2 = Config('desktop', [r2])
    a2 = application.Application(c2)

    m1 = Message()
    m1.x = 3
    a1.enqueue(m1)
    a1.sync()

    messages = a2.fetch()
    assert messages == [m1]

def test_dumb_server_2(tmpdir):
    r1 = Remote('server', Remote.DUMB, url='ssh://localhost/{}'.format(tmpdir))

    # Four instances, all communicating by dropping messages on a
    # dumb server. Messages should go to two but not three.
    c1 = Config('laptop', [r1], {'desktop': [(Always(), Log())],
                                 'phone': [(Always(), Log())]})
    a1 = application.Application(c1)

    c2 = Config('desktop', [r1])
    a2 = application.Application(c2)

    c3 = Config('phone', [r1])
    a3 = application.Application(c3)

    c4 = Config('work_laptop', [r1])
    a4 = application.Application(c4)


    m1 = Message()
    m1.x = 3
    a1.enqueue(m1)
    a1.sync()

    messages = a2.fetch()
    assert messages == [m1]

    messages = a3.fetch()
    assert messages == [m1]

    messages = a4.fetch()
    assert messages == []
