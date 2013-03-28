"""Test that two Tuyaus can communicate using DumbServers."""

import os.path
from mock import Mock
from tuyau import application
from tuyau.document import Document
from tuyau.config import Remote, Configuration as Config, GlobalConfig
from tuyau.conditions import Always
from tuyau.actions import LogWithLogging, SaveToMaildir
from . import TESTDIR

def test_always_log(tmpdir):
    log = Mock()
    c = GlobalConfig(desktop=Config([(Always(), log)]))

    a1 = application.Application('desktop', 'http://localhost:5984/tuyau', c)

    m1 = Document()
    a1.process([m1])

    log.assert_called_with(m1)

def test_save_maildir(couchurl, tmpdir):
    c = GlobalConfig(desktop=Config([(Always(), SaveToMaildir(str(tmpdir)))]))
    a1 = application.Application('desktop', 'http://localhost:5984/tuyau', c)

    m1 = Document()
    tmpdir.mkdir('INBOX').mkdir('cur')
    m1.folder = 'INBOX'
    m1.filename = '01:2,'
    m1.content = """From: test@test.local
Subject: Test message

This is my test.

"""
    a1.process([m1])

    created = tmpdir.join('INBOX/cur/01:2,')
    assert created.check()
    assert file(str(created)).read() == m1.content
