import six
from hypothesis import given
from hypothesis.strategies import text
from cmph.utils import convert_to_bytes

unicrud_type = str if six.PY3 else unicode


@given(text())
def test_unicode_bytes(unicrud):
    assert unicrud_type(convert_to_bytes(unicrud), 'utf8') == unicrud
