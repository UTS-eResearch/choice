#!/bin/bash

# This tarballs up the code to send to the client i.e. Emily Bird 
# or Deborah Street's student that will be working on the code. 

# Todays date
today=`date +%Y.%m.%d`

# Tarball just the code for the client and the test directory.
tar cvf choice_to_emily_$today.tar choice.py choice_common.py process_choices.py test

