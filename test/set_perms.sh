#!/bin/bash

# Set all input files to read-only.
find . -name "in_*.dat" | xargs chmod ugo-w 

# Set all originals of output files to read-only.
find . -name "out_*.orig" | xargs chmod ugo-w 



