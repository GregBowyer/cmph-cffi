import logging
logging.basicConfig(level=logging.DEBUG)
import cmph
import os
import pytest
import six
import math
from cmph._utils import convert_to_bytes
from collections import Counter
from hypothesis import given, assume
from random import Random

_words = os.path.join(os.path.dirname(__file__), 'words')
_words8 = os.path.join(os.path.dirname(__file__), 'words8')
unicrud_type = str if six.PY3 else unicode


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


def test_str_input(tmpdir):
    data = 'This is a string list test'.split()
    mph = cmph.generate_hash(data)
    out = tmpdir.ensure('out.mph')

    with out.open('w') as test_output:
        mph.save(test_output)

    with out.open() as saved_mph:
        mph2 = cmph.load_hash(saved_mph)

    for word in data:
        assert mph(word) == mph2(word)


def test_str_input2(tmpdir):
    data = open(_words).readlines()
    mph = cmph.generate_hash(data)
    out = tmpdir.ensure('out.mph')

    with out.open('w') as test_output:
        mph.save(test_output)

    with out.open() as saved_mph:
        mph2 = cmph.load_hash(saved_mph)

    for word in data:
        assert mph(word) == mph2(word)


def test_filename_usage(tmpdir):
    mph = cmph.generate_hash(_words)
    out = tmpdir.ensure('out.mph')
    mph.save(out.strpath)

    mph2 = cmph.load_hash(out.strpath)

    with open(_words) as test_input:
        for word in test_input:
            assert mph(word) == mph2(word)


def _entropy(strs):
    p, lns = Counter(strs), float(len(strs))
    return -sum(x / lns * math.log(x) for x in p.values())


@given([unicrud_type])
def test_unicode_input(unicrud):
    unicrud = list(set(unicrud))
    assume(len(unicrud) > 5)

    # MPH is an entropy game, hence things with low-entropy will
    # confuse the hash algorithms preventing convergence on a
    # solution, making this test fail
    assume(_entropy(unicrud) == -0.0)

    mph = cmph.generate_hash(unicrud)

    # ... break the encapsulation, knowing that we
    # do this under the hood
    test_strs = [convert_to_bytes(s) for s in unicrud]
    for original, escaped in zip(unicrud, test_strs):
        assert mph(escaped) == mph(original)


@given(str)
def test_invalid_algo(algo):
    if algo in cmph._ALGOS:
        pytest.skip("Random algo is a known algo !")

    with pytest.raises(ValueError):
        test_data = _words
        with open(test_data) as test_input:
            cmph.generate_hash(test_input, algorithm=algo)


@given([str])
def test_invalid_hash_fn(hash_fns):
    assume(len(hash_fns) > 1)
    assume(any(fn not in cmph._HASH_FNS for fn in hash_fns))

    with pytest.raises(ValueError):
        test_data = _words
        with open(test_data) as test_input:
            cmph.generate_hash(test_input, hash_fns=hash_fns)
