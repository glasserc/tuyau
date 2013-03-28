"""Test that two Tuyaus can communicate using DumbServers."""

import os.path
from mock import Mock
from tuyau import application
from tuyau.document import Document
from tuyau.config import Remote, Configuration as Config, GlobalConfig
from tuyau.conditions import Always
from tuyau.actions import LogWithLogging
from . import TESTDIR

def test_always_log(tmpdir):
    r = Remote('server', Remote.DUMB, url='ssh://localhost/{}'.format(tmpdir))

    log = Mock()
    c = GlobalConfig(global_remotes=[r],
                     desktop=Config([(Always(), log)]))

    a1 = application.Application('desktop', 'http://localhost:5984/tuyau', c)

    m1 = Document()
    a1.process([m1])

    log.assert_called_with(m1)
