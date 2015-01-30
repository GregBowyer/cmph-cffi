__all__ = ['MPH', 'generate_hash', 'load_hash']

from cffi import FFI
from os.path import dirname
from os.path import join as pthjoin
from os.path import relpath
from glob import glob
from collections import Iterable
import logging

ffi = FFI()

ffi.cdef("""
    typedef ... FILE;

    typedef char cmph_int8;
    typedef unsigned char cmph_uint8;

    typedef short cmph_int16;
    typedef unsigned short cmph_uint16;

    typedef int cmph_int32;
    typedef unsigned int cmph_uint32;

    typedef ... cmph_t;
    typedef ... cmph_io_adapter_t;
    typedef ... cmph_config_t;

    typedef enum { CMPH_HASH_JENKINS, CMPH_HASH_COUNT } CMPH_HASH;
    typedef enum { CMPH_BMZ, CMPH_BMZ8, CMPH_CHM, CMPH_BRZ, CMPH_FCH,
               CMPH_BDZ, CMPH_BDZ_PH,
               CMPH_CHD_PH, CMPH_CHD, CMPH_COUNT } CMPH_ALGO;

    cmph_io_adapter_t *cmph_io_nlfile_adapter(FILE * keys_fd);
    void cmph_io_nlfile_adapter_destroy(cmph_io_adapter_t * key_source);
    cmph_io_adapter_t *cmph_io_nlnkfile_adapter(FILE * keys_fd,
                                                cmph_uint32 nkeys);
    void cmph_io_nlnkfile_adapter_destroy(cmph_io_adapter_t * key_source);
    cmph_io_adapter_t *cmph_io_vector_adapter(char ** vector,
                                              cmph_uint32 nkeys);
    void cmph_io_vector_adapter_destroy(cmph_io_adapter_t * key_source);
    cmph_io_adapter_t *cmph_io_byte_vector_adapter(cmph_uint8 ** vector,
                                                   cmph_uint32 nkeys);
    void cmph_io_byte_vector_adapter_destroy(cmph_io_adapter_t * key_source);
    cmph_io_adapter_t *cmph_io_struct_vector_adapter(void * vector,
                                                 cmph_uint32 struct_size,
                                                 cmph_uint32 key_offset,
                                                 cmph_uint32 key_len,
                                                 cmph_uint32 nkeys);
    void cmph_io_struct_vector_adapter_destroy(cmph_io_adapter_t * key_source);

    cmph_config_t *cmph_config_new(cmph_io_adapter_t *key_source);
    void cmph_config_set_hashfuncs(cmph_config_t *mph, CMPH_HASH *hashfuncs);
    void cmph_config_set_verbosity(cmph_config_t *mph, cmph_uint32 verbosity);
    void cmph_config_set_graphsize(cmph_config_t *mph, double c);
    void cmph_config_set_algo(cmph_config_t *mph, CMPH_ALGO algo);
    void cmph_config_set_tmp_dir(cmph_config_t *mph, cmph_uint8 *tmp_dir);
    void cmph_config_set_mphf_fd(cmph_config_t *mph, FILE *mphf_fd);
    void cmph_config_set_b(cmph_config_t *mph, cmph_uint32 b);
    void cmph_config_set_keys_per_bin(cmph_config_t *mph,
                                      cmph_uint32 keys_per_bin);
    void cmph_config_set_memory_availability(cmph_config_t *mph,
                                             cmph_uint32 memory_availability);
    void cmph_config_destroy(cmph_config_t *mph);

    cmph_t *cmph_new(cmph_config_t *mph);
    void cmph_destroy(cmph_t *mphf);

    int cmph_dump(cmph_t *mphf, FILE *f);
    cmph_t *cmph_load(FILE *f);

    cmph_uint32 cmph_search(cmph_t *mphf, const char *key, cmph_uint32 keylen);
""")
ffi.C = ffi.dlopen(None)

path = dirname(__file__)
sources = [relpath(src) for src in
           glob(pthjoin(path, '*.c'))]

_cmph = ffi.verify('''
#include <cmph.h>
''', sources=sources, include_dirs=[path])

_HASH_FNS = {
    'jenkins': _cmph.CMPH_HASH_JENKINS,
    'count': _cmph.CMPH_HASH_COUNT
}

