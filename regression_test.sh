#!/bin/bash

# Regession script to test process_choices.py
#
# Usage: ./this_script
# There are no arguments.
# 
# Version: 
# 2013.10.21 first version
# 2014.10.16 this script now handles all tests, changed to no output for success. 
 

# Set the top test directory containing all the test directories here.
# The individual test directories must be named like: 
#   [check|construct]_[main|mplussome|mplusall]_[0-9] and 
# must contain the correct data files.  
# e.g.:
#   construct_mplusall_1
#   construct_main_2
# There must be no other directories.
testdir='test' 


###########
# Functions
###########

# Show usage of this program.  
function usage {    
    echo "Usage: "
    echo "  $0                <-- this usage message"  
    echo "  $0 all            <-- run all tests, no output if all OK"  
    echo "  $0 clean          <-- cleans all test directories"  
    echo "  $0 list           <-- lists all test directories"  
    echo "  $0 test_directory <-- run test on this directory only, no output if all OK"  
    echo ""
}

# Remove all output files to start clean again.
function clean_all {
    # original files used to be called e.g. out_lmat_orig.dat 
    # files=`find $testdir -name out_*[!_orig].dat`

    files=`find $testdir -name out_*.dat`
    for file in $files; do
        #echo $file
        rm -f $file
    done

    # Also remove all choice temp directories
    rm -fr /tmp/choice.*
}


function get_parts {
    dir=$1
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
}


function get_operation_effects {
    
    tmp=`basename $1`
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
}


# Check the new output files match the original ones.
function test_one {
    dir=$1
    
    # The function get_operation_effects() will set $operation and $effects
    # from the $dir directory name.
    get_operation_effects $dir

    # Run the program, generating output files.
    time ./process_choices.py $dir $operation $effects 
  
    # Check the outputs against the originals. 
    for orig in $dir/out_*.orig ; do
        # % removes from $orig the shortest part of .orig that 
        # matches the end of $orig and replace it with .dat
        new="${orig%.orig}.dat"
        diff $orig $new
        if [ $? -ne 0 ]; then
            echo "Error above in test for $dir" 
            echo "File with error is `basename $new`"
            echo ''
        fi
    done
}


function test_all {
    # Find all directories which match *_*_*
    testdirs=`find $testdir -type d -name "c*_*_*"`
    
    # Loop through those directories ...
    for dir in $testdirs; do
        echo -en "\n------ $dir ------"
        test_one $dir
    done
}


function test_list {
    # Find all directories which match *_*_*
    testdirs=`find $testdir -type d -name "c*_*_*"`
    
    echo
    # Loop through those directories ...
    for dir in $testdirs; do
        echo '  ' $dir
    done 
    echo
}


##############
# Start script
##############
    
# If no args then show usage. 
if [ $# -ne 1 ]; then 
    usage 
    exit 1;
fi

# If here then there is just one arg. 

if [ $1 == 'all' ]; then 
    test_all 
    exit 0;
fi

if [ $1 == 'clean' ]; then
    echo "Cleaning all test directories ..."
    clean_all 
    exit 0;
fi

if [ $1 == 'list' ]; then
    echo "Listing all test directories ..."
    test_list 
    exit 0;
fi

# If here then we test the one specified directory given by arg1
if [ -d $1 ]; then
    test_one $1
else
    echo "$1 is not an existing test directory"
    echo "Run: $0 list "
fi

