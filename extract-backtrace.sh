#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: extract-backtrace.sh <core>"
    exit 1
fi

export LIB=$(python -c 'from __future__ import print_function; import cmph; print(cmph._cmph._cffi_python_module.__file__)')

gdb --batch-silent                          \
    -ex 'set logging overwrite on'          \
    -ex 'set logging file backtrace'        \
    -ex 'set logging on'                    \
    -ex 'handle SIG33 pass nostop noprint'  \
    -ex "file $LIB"                         \
    -ex "core-file $1"                      \
    -ex 'set pagination 0'                  \
    -ex 'echo backtrace::\n'                \
    -ex 'backtrace full'                    \
    -ex 'echo \nregisters::\n'              \
    -ex 'info registers'                    \
    -ex 'echo \nprogram-counters::\n'       \
    -ex 'x/16i $pc'                         \
    -ex 'echo \nfull-backtrace::\n'         \
    -ex 'thread apply all backtrace'        \
    -ex 'quit'

