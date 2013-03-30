"""Test that two Tuyaus can communicate using DumbServers."""

import os.path
from tuyau import application
from tuyau.document import Document
from tuyau.config import Remote, Configuration as Config, GlobalConfig
from tuyau.conditions import Always, Filter
from tuyau.actions import LogWithLogging
from glob import glob
from . import DocumentFuzzy, DocumentFuzzy as DF, TESTDIR, \
    TestApplication as Application

def test_dumb_server_1(couchurl, tmpdir):
    log = LogWithLogging('tuyau.test_dumbserver')
    r = Remote('server', Remote.DUMB, url='ssh://localhost/{}'.format(tmpdir))

    c = GlobalConfig(global_remotes=[r],
                     laptop=Config(),
                     desktop=Config([(Always(), log)]))

    a1 = Application('laptop', couchurl)
    a1.save_config(c)
    a2 = Application('desktop', None, c)


    m1 = Document()
    a1.save(m1)
    a1.sync()

    documents = a2.fetch()
    no_config = DF.strip_configs(documents)
    assert no_config == [m1]
    assert len(documents) > len(no_config)

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

    a1 = Application('laptop', couchurl, insecure=True)
    a1.save_config(c)
    a2 = Application('desktop', None, c, insecure=True)
    a3 = Application('phone', None, c, insecure=True)
    a4 = Application('work_laptop', None, c, insecure=True)


    m1 = Document()
    a1.save(m1)
    a1.sync()

    documents = a2.fetch()
    configs2 = DF.only_configs(documents)
    assert DF.strip_configs(documents) == [m1]

    documents = a3.fetch()
    configs3 = DF.only_configs(documents)
    assert DF.strip_configs(documents) == [m1]

    documents = a4.fetch()
    configs4 = DF.only_configs(documents)
    assert DF.strip_configs(documents) == []

    assert configs2 == configs3
    assert configs3 == configs4

def test_many_sync(couchurl, tmpdir):
    r = Remote('server', Remote.DUMB, url='ssh://localhost/{}'.format(tmpdir))

    # Four instances, all communicating by dropping documents on a
    # dumb server. Documents should go to some but not all.
    log = LogWithLogging('tuyau.test_dumbserver')
    c = GlobalConfig(global_remotes=[r],
                     laptop=Config(),
                     desktop=Config([(Always(), log)]))

    a1 = Application('laptop', couchurl)
    a1.save_config(c)
    m1 = Document()
    a1.save(m1)
    a1.sync()

    a2 = Application('laptop', couchurl)
    m2 = Document()
    a2.save(m2)
    a2.sync()

    desktop = Application('desktop', couchurl)
    documents = desktop.fetch()
    assert DF.strip_configs(documents) == [m1, m2]


def test_shared_sync(couchurl, tmpdir):
    r = Remote('server', Remote.DUMB, url='ssh://localhost/{}'.format(tmpdir))

    # Four instances, all communicating by dropping documents on a
    # dumb server. Documents should go to some but not all.
    log = LogWithLogging('tuyau.test_dumbserver')
    c = GlobalConfig(global_remotes=[r],
                     laptop=Config(),
                     desktop=Config([(Always(), log)]))

    a1 = Application('laptop', couchurl)
    a1.save_config(c)
    m1 = Document()
    a1.save(m1)
    # a1 doesn't sync; a2 will sync both

    a2 = Application('laptop', couchurl)
    m2 = Document()
    a2.save(m2)
    a2.sync()

    desktop = Application('desktop', couchurl)
    documents = desktop.fetch()
    assert DF.strip_configs(documents) == [m1, m2]

def test_encryption(couchurl, tmpdir):
    test_keyring = os.path.join(TESTDIR, 'test_keyring')
    r = Remote('server', Remote.DUMB, url='ssh://localhost/{}'.format(tmpdir))
    log = LogWithLogging('tuyau.test_dumbserver')
    c = GlobalConfig(global_remotes=[r],
                     laptop=Config(),
                     desktop=Config([(Always(), log)],
                                    key_id='0487A9A8'))  # id from test keyring

    # N.B. don't use TestApplication here :)
    a1 = application.Application('laptop', couchurl, gpg_keyring=test_keyring)
    a1.save_config(c)
    d1 = Document()
    a1.save(d1)
    a1.sync()

    for filename in glob(str(tmpdir.join('documents-desktop-*'))):
        assert '_id' not in file(filename).read()  # should be gibberish

    a2 = application.Application('desktop', couchurl, gpg_keyring=test_keyring)
    documents = a2.fetch()
    assert DF.strip_configs(documents) == [d1]
