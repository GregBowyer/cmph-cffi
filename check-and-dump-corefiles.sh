#!/bin/bash

for i in $(find ./ -maxdepth 1 -name 'core*' -print); do 
    ./extract-backtrace.sh $i
    cat backtrace
done
