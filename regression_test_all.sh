#!/bin/bash

# Regession script to test process_choices.py
#
# Usage: ./this_script
# There are no arguments.
# 
# Version: 
# 2013.10.21 first version

# The main test directory. This must contain directories of data and 
# they must be named [check|construct]_[main|mplussome|mplusall]_[0-9]
# e.g.:
#   construct_mplusall_1
#   construct_main_2
# There must be no other directories.

testdir='test' 

# Find all directories which match *_*_*
testdirs=`find $testdir -type d -name "c*_*_*"`

# Loop through those directories ...
for dir in $testdirs; do
    tmp=`basename $dir`
    # Split into parts separated by _.
    parts=(${tmp//_/ })

    # Quick check that there are three parts to the directory name.
    # ${#name[@]} is the number of elements in the array. 
    length=${#parts[@]}   
    if [ $length -ne 3 ]; then
        echo "Incorrect directory name $dir ($length)"
        exit 1
    fi
    # Debugging 
    #echo $dir
    #echo ${parts[0]} ${parts[1]} ${parts[2]}
    operation=${parts[0]} 
    effects=${parts[1]} 

    # Run the program.
    echo 'Running' $dir $operation $effects 
    ./process_choices.py $dir $operation $effects 
    ./regression_test.sh $dir check

done


