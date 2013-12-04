#!/bin/bash

# Version: 
# 2013.09.30 first version
# 2013.10.08 loop through .orig instead of .dat files
# 2013.10.23 

testdir='test' 

###########
# Functions
###########

# Show usage of this program.  
function usage {    
    echo "Usage: $0 <directory name> check|clean"  
    echo "Enter a directory name as an argument followed by either check|clean."
}


# Check the new output files match the original ones.
function check {
    for orig in $dir/out_*.orig ; do
        # % removes from $orig the shortest part of .orig that 
        # matches the end of $orig and replace it with .dat
        new="${orig%.orig}.dat"
        diff $orig $new
        #result=$(diff $orig $new)
        if [ $? -ne 0 ]; then
            echo "  ERROR is above for <-- " `basename $new`
            echo ''
        fi
    done
}


# Remove all output files to start clean again.
function clean {
    for file in $dir/out_*.dat ; do
        echo ' ' `basename $file`
        rm -f $file
    done

    # Also remove all choice temp directories
    rm -fr /tmp/choice.*
}


function clean_all {
    # original files used to be called e.g. out_lmat_orig.dat 
    # files=`find $testdir -name out_*[!_orig].dat`

    files=`find $testdir -name out_*.dat`
    for file in $files; do
        echo $file
        rm -f $file
    done

    # Also remove all choice temp directories
    rm -fr /tmp/choice.*
}



#########################
# Main script starts here
#########################

# Check number of args is two & first arg is a directory.
if [ $# -lt 2 ]; then 
    usage 
    exit 1;
fi

if [ ! -d $1 ]; then
    usage
    echo "$1 is not a directory"
    exit 1;
fi


# OK user has entered a directory name.
dir=$1

if [ $2 == 'check' ]; then
    #echo "  checking ... $dir"
    check $dir
elif [ $2 == 'clean' ]; then
    #echo "  cleaning ... $dir"
    #clean $dir
    clean_all 
else
    echo "Usage: $0 <directory name> check|clean"
    echo "$2 is neither check nor clean"
fi


