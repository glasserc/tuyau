"""Test that two Tuyaus can communicate using DumbServers."""

import os.path
from tuyau import application
from tuyau.document import Document
from tuyau.config import Remote, Configuration as Config, GlobalConfig
from tuyau.conditions import Always, Filter
from tuyau.actions import LogWithLogging
from . import DocumentFuzzy

def test_dumb_server_1(couchurl, tmpdir):
    log = LogWithLogging('tuyau.test_dumbserver')
    r = Remote('server', Remote.DUMB, url='ssh://localhost/{}'.format(tmpdir))

    c = GlobalConfig(global_remotes=[r],
                     laptop=Config(),
                     desktop=Config([(Always(), log)]))

    a1 = application.Application('laptop', couchurl, c)
    a2 = application.Application('desktop', None, c)

    m1 = Document()
    a1.save(m1)
    a1.sync()

    documents = a2.fetch()
    assert DocumentFuzzy.wrap_all(documents) == [m1]

def test_dumb_server_2(couchurl, tmpdir):
    r = Remote('server', Remote.DUMB, url='ssh://localhost/{}'.format(tmpdir))

    # Four instances, all communicating by dropping documents on a
    # dumb server. Documents should go to some but not all.
    log = LogWithLogging('tuyau.test_dumbserver')
    c = GlobalConfig(global_remotes=[r],
                     laptop=Config(),
                     desktop=Config([(Always(), log)]),
                     phone=Config([(Always(), log)]),
                     work_laptop=Config([(Filter(type='mail'), log)]))

    a1 = application.Application('laptop', couchurl, c)
    a2 = application.Application('desktop', None, c)
    a3 = application.Application('phone', None, c)
    a4 = application.Application('work_laptop', None, c)


    m1 = Document()
    a1.save(m1)
    a1.sync()

    documents = a2.fetch()
    assert DocumentFuzzy.wrap_all(documents) == [m1]

    documents = a3.fetch()
    assert DocumentFuzzy.wrap_all(documents) == [m1]

    documents = a4.fetch()
    assert documents == []
