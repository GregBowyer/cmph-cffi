import six
from os.path import abspath, exists


def is_file(obj):
    return isinstance(obj, six.string_types) and exists(abspath(obj))
