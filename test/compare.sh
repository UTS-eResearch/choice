#!/bin/bash

for i in check_mplusall_1/*; do 
    # diff exit status is 0 if inputs are the same.
    diff $i `echo $i | sed s/_1/_2/`
    if [ $? -ne 0 ]; then
        echo $i
    fi
done

