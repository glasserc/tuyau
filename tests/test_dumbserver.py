"""Test that two Tuyaus can communicate using DumbServers."""

import os.path
from tuyau import application
from tuyau.message import Document
from tuyau.config import Remote, Configuration as Config
from tuyau.conditions import Always
from tuyau.actions import LogWithLogging
from . import DocumentFuzzy

def test_dumb_server_1(couchurl, tmpdir):
    log = LogWithLogging('tuyau.test_dumbserver')
    r = Remote('server', Remote.DUMB, url='ssh://localhost/{}'.format(tmpdir))

    c = Config({'laptop': [r], 'desktop': [r]},
               {'desktop': [(Always(), log)]})

    a1 = application.Application('laptop', couchurl, c)
    a2 = application.Application('desktop', None, c)

    m1 = Document()
    a1.enqueue(m1)
    a1.sync()

    messages = a2.fetch()
    assert DocumentFuzzy.wrap_all(messages) == [m1]

def test_dumb_server_2(couchurl, tmpdir):
    r = Remote('server', Remote.DUMB, url='ssh://localhost/{}'.format(tmpdir))

    # Four instances, all communicating by dropping messages on a
    # dumb server. Messages should go to some but not all.
    log = LogWithLogging('tuyau.test_dumbserver')
    c = Config({'laptop': [r],
                 'desktop': [r],
                 'phone': [r],
                 'work_laptop': [r]},
                {'desktop': [(Always(), log)],
                 'phone': [(Always(), log)]})

    a1 = application.Application('laptop', couchurl, c)
    a2 = application.Application('desktop', None, c)
    a3 = application.Application('phone', None, c)
    a4 = application.Application('work_laptop', None, c)


    m1 = Document()
    a1.enqueue(m1)
    a1.sync()

    messages = a2.fetch()
    assert DocumentFuzzy.wrap_all(messages) == [m1]

    messages = a3.fetch()
    assert DocumentFuzzy.wrap_all(messages) == [m1]

    messages = a4.fetch()
    assert messages == []
