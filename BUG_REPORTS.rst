Submitting bug reports
######################

The bridge between CMPH and python is via cffi, which despite its advantages
can break and throwup various failures.

We try to use random testing to ensure that this is not likely to happen, but
it can be hard to know for sure.

Naturally, if this library goes boom on you, it can be helpful to get a bug report,
this guide should explain how to get a good bug report.

If a test fails
---------------
When tests fail, please capture the following from the test suite

```
GLOB sdist-make: /home/greg/work/cmph-python/setup.py
py27 inst-nodeps: /home/greg/work/cmph-python/.tox/dist/cmph-cffi-0.2.0.zip
py27 runtests: PYTHONHASHSEED='3431726178'
```

This should let us reproduce test-case failures

If you get a core dump
----------------------
If you get a core-dump, you will need to do the following:

* In your terminal do `ulimit -c 0`
* please checkout a new copy of cmph-cffi and change the
  `DEBUG=False` statement in `cmph/__init__.py` to `True`
* Once you have a core-dump (should be a file called `core` locally), 
  run the following command from the cmph distro
  `./extract-backtrace.sh <core_file>`
* This should generate a file called backtrace, post this as a github issue
  and we will see if we can fixerate it.