_ALGOS = {
    'bmz': _cmph.CMPH_BMZ,
    'bmz8': _cmph.CMPH_BMZ8,
    'chm': _cmph.CMPH_CHM,
    'brz': _cmph.CMPH_BRZ,
    'fch': _cmph.CMPH_FCH,
    'bdz': _cmph.CMPH_BDZ,
    'bdz_ph': _cmph.CMPH_BDZ_PH,
    'chd_ph': _cmph.CMPH_CHD_PH,
    'chd': _cmph.CMPH_CHD,
}


class MPH(object):
    """ Wrapper class that maintains a Minimal Perfect Hash (MPH)

    There are many ways to use an MPH, typically given a pre-constructed
    MPH, you make lookups on the MPH to get the relevant hashcode for
    a given key.

    Construction is typically done via the `generate_hash` method like so

    >>> some_keys = xrange(100)
    >>> mph = generate_hash(some_keys)

    Lookups on the hash can be performed with either directly as a functor, or
    via the `lookup` method

    >>> mph(10)
    >>> mph.lookup(10)

    MPH hashes can also be saved to disk like so

    >>> with open('hashcodes.mph', 'w') as mph_file:
    ...     mph.save(mph_file)

    These same MPH objects can be reloaded via the `load_hash` method

    >>> with open('hashcodes.mph') as mph_file:
    ...     mph = load_hash(mph_file)

    **Note** The data stored by MPH is, in theory compatible with that of
    any file using the underlying CMPH library. However please be aware that
    differences in objects between use cases can result in issues.
    """

    def __init__(self, mph):
        self._mph = mph

    def save(self, output):
        """ Persist the Minimal Perfect Hash (MPH) to a stream

        Parameters
        ----------
        output : file_like
            The stream to use to persist the MPH

        Raises
        ------
        IOError
            If there is an issue accessing or manipulating the underlying
            stream
        """
        assert self._mph, "There is no MPH ?"
        _cmph.cmph_dump(self._mph, output)

    def lookup(self, key):
        """Generate hash code for a key from the Minimal Perfect Hash (MPH)

        Parameters
        ----------
        Key : object
            The item to generate a key for, this works best for keys that
            are strings, or can be transformed fairly directly into bytes

        Returns : int
            The code for the given item

        """
        return _cmph.cmph_search(self._mph, key, len(key))

    def __call__(self, key):
        """Generate hash code for a key from the Minimal Perfect Hash (MPH)

        Parameters
        ----------
        Key : object
            The item to generate a key for

        Returns : int
            The code for the given item

        """
        return self.lookup(key)

    def __del__(self):
        _cmph.cmph_destroy(self._mph)


def _range_check(name, lower, value, upper=None):
    if upper:
        if not (lower <= value <= upper):
            raise ValueError("Invalid parameter for %s" % name)
    else:
        if not (lower <= value):
            raise ValueError("Invalid parameter for %s" % name)


