"""Test that two Tuyaus can communicate using DumbServers."""

import os.path
from mock import Mock
from tuyau import application
from tuyau.message import Message
from tuyau.config import Remote, Configuration as Config
from tuyau.conditions import Always
from tuyau.actions import LogWithLogging
from . import TESTDIR

def test_always_log(tmpdir):
    r = Remote('server', Remote.DUMB, url='ssh://localhost/{}'.format(tmpdir))

    log = Mock()
    c = Config({'laptop': [r], 'desktop': [r]},
               {'desktop': [(Always(), log)]})

    a1 = application.Application('desktop', c)

    m1 = Message()
    a1.process([m1])

    log.assert_called_with(m1)
