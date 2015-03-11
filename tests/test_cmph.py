import logging
logging.basicConfig(level=logging.DEBUG)
import cmph
import os
import pytest

_words = os.path.join(os.path.dirname(__file__), 'words')
_words8 = os.path.join(os.path.dirname(__file__), 'words8')


def test_simple_usage(tmpdir):
    with open(_words) as test_input:
        mph = cmph.generate_hash(test_input)

    out = tmpdir.ensure('out.mph')

    with out.open('w') as test_output:
        mph.save(test_output)

    with out.open() as saved_mph:
        mph2 = cmph.load_hash(saved_mph)

    with open(_words) as test_input:
        for word in test_input:
            assert mph(word) == mph2(word)


@pytest.mark.parametrize('algo', cmph._ALGOS.keys())
def test_each_algo_defaults(tmpdir, algo):
    if algo == 'brz':
        pytest.skip("brz is known to segfault on some machines")

    test_data = _words
    if algo == 'bmz8':
        test_data = _words8

    with open(test_data) as test_input:
        mph = cmph.generate_hash(test_input, algorithm=algo)

    out = tmpdir.ensure('%s.mph' % algo)

    with out.open('w') as test_output:
        mph.save(test_output)

    with out.open() as saved_mph:
        mph2 = cmph.load_hash(saved_mph)

    with open(test_data) as test_input:
        for word in test_input:
            assert mph(word) == mph2(word)

    # Check that nothing untoward happens in __del__
    del mph
    del mph2