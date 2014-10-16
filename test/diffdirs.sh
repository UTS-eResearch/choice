#!/bin/bash

# Compares the dat and orig files between two directories. 
# e.g. 
# ./mydiffs.sh check_mplusall_1 check_mplusall_2

# Need two args, assume they are directories.
if [ $# -ne 2 ]; then 
    echo 'needs two directory args'
    exit 1;
fi

dir1=$1 
dir2=$2

# Comparing input dat files
for i in $dir1/in_*.dat; do 
    j=`echo $i | sed s/$dir1/$dir2/` 
    diff $i $j
    if [ $? -ne 0 ]; then
        echo "$i  !=  $j" 
    fi
done

# Comparing output original files
for i in $dir1/*.orig; do 
    j=`echo $i | sed s/orig/dat/`
    diff $i $j
    if [ $? -ne 0 ]; then
        echo "$i  !=  $j" 
    fi
done

