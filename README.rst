*********************************
CFFI bindings to the CMPH library
*********************************

These bindings provide python with the ability to create and use 
`Minimal Perfect Hashes`_ via the CMPH_ library.

-----

|pypi| |build| |coverage| |lint|

-----


============
Installation
============

Should be as simple as 

.. code-block:: bash
    
    $ pip install cmph-cffi


-------------------
Development version
-------------------

The **latest development version** can be installed directly from GitHub:

.. code-block:: bash

    $ pip install --upgrade 'git+https://github.com/URXtech/cmph-cffi'


=====
Usage
=====

Creating a new MPH

.. code-block:: python

    import cmph
    with open('/usr/share/dict/words', 'w') as keys:
        mph = cmph.generate_hash(keys)

Getting keys out of an MPH

.. code-block:: python

    mph('Test')

.. warning:: Be aware that whilst MPH's are awesome, they typically cannot
   distinguish between keys they are built on and unseen keys. Concretely this
   means that feeding in keys that are not in the original key set will have
   **undefined results**

Saving the MPH

.. code-block:: python

    with open('/tmp/out.mph', 'w') as out_file:
        mph.save(out_file)

Loading a pre-existing MPH

.. code-block:: python

    with open('/tmp/out.mph') as in_file:
        cmph.load_hash(in_file)

=======
Authors
=======


`Greg Bowyer`_ (`@GregBowyer`_) and `Venkatesh Sharma`_ (`@Venkateshks`_)
created these bindings and `these fine people`_ did all the hard implementation
work in CMPH_.


==============
Reporting bugs
==============
Please see `BUG_REPORTS <https://github.com/URXtech/cmph-cffi/blob/master/BUG_REPORTS.rst>`_.


==========
Contribute
==========

Please see `CONTRIBUTING <https://github.com/URXtech/cmph-cffi/blob/master/CONTRIBUTING.rst>`_.


=======
Licence
=======

Please see `LICENSE <https://github.com/URXtech/cmph-cffi/blob/master/LICENSE>`_.


.. _Minimal Perfect Hashes: http://en.wikipedia.org/wiki/Perfect_hash_function#Minimal_perfect_hash_function
.. _CMPH: http://cmph.sourceforge.net/
.. _these fine people: http://sourceforge.net/p/cmph/git/ci/master/tree/AUTHORS
.. _Greg Bowyer: http://bonsaichicken.org
.. _Venkatesh Sharma: https://github.com/venkateshks
.. _@venkateshks: https://github.com/venkateshks
.. _@GregBowyer: https://github.com/GregBowyer

.. |pypi| image:: https://img.shields.io/pypi/v/cmph-cffi.svg?style=flat-square&label=latest%20version
    :target: https://pypi.python.org/pypi/cmph-cffi
    :alt: Latest version released on PyPi

.. |build| image:: https://img.shields.io/travis/URXtech/cmph-cffi/master.svg?style=flat-square&label=build
    :target: http://travis-ci.org/URXtech/cmph-cffi
    :alt: Build status 

.. |coverage| image:: https://img.shields.io/codecov/c/github/URXtech/cmph-cffi.svg
    :target: https://codecov.io/github/URXtech/cmph-cffi
    :alt: Coverage

.. |lint| image:: https://landscape.io/github/URXtech/cmph-cffi/master/landscape.svg?style=flat-square
   :target: https://landscape.io/github/URXtech/cmph-cffi/master
   :alt: Code Health
