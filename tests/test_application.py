
from . import TestApplication as Application
from tuyau.config import Remote, Configuration, GlobalConfig
from tuyau.actions import LogWithLogging
from tuyau.conditions import Always

def test_application(couchurl):
    """Test that save/load config works"""
    a1 = Application('laptop', couchurl)
    r1 = Remote('server', Remote.DUMB, url='ssh://localhost/blah')
    log = LogWithLogging('tuyau.test_application')
    gc = GlobalConfig(global_remotes = [r1],
                      laptop=Configuration(),
                      desktop=Configuration([(Always(), log)]))

    a1.save_config(gc)

    a2 = Application('laptop', couchurl)
    assert a2.global_config.to_json() == gc.to_json()
    desktop_listeners = a2.global_config['desktop'].listeners
    assert isinstance(desktop_listeners[0][0], Always)
    assert isinstance(desktop_listeners[0][1], LogWithLogging)
    assert log.logger == desktop_listeners[0][1].logger
