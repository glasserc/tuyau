"""
Unit tests for condition
"""

from tuyau import conditions

def test_condition():
    f = conditions.Filter(type="mail")
    f_js = f.to_javascript()
    assert f_js.strip('()') == "doc['type'] == \"mail\""

    f2 = conditions.Filter(type="mail", folder="Inbox")
    f2_js = f2.to_javascript()
    # No need to implement a full JS parser to verify the form..
    # let's just look for some keywords
    assert 'type' in f2_js
    assert 'mail' in f2_js
    assert 'Inbox' in f2_js
