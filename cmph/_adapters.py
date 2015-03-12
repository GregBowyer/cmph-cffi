from collections import Sequence
from ._utils import is_file
import logging
import six


logger = logging.getLogger(__name__)


class _PythonListAdapter(object):

    def __init__(self, data, encoding='utf8'):
        self.data = data
        self.cursor = 0
        self.current = None
        self.box = None
        self.warned = False
        self.encoding = encoding

    def read(self):
        if self.cursor < len(self.data):
            index = self.cursor
            self.cursor = index + 1
            element = self.data[index]

            if six.PY2:
                bstr = bytes(element.decode(self.encoding, errors='ignore'))
                self.current = bstr
            else:
                self.current = bytes(element.encode('utf8'))
            if not self.warned:
                if not isinstance(element, six.string_types):
                    logger.warn('CMPH expects strings, we will stringify '
                                'your type [%s], but this may not work '
                                '(example stringification "%s")',
                                type(element),
                                self.current.encode('unicode-escape'))
                    self.warned = True
        else:
            self.current = None
        return self.current

    def rewind(self):
        self.cursor = 0

    def destroy(self):
        pass


class _AdapterCxt(object):

    def __init__(self, adapter, destructor):
        self.adapter = adapter
        self.destructor = destructor

    def __enter__(self):
        return self.adapter

    def __exit__(self, *args):
        if self.destructor:
            self.destructor()


def _create_pyobj_adapter(cmph, ffi, obj):
    nkeys = len(obj)

    pySideAdapter = _PythonListAdapter(obj)

    @ffi.callback('char*()')
    def read_fn():
        cstr = pySideAdapter.read()
        if cstr is not None:
            pySideAdapter.box = ffi.new('char[]', cstr)
            return pySideAdapter.box
        else:
            return None

    @ffi.callback('cmph_uint32()')
    def keylen_fn():
        # It is important to tell C that the len might be 0
        # CMPH rather irritatingly does not always check the pointer
        # that comes back
        if pySideAdapter.current is not None:
            return ffi.sizeof('char') * (len(pySideAdapter.current))
        else:
            return 0

    @ffi.callback('void()')
    def rewind_fn():
        pySideAdapter.rewind()

    @ffi.callback('void()')
    def destroy_fn():
        pass

    # THIS IS VITAL - without this you are going to
    # accidently GC the callbacks and freak C out
    pySideAdapter.rd_cb = read_fn
    pySideAdapter.rw_cb = rewind_fn
    pySideAdapter.dt_cb = destroy_fn
    pySideAdapter.kl_cb = keylen_fn

    adapter = cmph.cmph_io_function_adapter(read_fn, rewind_fn,
                                            destroy_fn, keylen_fn,
                                            nkeys)
    dtor = lambda: cmph.cmph_io_function_adapter_destroy(adapter)
    return _AdapterCxt(adapter, dtor)


def create_adapter(cmph, ffi, obj):
    """ Generates a wrapped adapter for the given object

    Parameters
    ----------
    obj : list, buffer, array, or file like

    Raises
    ------
    ValueError
        If presented with an object that cannot be adapted

    Returns
    -------
    CMPH capable adapter
    """

    # if arraylike and fixed unit size
    # if file
    # if buffer

    if is_file(obj):
        # The FP is captured for GC reasons inside the dtor closure
        fp = open(obj)
        adapter = cmph.cmph_io_nlfile_adapter(fp)

        def dtor():
            cmph.cmph_io_nlfile_adapter_destroy(adapter)
            fp.close()
        return _AdapterCxt(adapter, dtor)
    elif hasattr(obj, 'fileno'):
        adapter = cmph.cmph_io_nlfile_adapter(obj)
        dtor = lambda: cmph.cmph_io_nlfile_adapter_destroy(adapter)
        return _AdapterCxt(adapter, dtor)
    elif isinstance(obj, Sequence):
        if len(obj) == 0:
            raise ValueError("An empty sequence is already a perfect hash!")
        return _create_pyobj_adapter(cmph, ffi, obj)
    else:
        raise ValueError("data cannot have a cmph wrapper generated")