def generate_hash(input, algorithm='chd_ph', hash_fns=[], chd_keys_per_bin=1,
                  chd_load_factor=None, fch_bits_per_key=None,
                  num_graph_vertices=None, brz_memory_size=8,
                  brz_temp_dir=None, brz_max_keys_per_bucket=128,
                  bdz_precomputed_rank=7, chd_avg_keys_per_bucket=4):
    """
    Generates a new Minimal Perfect Hash (MPH)

    Parameters
    ----------
    input : Iterable
        The input that is used to generate the minimal perfect hash.

        Be aware, in most cases the input is expected to be distinct, and
        many of the algorithms benefit from the input being sorted.

    algorithm : string, optional
        {chd_ph (default), chd, bmz, bmz8, chm, brz, fch, bdz, bdz_ph}
        The algorithm to use in generating MPH's, choice of:

        chd / chd_ph - Compress Hash and Displace (default)
            (http://cmph.sourceforge.net/chd.html)
            - It is the fastest algorithm to build PHFs and MPHFs in linear
            time.
            - It generates the most compact PHFs and MPHFs we know of.
            - It can generate PHFs with a load factor up to 99 %.
            - It can be used to generate t-perfect hash functions. A
            t-perfect hash function allows at most t collisions in a given
            bin. It is a well-known fact that modern memories are
            organized as blocks which constitute transfer unit. Example of
            such blocks are cache lines for internal memory or sectors for
            hard disks. Thus, it can be very useful for devices that
            carry out I/O operations in blocks.
            - It is a two level scheme. It uses a first level hash function
            to split the key set in buckets of average size determined by
            a parameter b in the range [1,32]. In the second level it uses
            displacement values to resolve the collisions that have given
            rise to the buckets.
            - It can generate MPHFs that can be stored in approximately 2.07
            bits per key.
            - For a load factor equal to the maximum one that is achieved by
            the BDZ algorithm (81 %), the resulting PHFs are stored in
            approximately 1.40 bits per key.

        bdz - BDZ / BPZ algorithm
            (http://cmph.sourceforge.net/bdz.html)
            - It is very simple and efficient. It outperforms all others
            except CHD.
            - It constructs both PHFs and MPHFs in linear time.
            - The maximum load factor one can achieve for a PHF is 1/1.23.
            - It is based on acyclic random 3-graphs. A 3-graph is a
            generalization of a graph where each edge connects 3 vertices
            instead of only 2.
            - The resulting MPHFs are not order preserving.
            - The resulting MPHFs can be stored in only (2 + x)cn bits,
            where c should be larger than or equal to 1.23 and x is a
            constant larger than 0 (actually, x = 1/b and b is a parameter
            that should be larger than 2). For c = 1.23 and b = 8, the
            resulting functions are stored in approximately 2.6 bits per
            key.
            - For its maximum load factor (81 %), the resulting PHFs are
            stored in approximately 1.95 bits per key.

        bmz - Botelho, Menoti and Ziviani algorithm:
            (http://cmph.sourceforge.net/bdz.html)
            - Constructs MPHFs in linear time.
            - It is based on cyclic random graphs. This makes it faster than
            the CHM algorithm.
            - The resulting MPHFs are not order preserving.
            - The resulting MPHFs are more compact than the ones generated by
            the CHM algorithm and can be stored in 4cn bytes, where c is in
            the range [0.93,1.15].

        brz - BRZ algorithm:
            (http://cmph.sourceforge.net/brz.html)
            - A very fast external memory based algorithm for constructing
            minimal perfect hash functions for sets in the order of
            billions of keys.
            - It works in linear time.
            - The resulting MPHFs are not order preserving.
            - The resulting MPHFs can be stored using less than 8.0 bits per
            key.

        chm - Czech, Havas and Majewski algorithm:
            (http://cmph.sourceforge.net/chm.html)
            - Construct minimal MPHFs in linear time.
            - It is based on acyclic random graphs
            - The resulting MPHFs are order preserving.
            - The resulting MPHFs are stored in 4cn bytes, where c is greater
            than 2.

        fch - Fox, Chen and Heath algorithm:
            (http://cmph.sourceforge.net/chm.html)
            - Construct minimal perfect hash functions that require less than
            4 bits per key to be stored.
            - The resulting MPHFs are very compact and very efficient at
            evaluation time
            - The algorithm is only efficient for small sets.
            - It is used as internal algorithm in the BRZ algorithm to
            efficiently solve larger problems and even so to generate MPHFs
            that require approximately 4.1 bits per key to be stored. For
            that, you just need to set the parameters -a to brz and -c to a
            value larger than or equal to 2.6.

    hash_fns : list {jenkins (default), count} optional
        Internal hash functions to use inside MPH generation functions,
        can be multiple fns as a list.

    chd_keys_per_bin : int [1 to 128], optional
        Set the number of keys per bin for a t-perfect hashing function. A
        t-perfect hash function allows at most t collisions in a given bin.
        This parameter applies only to the `chd` and `chd_ph` algorithms.
        Its value should be an integer in the range [1, 128].

        Default is 1

    chd_load_factor : float, optional
        The load factor used in the `chd_ph` algorithm

    fch_bits_per_key : int, optional
        The number of bits per key required in the FCH algorithm

    num_graph_vertices : int, optional
        The number of vertices in the graph for the algorithms BMZ and CHM

    brz_memory_size : int (default 8), optional
        Main memory availability (in MB) used in BRZ algorithm

        Default is 8Mb

    brz_temp_dir : string, optional
        Temporary directory used in BRZ algorithm

    brz_max_keys_per_bucket : int [64 to 175] (default 128), optional
        Used to make the maximal number of keys in a bucket lower than 256.
        In this case its value should be an integer in the range [64,175].
        Default is 128.

    bdz_precomputed_rank : int [3 to 10] (default 7), optional
        For BDZ it is used to determine the size of some precomputed rank
        information and its value should be an integer in the range [3,10].

        Default is 7.

        The larger is this value, the more compact are the resulting
        functions and the slower are them at evaluation time.

    chd_avg_keys_per_bucket : int [1 to 32] (default 4), optional
        For CHD and CHD_PH it is used to set the average number of keys per
        bucket and its value should be an integer in the range [1,32].

        Default is 4.

        The larger is this value, the slower is the construction of the
        functions.

    Returns
    -------
    MPH
        A wrapper object that represents a minimal perfect hash in memory

    Raises
    ------
    ValueError
        If arguments presented are incomplete, or incompatable
    RuntimeError
        If the MPH generation fails
    """

    algorithm = algorithm.lower()

    if algorithm.lower() not in _ALGOS.keys():
        raise ValueError("Invalid algorithm")

    if hash_fns:
        hash_fns = [fn.lower() for fn in hash_fns]
        if any(fn not in _HASH_FNS.keys() for fn in hash_fns):
            raise ValueError("Invalid internal hash fn")

    _range_check('chd_keys_per_bin', 1, chd_keys_per_bin, 128)
    _range_check('brz_memory_size', 1, brz_memory_size)
    _range_check('brz_max_keys_per_bucket', 64,
                 brz_max_keys_per_bucket, 175)
    _range_check('bdz_precomputed_rank', 3,
                 bdz_precomputed_rank, 10)
    _range_check('chd_avg_keys_per_bucket', 1,
                 chd_avg_keys_per_bucket, 32)

    _is_nlfile = False
    if hasattr(input, 'fileno'):
        source = _cmph.cmph_io_nlfile_adapter(input)
        _is_nlfile = True
    elif isinstance(input, Iterable):
        raise NotImplementedError("EEP")

    config = _cmph.cmph_config_new(source)
    _cmph.cmph_config_set_algo(config, _ALGOS[algorithm])

    #_cmph.cmph_config_set_mphf_fd(config, mphf_fd)

    if algorithm in ('chd', 'chd_ph'):
        if chd_load_factor is not None:
            _range_check('chd_load_factor', 0, chd_load_factor)
            _cmph._cmph_set_graphsize(config, chd_load_factor)
        _cmph.cmph_config_set_keys_per_bin(config, chd_keys_per_bin)
        _cmph.cmph_config_set_b(config, chd_avg_keys_per_bucket)
        if num_graph_vertices:
            _cmph.cmph_set_graphsize(config, num_graph_vertices)
    elif algorithm == 'bdz':
        _cmph.cmph_config_set_b(config, bdz_precomputed_rank)
    elif algorithm == 'brz':
        _cmph.cmph_config_set_b(config, brz_max_keys_per_bucket)
        if not brz_temp_dir:
            brz_temp_dir = tempfile.mkdtemp(suffix='cmph')
        _cmph.cmph_set_tmp_dir(config, brz_temp_dir)
        _cmph.cmph_set_memory_availability(config, brz_memory_size)
    elif algorithm == 'bmz':
        if num_graph_vertices:
            _range_check('num_graph_vertices', 1, num_graph_vertices)
            if num_graph_vertices >= 2.0:
                logging.warn("num_graph_vertices for bmz was given "
                             "as >= 2, but forced to 1.15")
                num_graph_vertices = 1.15
            _cmph.cmph_set_graphsize(config, num_graph_vertices)
    elif algorithm == 'chm':
        if num_graph_vertices is not None:
            _range_check('num_graph_vertices', 1, num_graph_vertices)
            _cmph.cmph_set_graphsize(config, num_graph_vertices)
    elif algorithm == 'fch':
        if fch_bits_per_key:
            _range_check('fch_bits_per_key', 0, fch_bits_per_key)
            _cmph.cmph_set_graphsize(config, fch_bits_per_key)

    try:
        return MPH(_cmph.cmph_new(config))
    except Exception as e:
        raise e
    finally:
        _cmph.cmph_config_destroy(config)

        if _is_nlfile:
            _cmph.cmph_io_nlfile_adapter_destroy(source)


def load_hash(input):
    """Load a Minimal Perfect Hash (MPH)
    Given an input stream, this will load a minimal perfect hash

    Parameters
    ----------
    input : file_like
        An input stream that is file like, and able to load
        a preexisting MPH

    Raises
    ------
    IOError
        If there is an issue accessing or manipulating the underlying
        stream

    Returns
    -------
    MPH
        A MPH wrapper class
    """
    assert hasattr(input, 'fileno'), "Input is not a file ?"
    _mph = _cmph.cmph_load(input)
    return MPH(_mph)
