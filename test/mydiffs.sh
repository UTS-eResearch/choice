#!/bin/bash

dir='Check_All2fis'
dir2='Construct_MainEffects1_b'

#for i in $dir/in_*.dat; do 
#    j=`echo $i | sed s/Construct_MainEffects1/Construct_MainEffects1_b/`
#    echo $i $j
#    diff $i $j
#done

dir='Construct_Some2fis'

for i in $dir/*_orig.dat; do 
    # out_bmat_orig.dat 
    j=`echo $i | sed s/_orig.dat/.orig/`
    mv $i $j
done
