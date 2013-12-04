#!/usr/bin/env python

'''
This python script is a command line program to check or construct choices 
in a choice experiment. It reads input from text files and writes it output 
to text files. This way it can be easily invoked by other programs such as 
a cgi script. 

Usage: see the usage() function.

Versions: 
2013.08.16: First version by Emily Bird
2013.08.30: MRL rearranged and tidied up; added lots of comments;
            tabs to spaces; shortened long lines; removed del statements; 
            moved open files to top; rearranged code into funcs.
2013.09.02: MRL changed program name, added main code to handle program options, 
            move calcs to a function. Renamed test files to be more inituitive.
2013.09.03: Added dummy functions for calcs to be implemented later. Removed choose2fi
            as variables were confusing.
2013.10.03: Added temp directory to args. Changed Cinv to cinv in filename. Read in 
            files based on expected variables. 
            Imported power from numpy as power() was undefined. 
            Note there is an inbuilt pow() - could that be used?
2013.10.04: Removed outputcode and out_code.dat. 
2013.10.08: Functions that calculate choice sets no longer write files, pass in
            a dict of input vars and return a dict of output vars. Renamed matc to cmat 
            and matlam to lmat. Release to Nectar.
2013.10.09: Moved functions common to choice.py & process_choices.py to a module. 
2013.10.10: Added return values to unimplemented functions. Release to Nectar.
2013.10.11: Added Emily Bird's new functions. Renamed in_dets.dat to in_det.dat
            Fixed lots of indentation errors.
2013.10.23: Release to Nectar.
2013.10.24: Removed 'from numpy import power'. Removed os.chdir('test/ConstructMainEffects')
2013.10.29: Release to Nectar.
2013.10.30: Changed format of 'in_twofis.dat'. Added check for reading in_det.dat file.
            Added check for False returns from inputs.keys(). 
2013.11.15: Release to Nectar.
2013.11.18: Added code to check for fraction input in det. Release to Nectar.
2013.11.21: Added maximum time to run for. Release to Nectar.
2013.11.27: Fixed code errors with detString. Release to Nectar.


Details
-------

The web interface is done by another program. It will show these options:

    () Check your own choice sets OR
    () Construct choice sets 
    AND
    () Main effects OR
    () Main effects + all two-factor interactions OR
    () Main effects + some two-factor interactions 

This program just reads text files written by the web program as its data input 
and outputs new text files as data output. 

Description of all input files:

    Check               Construct  
    -----               ---------
    in_factors.dat      in_factors.dat  <-- (k) calculated from the length of 'levels'
    in_levels.dat       in_levels.dat   e.g. 4 3 3 3
    in_msize.dat        in_msize.dat    e.g. 2
    in_chsets.dat       ---  
    ---                 in_tmts.dat     e.g. 4 x 16 matrix
    ---                 in_gens.dat     e.g. 3 2 2 2
    
    and 

    If Main effects     If Main effects + all 2FI   If Main effects + some 2FI
    ------------        ----------------------      -----------------------
    ---                 in_det.dat [Optional!]      in_det.dat [Optional!]
    ---                 ---                         in_twofis.dat e.g. 1,2 1,3 

    in_msg.dat -- This file which contains text messages from the web program 
    and destined for the user's browser. This file can be appended to by this
    program. 

Description of all output files:

    Output files are the nearly same for all input options except:
      if "Construct Sets" then there is "out_chsets.dat", 
      if "Check Sets" then there is no "out_chsets.dat".

    out_chsets.dat      Choice sets         <--- only if "Construct Sets"
    out_bmat.dat        Contrast matrix B
    out_cinv.dat        Variance-Covariance matrix C^-1
    out_chsets.dat      Choice sets
    out_correln.dat     Correlation matrix
    out_cmat.dat        Information matrix C
    out_lmat.dat        Lambda matrix
    out_msg.dat         Output messages for the user's browser.

'''

import os, re, sys
import numpy as np
import itertools
import sympy
from sympy.matrices import *
from datetime import datetime, timedelta
#from time import sleep  # add e.g. sleep(3) for testing

# Our own modules
from choice_common import get_expected_io, write_errors


##################
# Global variables 
##################

global START, MAX_TIME 
START = datetime.now()
MAX_TIME = 10           # Maximum time in seconds to run for.


###################
# Classes / methods
###################

class myComb(object):
    '''
    A class to do component-wise modulo addition on an array where
    the mod value is determined by the levels of each factor.
    '''
    def __init__(self, val, nmod):
        super(myComb,self).__init__()
        self.val = tuple(val)
        self.nmod = tuple(nmod)
    
    def __add__(self, other):
        l = []
        for item1, item2, item3 in zip(self.val, other.val, self.nmod):
            l.append((item1 + item2)%int(item3))
        return tuple(l)
    
    def __lt__(self, other):
        return self.val < other.val
    
    def __gt__(self, other):
        return self.val > other.val
    
    def __eq__(self, other):
        return self.val == other.val
           
    def __str__(self):
        return str(self.val)
    
    def __repr__(self):
        return str(self.val) #+ ' modulo ' + str(self.nmod)


###################
# General functions 
###################


def usage ():
    print ''
    print 'Usage: %s <input_dir> <check|construct> <main|mplusall|mplussome>' % sys.argv[0]
    print '  input_dir               <-- a directory of data input files'
    print '  check|construct         <-- select one of these two options'
    print '  main|mplusall|mplussome <-- select one of these three options '
    print ''


def read_input_files(input_dir, expected_input):
    '''
    expected_input is a list of the input variables that we expect. For each expected 
    variable we look for a file named "in_variable.dat" and read this file. 
    Most of the input files have different formats; some are integers, some are 
    matrices, some are lists of numbers. There names are based on the variable names 
    i.e. 'factors', 'levels', 'msize', 'chsets', 'tmts', 'gens', 'det', 'twofis'
    
    TODO MRL This old version (processchoice.py) had a check that the user-inputted 
             value of k (number of factors) equals the length of levels. 
             It appears this check has been removed? 
    The output dictionary will be the string inputs converted to the required output 
    types so inputs['det'] will be a int or float or exponent, inputs['twofis'] will
    be a list of integers etc. 
    '''

    inputs = {}  # We will be returning this dictionary.

    # factors should be a single integer
    if 'factors' in expected_input:
        fh = open('in_factors.dat')
        contents = fh.read()
        fh.close()
        try:
            factors = int(contents)
        except ValueError as e: 
            write_errors('Reading in_factors.dat: %s\n' % e)
            factors = False

        inputs['factors'] = factors    

    # levels read in as string e.g. '4 3 3 3' & converted to list of ints.
    if 'levels' in expected_input:
        fh = open('in_levels.dat')
        levelsString = fh.read()
        fh.close()
        try:
            levels = [int(i) for i in levelsString.split()]
        except ValueError as e:
            levels = False
            write_errors('Reading in_levels.dat: %s\n' % e)

        inputs['levels'] = levels

    # choice set size (m) read in as a string, it's a single integer e.g. 2
    if 'msize' in expected_input:
        fh = open('in_msize.dat')
        cssString = fh.read()
        fh.close()
        try:
            choicesetsize = int(cssString)
        except ValueError as e:
            choicesetsize = False
            write_errors('Reading in_msize.dat: %s\n' % e)

        inputs['msize'] = choicesetsize

    # tmts matrix read in and converted to a list of tuples.
    if 'tmts' in expected_input:
        # MRL version is here, uses two list comprehensions and split() 
        tmts = []
        fh = open('in_tmts.dat')
        lines = fh.readlines()
        fh.close()
        try:
            tmts = [[int(char) for char in line.split()] for line in lines]
        except ValueError as e:
            write_errors('Reading in_tmts.dat: %s\n' % e)
            tmts = False 

        inputs['tmts'] = tmts

    # generators read in and converted to list of tuples.
    if 'gens' in expected_input:
        generators = []
        fh = open('in_gens.dat')
        lines = fh.readlines()
        fh.close()
        try:
            gens = [[int(char) for char in line.split()] for line in lines]
        except ValueError as e:
            write_errors('Reading in_gens.dat: %s\n' % e)
            gens = False 

        inputs['gens'] = gens

    # chsets for checking your own sets 
    if 'chsets' in expected_input:
        fh = open('in_chsets.dat')
        lines = fh.readlines()
        fh.close()
        try:
            chsets = [[int(char) for char in line.split()] for line in lines]
        except ValueError as e:
            write_errors('Reading in_chsets.dat: %s\n' % e)
            gens = False 

        inputs['chsets'] = chsets

    # det
    if 'det' in expected_input:
        # This is a little different from the above. The det is optional 
        # so there might be no input file. If it exists it will contain either nothing 
        # or blanks or a string that should be able to be cast into a float. 
        # That is: '' or '  ' or '0' or '1' or '0.12' or '1/3' or '0.1/2.3' or 
        # or 1.35738e-12. We also check if it's in the range (0,1).

        # We start off with False and override if a valid numerical value for
        # the det is found. 
        detString_is_OK = False
 
        # Note: In the tests below We set detString to None because later we
        # cast to a float and a float(False) = 0.0 which we don't want.
        try: 
            fh = open('in_det.dat')
            detString = fh.read()
            fh.close()
        except IOError as e:
            # TODO I still have to check what happens if in_det.dat can't be read.
            # detString & detString_is_OK remain as initial values as above.
            write_errors('Reading in_det.dat, got IOError: %s\n' % e)
            detString = None
       
        # At this point detString will be either None or whatever was in the
        # file if successfully read. 
 
        # Here we try a float cast which returns a float if the string is 
        # '1' or '0.2' or even '1.2e-12' ! so exponents are handled fine. 
        if not detString_is_OK:
            try:
                optdet = float(detString)
                detString_is_OK = True
            except:
                # It's not 0, 1 or exponent, still might be '' or ' ' or a fraction.
                pass

        # Here we try a fraction  
        if not detString_is_OK:
            try:
                (numerator, denominator) = detString.split('/')
                # Here we are just trying to see if we don't get an exception.
                optdet = float(numerator)/float(denominator)
                detString_is_OK = True
            except:
                # It's not a fraction, still might be  '' or ' '.
                pass 
       
        # Here we try a blank or nothing.  
        if not detString_is_OK:
            pat = re.compile('\s*$') # will match just nothing or only whitespace
            if re.match(pat, detString):
                # Matches nothing or only whitespace. 
                optdet = None
                detString_is_OK = True

        # If det is still not OK then detString remains as None.
        if not detString_is_OK:
            write_errors('Setting determinant of C to default value = None\n')
            optdet = None

        # At this stage optdet should be a valid numerical value or None.
        # Here we do a final check that it's in range(0,1), if not set to None.
        if optdet<0 or optdet>1:
            optdet = None
 
        inputs['det'] = optdet

    # twofis - Note TODO check are integers <= k
    if 'twofis' in expected_input:
        fh = open('in_twofis.dat')
        line = fh.read()
        fh.close()
        twofis = []
        try:
            for factor in line.split():
                # '1,2' --> ['1,2'] and '1,2 3,4' --> ['1,2', '3,4']
                temp = [int(char) for char in factor.split(',')] 
                twofis.append(temp)
        except ValueError as e:
            write_errors('Reading in_twofis.dat: %s\n' % e)
            twofis = False 

        inputs['twofis'] = twofis

    # Return a dict of all the vars with their values filled in.
    return inputs


def write_output_files(outputs):
    '''
    Takes a dictionary of output data and writes a file for each key, 
    the file contents being the value for that key.
    '''
    for key in outputs.keys():
        filename = 'out_' + key + '.dat'
        fh = open(filename, 'w')
        fh.write(outputs[key])
        fh.close()


def lexico(mat):
    ''' Sorts the rows of a matrix lexicographically. '''
    mat = np.matrix(mat) # ensure the variable is a numpy matrix
    numCols = mat.shape[1]
    # transpose the matrix and reverse the order of the columns (now rows)
    transReverseColumns = [mat.T[-i] for i in range(-numCols+1, 1)] 
    ind = np.lexsort(transReverseColumns) # determine the order
    return mat[ind][0] 


def unique(mat):
    ''' Returns the unique rows of a matrix, sorted lexicographically. '''
    if np.shape(mat)[0] > 1: # only do work if there is more than one row
        mat = np.matrix(mat) # ensure the variable is a numpy matrix
        mat = lexico(mat) # sort lexicographically
        diff = np.diff(mat, axis=0).tolist() # compare each row to the one above
        ind = [0] # list of indicies to keep
        for i in range(len(diff)):
            # check that each row has at least one component different to the row above
            if all([item==0 for item in diff[i]]) == False: 
                ind.append(i+1) 
        return mat[ind]
    else:
        return mat


def is_integer(s):
    
    ''' Returns 'True' if value, s, is integer. 
    MRL: One can also use this:
        import numbers
        isinstance(some_number, numbers.Integral)
    '''
    try:
        int(s)
        return True
    except ValueError:
        return False


def lcm(values):
    ''' Returns Lowest Common Multiple of a list. '''
    values = set([abs(int(v)) for v in values])
    if values and 0 not in values:
        n = n0 = max(values)
        values.remove(n)
        while any( [n % m for m in values] ):
            n += n0
        return n
    else:
        return 0


def construct_poly_contrasts():
    ''' Construct the othogonal polynomial contrasts. '''
    orthogpolys = []
    orthogpolys.append(np.matrix([-1, 1]).reshape(1, 2))
    orthogpolys.append(np.matrix([-1, 0, 1, 1, -2, 1]).reshape(2, 3))
    orthogpolys.append(np.matrix([-3, -1, 1, 3, 1, -1, -1, 1, -1, 3, -3, 1]).reshape(3, 4))
    orthogpolys.append(np.matrix([-2, -1, 0, 1, 2, 2, -1, -2, -1, 2, -1, 2, 0, -2, 1, 1, -4, 6, -4, 1]).reshape(4, 5))
    orthogpolys.append(np.matrix([-5, -3, -1, 1, 3, 5, 5, -1, -4, -4, -1, 5, -5, 7, 4, -4, -7, 5, 1, -3, 2, 2, -3, 1, -1, 5, -10, 10, -5, 1]).reshape(5, 6))
    orthogpolys.append(np.matrix([-3, -2, -1, 0, 1, 2, 3, 5, 0, -3, -4, -3, 0, 5, -1, 1, 1, 0, -1, -1, 1, 3, -7, 1, 6, 1, -7, 3, -1, 4, -5, 0, 5, -4, 1, 1, -6, 15, -20, 15, -6, 1]).reshape(6, 7))
    orthogpolys.append(np.matrix([-7, -5, -3, -1, 1, 3, 5, 7, 7, 1, -3, -5, -5, -3, 1, 7, -7, 5, 7, 3, -3, -7, -5, 7, 7, -13, -3, 9, 9, -3, -13, 7, -7, 23, -17, -15, 15, 17, -23, 7, 1, -5, 9, -5, -5, 9, -5, 1, -1, 7, -21, 35, -35, 21, -7, 1]).reshape(7, 8))
    orthogpolys.append(np.matrix([-4, -3, -2, -1, 0, 1, 2, 3, 4, 28, 7, -8, -17, -20, -17, -8, 7, 28, -14, 7, 13, 9, 0, -9, -13, -7, 14, 14, -21, -11, 9, 18, 9, -11, -21, 14, -4, 11, -4, -9, 0, 9, 4, -11, 4, 4, -17, 22, 1, -20, 1, 22, -17, 4, -1, 6, -14, 14, 0, -14, 14, -6, 1, 1, -8, 28, -56, 70, -56, 28, -8, 1]).reshape(8, 9))
    orthogpolys.append(np.matrix([-9, -7, -5, -3, -1, 1, 3, 5, 7, 9, 6, 2, -1, -3, -4, -4, -3, -1, 2, 6, -42, 14, 35, 31, 12, -12, -31, -35, -14, 42, 18, -22, -17, 3, 18, 18, 3, -17, -22, 18, -6, 14, -1, -11, -6, 6, 11, 1, -14, 6, 3, -11, 10, 6, -8, -8, 6, 10, -11, 3, -9, 47, -86, 42, 56, -56, -42, 86, -47, 9, 1, -7, 20, -28, 14, 14, -28, 20, -7,1, -1, 9, -36, 84, -126, 126, -84, 36, -9, 1]).reshape(9, 10))

    return orthogpolys


#########################################
# Here are the main calculation functions
#########################################

def CheckSets_MainEffects(inputs):
    '''
    inputs:  a dictionary of all input variables, in this case: 
             levels, msize, chsets
    outputs: a dictionary of all output variables, in this case: 
             msg, bmat, lmat, cmat, cinv, correln
    '''
    
    levels = inputs['levels']
    choicesetsize = inputs['msize']
    choicesets = inputs['chsets']
    optdet = 1  # optimal det
    
    # Create formatted outputs vars as a dictionary.
    outputs = {}
    
    # The text of this message string will be printed to the browser 
    msg = '' 
    
    # calculate a few little bits and pieces
    p = len(choicesets) # the number of choice sets
    factors = len(levels) # number of factors
    numME = sum([lvl - 1 for lvl in levels]) # number of main effect parameters
    numInts = 0 # number of interactions
    num2FI = 0 # number of 2fi parameters
    numEffects = numME + num2FI; # total number of parameters 
    
    # Construct the othogonal polynomial contrasts.
    orthogpolys = construct_poly_contrasts()
    
    # check that each choiceset is made up of unique tmts
    for i in range(len(choicesets)): # loop through each choice set
        if len(unique(np.matrix(choicesets[i]).reshape(choicesetsize, factors))) != choicesetsize:
            msg += 'Repeated treatment combination in choice set %d.\n' % (i+1)
    
    if msg != '':
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs
    
    # construct a matrix of all unique tmt combinations
    allTmts = unique(np.matrix(choicesets).reshape(choicesetsize * p, factors)) 
    # recalculate the number of tmt combinations
    t = len(allTmts) 
    
    # within each choiceset, sort the options lexicographically
    choicesets = [lexico(np.matrix(item)) for item in choicesets] 
    # reshape the choicesets into a 2D matrix
    choicesets = np.vstack([np.hstack(item) for item in choicesets]) 
    
    # check for duplicates
    dup = [] # a list of duplicate choicesets
    # loop through each choiceset except the last
    for i in range(len(choicesets)-1): 
        # loop through each remaining choiceset 
        for j in range(i+1, len(choicesets)): 
            # check if all entries are the same in both choicesets
            if all([choicesets[i,k]==choicesets[j,k] for k in range(np.shape(choicesets[i])[1])]): 
                dup.append(j+1) # append to the list
    
    if len(dup) > 0:
        if len(dup) == 1:
            msg += 'Warning: choice set %s is a duplicate.\n' % dup[0]
        else:
            tmp = str(list(np.sort(dup))).replace('[','').replace(']','')
            msg += 'Warning: choice sets %s are duplicates.\n' % tmp
    
    choicesets = unique(choicesets) # remove repeated rows (if any)
    p = len(choicesets) # number of unique choice sets
    
    # update output info
    msg += 'Number of choicesets: %d \n' % p
    
    # construct the b matrix
    bmat = np.matrix([0 for i in np.arange(numEffects * t)]).reshape(numEffects, t) 
    
    # define the main effects contrasts
    for tmt in range(t): # loop through each tmt 
        TopRow = 0
        for f in range(factors): # loop through each factor
            BottomRow = TopRow
            TopRow = TopRow + levels[f] - 1
            # get the orthogonal polynomial contrasts for the given factor
            poly = orthogpolys[levels[f] - 2] 
            # assign the main effects
            bmat[BottomRow:TopRow,tmt] = poly[:,allTmts[tmt,f]] 
    
    # convert to sympy
    bmat = sympy.Matrix(bmat)
    levels = sympy.Matrix(levels)
    
    # normalise the main effects 
    TopRow = 0
    for f in range(factors): # loop through each factor
        BottomRow = TopRow
        TopRow = TopRow + levels[f] - 1
        # get the orthogonal polynomial contrasts for the given factor
        poly =  sympy.Matrix(orthogpolys[levels[f] - 2]) 
        # calculate the normalising constant for each component
        norm = [sympy.sqrt(sum(([innerItem**2 for innerItem in poly[item,:]])*np.prod(levels))/levels[f]) for item in range(poly.shape[0])] 
        # normalise
        bmat[BottomRow:TopRow,:] = [bmat[BottomRow:TopRow,:][i,:]/norm[i] for i in range(len(norm))] 
    
    # construct the lambda matrix
    # initialise a matrix
    lmat = np.matrix([0 for i in np.arange(t * t)]).reshape(t, t) 
    # initialise an array of indicies
    lind = np.matrix([0 for i in np.arange(p * choicesetsize)]).reshape(p, choicesetsize) 
    
    # get the index for each option in each choiceset
    for ch in range(p): # loop through each choiceset
        EndCol = 0
        for op in range(choicesetsize): # loop thought each option in the choiceset
            StartCol = EndCol
            EndCol = StartCol + factors
            for tmt in range(t): # loop though each tmt
                if all([choicesets[ch,StartCol+k] == allTmts[tmt,k] for k in range(factors)]): 
                    lind[ch,op] = tmt 
    
    # calculate lambda
    for ch in range(p): # loop through each choiceset
        for i in range(choicesetsize-1): # loop through each option except the last
            for j in range(i+1, choicesetsize): # loop through each remaining option
                lmat[lind[ch,i], lind[ch,j]] = lmat[lind[ch,i], lind[ch,j]] - 1
                lmat[lind[ch,j], lind[ch,i]] = lmat[lind[ch,j], lind[ch,i]] - 1
    
    # calculate the diagonal entries of lambda
    for diag in range(t):
        lmat[diag,diag] = -np.sum(lmat[diag])
    
    lmat = sympy.Matrix(lmat)/(p*np.power(choicesetsize,2))
    
    # Save bmat and lmat.
    rows = ''
    rows += ''.join(str(bmat)).replace('[','').replace(']','').replace(',','')
    outputs['bmat'] = rows
    
    rows = ''
    rows += ''.join(str(lmat)).replace('[','').replace(']','').replace(',','')
    outputs['lmat'] = rows
  
    # Exit if this calc is taking too long.
    if (datetime.now() - START).seconds > MAX_TIME: 
        msg += 'Calculation is taking too long ... exiting.\n'
        outputs['msg'] = msg
        return outputs 
    
    # calculate the c matrix
    try:
        cmat = bmat*lmat*bmat.T # the c matrix
    except:
        msg += 'Unable to calculate the C matrix.\n'
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
       
    cRank = np.linalg.matrix_rank(cmat) # the rank of the c matrix
    
    # Save cmat
    rows = ''
    rows += ''.join(str(cmat)).replace('[','').replace(']','').replace(',','')
    outputs['cmat'] = rows
    
    # check the c matrix is of sufficient rank
    if cRank < numEffects:
        msg += '''
The determinant of the C matrix is zero. At least one of the effects cannot be estimated\n
Efficiency compared with optimal design for choice set size m = %s: 0%%\n
Efficiency compared with optimal design for optimal choice set size m = %s: 0%%\n''' % (choicesetsize, lcm(levels))
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
    
    try:
        detc = cmat.det() # the determinant of the c matrix
    except:
        msg += 'Unable to calculate the determinant of the C matrix\n' 
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
    
    msg += 'Det C is: %s \n' % str(float(detc))
    
    try:
        cinv = cmat.inv() # invert the c matrix
    except:
        msg += 'Unable to calculate the inverse of the C matrix\n'  
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
    
    # initialise a matrix
    correln = np.matrix([0 for i in np.arange(numEffects * numEffects)]).reshape(numEffects, numEffects) 
    correln = sympy.Matrix(correln)     # convert to sympy
    for i in range(numEffects):         # loop through each row
        for j in range(numEffects):     # loop through each column
            correln[i, j] = cinv[i, j]/sympy.sqrt(cinv[i, i] * cinv[j, j])
    
    # Save cinv and correln.
    rows = ''
    rows += ''.join(str(cinv)).replace('[','').replace(']','').replace(',','')
    outputs['cinv'] = rows
    
    rows = ''
    rows += ''.join(str(correln)).replace('[','').replace(']','').replace(',','')
    outputs['correln'] = rows
    
    # calculate the determinant of the optimal design
    prodlevels = np.product(levels)
    Sumdiffs = list(np.repeat(0, factors))
    optdet = 1
    optdet2 = np.power((1/prodlevels), numEffects)
    for q in range(factors):
        if levels[q] == 2:
            if choicesetsize%2 == 0:
                Sumdiffs[q] = np.power(choicesetsize, 2)/4
            else:
                Sumdiffs[q] = (np.power(choicesetsize, 2) - 1)/4
        else:
            if levels[q] >= choicesetsize:
                Sumdiffs[q] = choicesetsize * (choicesetsize - 1)/2
            else:
                x = choicesetsize//levels[q]
                y = choicesetsize%levels[q]
                Sumdiffs[q] = (np.power(choicesetsize, 2) - (levels[q] * np.power(x, 2) + 2 * x * y + y))/2
        optdet = optdet * np.power(((2 * levels[q] * Sumdiffs[q])/(np.power(choicesetsize, 2) * (levels[q] - 1) * prodlevels)), (levels[q] - 1))
    
    # calculate efficiency
    if detc > 0 and optdet > 0:
       eff = 100*np.power(detc/optdet,sympy.Rational(1, numEffects))
       eff2 = 100*np.power(detc/optdet2,sympy.Rational(1, numEffects))
       # output to user
       msg += 'Efficiency compared with optimal design for choice set size m = %s: %s%% \n' % (choicesetsize, round(eff, 6))
       msg += 'Efficiency compared with optimal design for optimal choice set size m = %s: %s%% \n' % (lcm(levels), round(eff2, 6))
    
    # initialise a zero matrix
    Block = sympy.Matrix([0 for i in np.arange(numEffects**2)]).reshape(numEffects, numEffects)
    End = 0
    for f in range(factors): # loop through each factor
        Start = End
        End = Start + levels[f] - 1
        # get the block of main effects
        Block[Start:End, Start:End] = cinv[Start:End, Start:End] 
    
    # Determine if all effects (i.e. the main effects) are uncorrelated.
    # MEuncorr will be True if Block == cinv
    MEuncorr = Block == cinv 
    
    # Output correlation details.
    if MEuncorr:
       if factors > 1:
          msg += 'Main effects are uncorrelated \n'
    else:
        msg += 'Main effects are correlated \n'
    
    outputs['msg'] = msg
    return outputs

    
def CheckSets_All2fis(inputs):
    '''
    inputs:  a dictionary of all input variables, in this case: 
             levels, msize, chsets, det
    outputs: a dictionary of all output variables, in this case: 
             msg, bmat, lmat, cmat, cinv, correln
    '''
    
    levels = inputs['levels']
    choicesetsize = inputs['msize']
    choicesets = inputs['chsets']
    optdet = inputs['det']
    
    # Create formatted outputs vars as a dictionary.
    outputs = {}
    
    # The text of this message string will be printed to the browser 
    msg = '' 
    
    # calculate a few little bits and pieces
    p = len(choicesets) # the number of choice sets
    factors = len(levels) # number of factors
    # define all possible 2fis
    choose2fis = list(itertools.combinations(range(1, factors + 1), 2)) 
    numME = sum([lvl - 1 for lvl in levels]) # number of main effect parameters
    numInts = np.shape(choose2fis)[0] # number of interactions
    ME2fiCombos = [(levels[item[0]-1] - 1, levels[item[1]-1] - 1) for item in choose2fis] # a list of tuples indicating the number of main effects in each factor of the 2fi
    num2FI = sum([np.prod(item) for item in ME2fiCombos]) # number of 2fi parameters
    numEffects = numME + num2FI; # total number of parameters 
    
    # Construct the othogonal polynomial contrasts.
    orthogpolys = construct_poly_contrasts()
    
    # check that each choiceset is made up of unique tmts
    for i in range(len(choicesets)): # loop through each choice set
        if len(unique(np.matrix(choicesets[i]).reshape(choicesetsize, factors))) != choicesetsize:
            msg += 'Repeated treatment combination in choice set %d.\n' % (i+1)
    
    if msg != '':
       msg += 'Cannot continue calculation.\n'
       outputs['msg'] = msg
       return outputs
    
    # construct a matrix of all unique tmt combinations
    allTmts = unique(np.matrix(choicesets).reshape(choicesetsize * p, factors)) 
    t = len(allTmts) # recalculate the number of tmt combinations
    
    # within each choiceset, sort the options lexicographically
    choicesets = [lexico(np.matrix(item)) for item in choicesets] 
    # reshape the choicesets into a 2D matrix
    choicesets = np.vstack([np.hstack(item) for item in choicesets]) 
    
    # check for duplicates
    dup = [] # a list of duplicate choicesets
    # loop through each choiceset except the last
    for i in range(len(choicesets)-1): 
        # loop through each remaining choiceset 
        for j in range(i+1, len(choicesets)): 
            # check if all entries are the same in both choicesets
            if all([choicesets[i,k]==choicesets[j,k] for k in range(np.shape(choicesets[i])[1])]): 
                dup.append(j+1) # append to the list
    
    if len(dup) > 0:
       if len(dup) == 1:
          msg += 'Warning: choice set %s is a duplicate.\n' % dup[0]
       else:
          tmp = str(list(np.sort(dup))).replace('[','').replace(']','')
          msg += 'Warning: choice sets %s are duplicates.\n' % tmp
    
    choicesets = unique(choicesets) # remove repeated rows (if any)
    p = len(choicesets) # number of unique choice sets
    
    # update output info
    msg += 'Number of choicesets: %d \n' % p
    
    # construct the b matrix
    # initialise a matrix
    bmat = np.matrix([0 for i in np.arange(numEffects * t)]).reshape(numEffects, t) 
    
    # define the main effects contrasts
    for tmt in range(t): # loop through each tmt 
        TopRow = 0
        for f in range(factors): # loop through each factor
            BottomRow = TopRow
            TopRow = TopRow + levels[f] - 1
            # get the orthogonal polynomial contrasts for the given factor
            poly = orthogpolys[levels[f] - 2] 
            # assign the main effects
            bmat[BottomRow:TopRow,tmt] = poly[:,allTmts[tmt,f]] 
       
    # define the interaction contrasts
    if len(choose2fis) > 0:
       RowIndex = numME
       for i in range(len(choose2fis)): # loop through each interaction
            # get the orthogonal polynomial contrasts for the first factor
            poly1 = orthogpolys[levels[choose2fis[i][0]-1] - 2] 
            # get the orthogonal polynomial contrasts for the second factor
            poly2 = orthogpolys[levels[choose2fis[i][1]-1] - 2] 
            # loop through each main effect contrast of the first factor
            for me1 in range(len(poly1)): 
                # loop through each main effect contrast of the second factor
                for me2 in range(len(poly2)): 
                    for tmt in range(t): # loop through each tmt 
                        # define the interaction contrast componenet
                        bmat[RowIndex,tmt] = poly1[me1,allTmts[tmt,choose2fis[i][0]-1]] * poly2[me2,allTmts[tmt,choose2fis[i][1]-1]] 
                    RowIndex = RowIndex + 1    
    
    # convert to sympy
    bmat = sympy.Matrix(bmat)
    levels = sympy.Matrix(levels)
    
    # normalise the main effects 
    TopRow = 0
    for f in range(factors): # loop through each factor
        BottomRow = TopRow
        TopRow = TopRow + levels[f] - 1
        # get the orthogonal polynomial contrasts for the given factor
        poly =  sympy.Matrix(orthogpolys[levels[f] - 2]) 
        norm = [sympy.sqrt(sum(([innerItem**2 for innerItem in poly[item,:]])*np.prod(levels))/levels[f]) for item in range(poly.shape[0])]  # calculate the normalising constant for each component
        # normalise
        bmat[BottomRow:TopRow,:] = [bmat[BottomRow:TopRow,:][i,:]/norm[i] for i in range(len(norm))] 
    
    # normalise the interactions
    if len(choose2fis) > 0:
        RowIndex = numME
        # loop through each interaction
        for i in range(len(choose2fis)): 
            # get the orthogonal polynomial contrasts for the first factor
            poly1 = orthogpolys[levels[choose2fis[i][0]-1] - 2] 
            # get the orthogonal polynomial contrasts for the second factor
            poly2 = orthogpolys[levels[choose2fis[i][1]-1] - 2] 
            # loop through each main effect contrast of the first factor
            for me1 in range(poly1.shape[0]): 
                # loop through each main effect contrast of the second factor
                for me2 in range(poly2.shape[0]): 
                    # define... a thing
                    poly = [poly1[me1,lv1] * poly2[me2,lv2] for lv1 in range(poly1.shape[1]) for lv2 in range(poly2.shape[1])] 
                    # calculate the normalising constant 
                    norm = sympy.sqrt(sum(([innerItem**2 for innerItem in poly])*np.prod(levels))/(levels[choose2fis[i][0]-1] * levels[choose2fis[i][1]-1]))  
                    bmat[RowIndex,:] = bmat[RowIndex,:]/norm # normalise
                    RowIndex = RowIndex + 1
    
    # construct the lambda matrix
    lmat = np.matrix([0 for i in np.arange(t * t)]).reshape(t, t) 
    # initialise an array of indicies
    lind = np.matrix([0 for i in np.arange(p * choicesetsize)]).reshape(p, choicesetsize) 
    
    # get the index for each option in each choiceset
    for ch in range(p): # loop through each choiceset
        EndCol = 0
        for op in range(choicesetsize): # loop thought each option in the choiceset
            StartCol = EndCol
            EndCol = StartCol + factors
            for tmt in range(t): # loop thought each tmt
                if all([choicesets[ch,StartCol+k] == allTmts[tmt,k] for k in range(factors)]): 
                    lind[ch,op] = tmt 
    
    # calculate lambda
    for ch in range(p): # loop through each choiceset
        for i in range(choicesetsize-1): # loop through each option except the last
            for j in range(i+1, choicesetsize): # loop through each remaining option
                lmat[lind[ch,i], lind[ch,j]] = lmat[lind[ch,i], lind[ch,j]] - 1
                lmat[lind[ch,j], lind[ch,i]] = lmat[lind[ch,j], lind[ch,i]] - 1
    
    # calculate the diagonal entries of lambda
    for diag in range(t):
        lmat[diag,diag] = -np.sum(lmat[diag])
    
    lmat = sympy.Matrix(lmat)/(p*(choicesetsize**2))
    
    # Save bmat and lmat.
    rows = ''
    rows += ''.join(str(bmat)).replace('[','').replace(']','').replace(',','')
    outputs['bmat'] = rows
    
    rows = ''
    rows += ''.join(str(lmat)).replace('[','').replace(']','').replace(',','')
    outputs['lmat'] = rows
    
    # Exit if this calc is taking too long.
    if (datetime.now() - START).seconds > MAX_TIME: 
        msg += 'Calculation is taking too long ... exiting.\n'
        outputs['msg'] = msg
        return outputs 
    
    # calculate the c matrix
    try:
        cmat = bmat*lmat*bmat.T # the c matrix
    except:
        msg += 'Unable to calculate the C matrix.\n'
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
    
    cRank = np.linalg.matrix_rank(cmat) # the rank of the c matrix
    
    # Save cmat
    rows = ''
    rows += ''.join(str(cmat)).replace('[','').replace(']','').replace(',','')
    outputs['cmat'] = rows
    
    # check the c matrix is of sufficient rank
    if cRank < numEffects:
        msg += 'The determinant of the C matrix is zero. At least one of the effects cannot be estimated\n'
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
    
    try:
        detc = cmat.det() # the determinant of the c matrix
    except:
        msg += 'Unable to calculate the determinant of the C matrix\n' 
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
    
    msg += 'Det C is: %s \n' % str(float(detc))
    
    try:
        cinv = cmat.inv() # invert the c matrix
    except:
        msg += 'Unable to calculate the inverse of the C matrix\n'  
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
    
    correln = np.matrix([0 for i in np.arange(numEffects * numEffects)]).reshape(numEffects, numEffects) # initialise a matrix
    correln = sympy.Matrix(correln) # convert to sympy
    for i in range(numEffects): # loop through each row
        for j in range(numEffects): # loop through each column
            correln[i, j] = cinv[i, j]/sympy.sqrt(cinv[i, i] * cinv[j, j])
    
    # Save cinv and correln.
    rows = ''
    rows += ''.join(str(cinv)).replace('[','').replace(']','').replace(',','')
    outputs['cinv'] = rows
    
    rows = ''
    rows += ''.join(str(correln)).replace('[','').replace(']','').replace(',','')
    outputs['correln'] = rows
    
    # If all factor are binary then calculate calculate the determinant of
    # the optimal design for the input choice set size.
    BinLvls = all([item==2 for item in levels]) # determine if all levels are binary
    if BinLvls: 
        if factors%2 == 0:
            optdet = np.power(((choicesetsize-1)*(factors+2)/(choicesetsize*(factors+1)*np.power(2,factors))), (factors+factors*(factors-1)/2))
        else:
            optdet = np.power(((choicesetsize-1)*(factors+1)/(choicesetsize*factors*np.power(2,factors))), (factors+factors (factors-1)/2))
    
    # calculate efficiency
    if detc > 0 and optdet > 0:
        eff = 100*np.power(detc/optdet,sympy.Rational(1, numEffects)) 
        if BinLvls:
            msg += 'Efficiency compared with optimal design: %s%% \n' % round(eff, 6)
        else:
            msg += 'Efficiency compared with input det C: %s%% \n' % round(eff, 6)
    
    Block = sympy.Matrix([0 for i in np.arange(numEffects**2)]).reshape(numEffects, numEffects) # initialise a zero matrix
    End = 0
    for f in range(factors): # loop through each factor
        Start = End
        End = Start + levels[f] - 1
        # get the block of main effects
        Block[Start:End, Start:End] = cinv[Start:End, Start:End] 
    for i in range(numInts): 
        Start = End
        End = Start + np.prod([levels[item-1] - 1 for item in choose2fis[i]])
        # get the block of interactions
        Block[Start:End, Start:End] = cinv[Start:End, Start:End] 
    
    # determine if the main effect are uncorrelated
    MEuncorr = Block[0:numME, 0:numME] == cinv[0:numME, 0:numME] 
    # determine if the interactions are uncorrelated
    Intuncorr = Block[numME:numEffects, numME:numEffects] == cinv[numME:numEffects, numME:numEffects] 
    # determine if the ME are uncorrelated with the intereactions
    MEIntuncorr = cinv[:numME, numME:numEffects] == sympy.Matrix([0 for i in np.arange(numME * num2FI)]).reshape(numME, num2FI) 
    # determine of all effect are uncorrelated
    Alluncorr = Block == cinv 
    
    # output correlation details
    if Alluncorr:
        if factors > 1:
            msg = msg + 'No effects are correlated \n'
    else:
        if MEuncorr:
            msg = msg + 'Main effects are uncorrelated \n'
        else:
            msg = msg + 'Main effects are correlated \n'
        if Intuncorr:
            if numInts > 1:
                msg = msg + 'Two-factor interactions are uncorrelated \n'
        else:
            if numInts > 1:
                msg = msg + 'Two-factor interactions are correlated \n'
        if MEIntuncorr:
            msg = msg + 'Main effects and two-factor interactions are uncorrelated \n'
        else:
            msg = msg + 'Main effects and two-factor interactions are correlated \n'
       
    outputs['msg'] = msg
    return outputs


def CheckSets_Some2fis(inputs):
    '''
    inputs:  a dictionary of all input variables, in this case: 
             levels, msize, chsets, factors, det
    outputs: a dictionary of all output variables, in this case: 
             msg, chsets, bmat, lmat, cmat, cinv, correln
    '''
    
    levels = inputs['levels']
    choicesetsize = inputs['msize']
    choicesets = inputs['chsets']
    optdet = inputs['det']
    choose2fis = inputs['twofis']
  
    # The text of this message string will be printed to the browser 
    msg = '' 
    
    # Create formatted outputs vars as a dictionary.
    outputs = {}
    
    # calculate a few little bits and pieces
    p = len(choicesets) # the number of choice sets
    factors = len(levels) # number of factors
    numME = sum([lvl - 1 for lvl in levels]) # number of main effect parameters
    numInts = np.shape(choose2fis)[0] # number of interactions
    # a list of tuples indicating the number of main effects in each factor of the 2fi
    ME2fiCombos = [(levels[item[0]-1] - 1, levels[item[1]-1] - 1) for item in choose2fis] 
    num2FI = sum([np.prod(item) for item in ME2fiCombos]) # number of 2fi parameters
    numEffects = numME + num2FI; # total number of parameters 

    # Construct the othogonal polynomial contrasts.
    orthogpolys = construct_poly_contrasts()
    
    # check that each choiceset is made up of unique tmts
    for i in range(len(choicesets)): # loop through each choice set
        if len(unique(np.matrix(choicesets[i]).reshape(choicesetsize, factors))) != choicesetsize:
            msg += 'Repeated treatment combination in choice set %d.\n' % (i+1)
    
    if msg != '':
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs
    
    # construct a matrix of all unique tmt combinations
    allTmts = unique(np.matrix(choicesets).reshape(choicesetsize * p, factors)) 
    t = len(allTmts) # recalculate the number of tmt combinations
    
    # within each choiceset, sort the options lexicographically
    choicesets = [lexico(np.matrix(item)) for item in choicesets] 
    # reshape the choicesets into a 2D matrix
    choicesets = np.vstack([np.hstack(item) for item in choicesets]) 
    
    # check for duplicates
    dup = [] # a list of duplicate choicesets
    # loop through each choiceset except the last
    for i in range(len(choicesets)-1): 
        # loop through each remaining choiceset 
        for j in range(i+1, len(choicesets)): 
            # check if all entries are the same in both choicesets
            if all([choicesets[i,k]==choicesets[j,k] for k in range(np.shape(choicesets[i])[1])]): 
                dup.append(j+1) # append to the list
    
    if len(dup) > 0:
        if len(dup) == 1:
            msg += 'Warning: choice set %s is a duplicate.\n' % dup[0]
        else:
            tmp = str(list(np.sort(dup))).replace('[','').replace(']','')
            msg += 'Warning: choice sets %s are duplicates.\n' % tmp
    
    choicesets = unique(choicesets) # remove repeated rows (if any)
    p = len(choicesets) # number of unique choice sets
    
    # update output info
    msg += 'Number of choicesets: %d \n' % p
    
    # construct the b matrix
    bmat = np.matrix([0 for i in np.arange(numEffects * t)]).reshape(numEffects, t) # initialise a matrix
    
    # define the main effects contrasts
    for tmt in range(t): # loop through each tmt 
        TopRow = 0
        for f in range(factors): # loop through each factor
            BottomRow = TopRow
            TopRow = TopRow + levels[f] - 1
            # get the orthogonal polynomial contrasts for the given factor
            poly = orthogpolys[levels[f] - 2] 
            # assign the main effects
            bmat[BottomRow:TopRow,tmt] = poly[:,allTmts[tmt,f]] 
       
    # define the interaction contrasts
    if len(choose2fis) > 0:
        RowIndex = numME
        for i in range(len(choose2fis)): 
            # get the orthogonal polynomial contrasts for the first factor
            poly1 = orthogpolys[levels[choose2fis[i][0]-1] - 2] 
            # get the orthogonal polynomial contrasts for the second factor
            poly2 = orthogpolys[levels[choose2fis[i][1]-1] - 2] 
            # loop through each main effect contrast of the first factor
            for me1 in range(len(poly1)): 
                # loop through each main effect contrast of the second factor
                for me2 in range(len(poly2)): 
                    for tmt in range(t): # loop through each tmt 
                        # define the interaction contrast componenet
                        bmat[RowIndex,tmt] = poly1[me1,allTmts[tmt,choose2fis[i][0]-1]] * poly2[me2,allTmts[tmt,choose2fis[i][1]-1]] 
                    RowIndex = RowIndex + 1    
    
    # convert to sympy
    bmat = sympy.Matrix(bmat)
    levels = sympy.Matrix(levels)
    
    # normalise the main effects 
    TopRow = 0
    for f in range(factors): # loop through each factor
        BottomRow = TopRow
        TopRow = TopRow + levels[f] - 1
        # get the orthogonal polynomial contrasts for the given factor
        poly =  sympy.Matrix(orthogpolys[levels[f] - 2]) 
        # calculate the normalising constant for each component
        norm = [sympy.sqrt(sum(([innerItem**2 for innerItem in poly[item,:]])*np.prod(levels))/levels[f]) for item in range(poly.shape[0])]  
        # normalise
        bmat[BottomRow:TopRow,:] = [bmat[BottomRow:TopRow,:][i,:]/norm[i] for i in range(len(norm))] 
    
    # normalise the interactions
    if len(choose2fis) > 0:
        RowIndex = numME
        for i in range(len(choose2fis)): 
            # get the orthogonal polynomial contrasts for the first factor
            poly1 = orthogpolys[levels[choose2fis[i][0]-1] - 2] 
            # get the orthogonal polynomial contrasts for the second factor
            poly2 = orthogpolys[levels[choose2fis[i][1]-1] - 2] 
            # loop through each main effect contrast of the first factor
            for me1 in range(poly1.shape[0]): 
                # loop through each main effect contrast of the second factor
                for me2 in range(poly2.shape[0]): 
                    # define... a thing
                    poly = [poly1[me1,lv1] * poly2[me2,lv2] for lv1 in range(poly1.shape[1]) for lv2 in range(poly2.shape[1])] 
                    # calculate the normalising constant 
                    norm = sympy.sqrt(sum(([innerItem**2 for innerItem in poly])*np.prod(levels))/(levels[choose2fis[i][0]-1] * levels[choose2fis[i][1]-1]))  
                    bmat[RowIndex,:] = bmat[RowIndex,:]/norm # normalise
                    RowIndex = RowIndex + 1
    
    # construct the lambda matrix, initialise a matrix
    lmat = np.matrix([0 for i in np.arange(t * t)]).reshape(t, t) 
    # initialise an array of indicies
    lind = np.matrix([0 for i in np.arange(p * choicesetsize)]).reshape(p, choicesetsize) 
    
    # get the index for each option in each choiceset
    for ch in range(p): # loop through each choiceset
        EndCol = 0
        for op in range(choicesetsize): # loop thought each option in the choiceset
            StartCol = EndCol
            EndCol = StartCol + factors
            for tmt in range(t): # loop thought each tmt
                if all([choicesets[ch,StartCol+k] == allTmts[tmt,k] for k in range(factors)]): 
                    lind[ch,op] = tmt 
    
    # calculate lambda
    for ch in range(p): # loop through each choiceset
        for i in range(choicesetsize-1): # loop through each option except the last
            for j in range(i+1, choicesetsize): # loop through each remaining option
                lmat[lind[ch,i], lind[ch,j]] = lmat[lind[ch,i], lind[ch,j]] - 1
                lmat[lind[ch,j], lind[ch,i]] = lmat[lind[ch,j], lind[ch,i]] - 1
    
    # calculate the diagonal entries of lambda
    for diag in range(t):
        lmat[diag,diag] = -np.sum(lmat[diag])
    
    lmat = sympy.Matrix(lmat)/(p*(choicesetsize**2))
    
    # Save bmat and lmat.
    rows = ''
    rows += ''.join(str(bmat)).replace('[','').replace(']','').replace(',','')
    outputs['bmat'] = rows
    
    rows = ''
    rows += ''.join(str(lmat)).replace('[','').replace(']','').replace(',','')
    outputs['lmat'] = rows
    
    # Exit if this calc is taking too long.
    if (datetime.now() - START).seconds > MAX_TIME: 
        msg += 'Calculation is taking too long ... exiting.\n'
        outputs['msg'] = msg
        return outputs 
    
    # calculate the c matrix
    try:
        cmat = bmat*lmat*bmat.T # the c matrix
    except:
        msg += 'Unable to calculate the C matrix.\n'
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
    
    cRank = np.linalg.matrix_rank(cmat) # the rank of the c matrix
    
    # Save cmat
    rows = ''
    rows += ''.join(str(cmat)).replace('[','').replace(']','').replace(',','')
    outputs['cmat'] = rows
    
    # check the c matrix is of sufficient rank
    if cRank < numEffects:
        msg += 'The determinant of the C matrix is zero. At least one of the effects cannot be estimated\n'
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
    
    try:
        detc = cmat.det() # the determinant of the c matrix
    except:
        msg += 'Unable to calculate the determinant of the C matrix\n' 
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
    
    msg += 'Det C is: %s \n' % str(float(detc))
    
    try:
        cinv = cmat.inv() # invert the c matrix
    except:
        msg += 'Unable to calculate the inverse of the C matrix\n'  
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
    
    # initialise a matrix
    correln = np.matrix([0 for i in np.arange(numEffects * numEffects)]).reshape(numEffects, numEffects) 
    correln = sympy.Matrix(correln)     # convert to sympy
    for i in range(numEffects):         # loop through each row
        for j in range(numEffects):     # loop through each column
            correln[i, j] = cinv[i, j]/sympy.sqrt(cinv[i, i] * cinv[j, j])
    
    # Save cinv and correln.
    rows = ''
    rows += ''.join(str(cinv)).replace('[','').replace(']','').replace(',','')
    outputs['cinv'] = rows
    
    rows = ''
    rows += ''.join(str(correln)).replace('[','').replace(']','').replace(',','')
    outputs['correln'] = rows
    
    # If all factor are binary then calculate calculate the determinant 
    # of the optimal design for the input choice set size
    BinLvls = all([item==2 for item in levels]) # determine if all levels are binary
    if BinLvls: 
        if factors%2 == 0:
            optdet = np.power(((choicesetsize-1)*(factors+2)/(choicesetsize*(factors+1)*np.power(2,factors))), (factors+factors*(factors-1)/2))
        else:
            optdet = np.power(((choicesetsize-1)*(factors+1)/(choicesetsize*factors*np.power(2,factors))), (factors+factors (factors-1)/2))
    
    # calculate efficiency
    if detc > 0 and optdet > 0:
        eff = 100*np.power(detc/optdet,sympy.Rational(1, numEffects)) 
        if BinLvls:
            msg += 'Efficiency compared with optimal design: %s%% \n' % round(eff, 6)
        else:
            msg += 'Efficiency compared with input det C: %s%% \n' % round(eff, 6)
    
    Block = sympy.Matrix([0 for i in np.arange(numEffects**2)]).reshape(numEffects, numEffects) # initialise a zero matrix
    End = 0
    for f in range(factors): # loop through each factor
        Start = End
        End = Start + levels[f] - 1
        # get the block of main effects
        Block[Start:End, Start:End] = cinv[Start:End, Start:End] 
    for i in range(numInts): # loop through each interactions
        Start = End
        End = Start + np.prod([levels[item-1] - 1 for item in choose2fis[i]])
        # get the block of interactions
        Block[Start:End, Start:End] = cinv[Start:End, Start:End] 
    
    # determine if the main effect are uncorrelated
    MEuncorr = Block[0:numME, 0:numME] == cinv[0:numME, 0:numME] 
    Intuncorr = Block[numME:numEffects, numME:numEffects] == cinv[numME:numEffects, numME:numEffects] # determine if the interactions are uncorrelated
    # determine if the ME are uncorrelated with the intereactions
    MEIntuncorr = cinv[:numME, numME:numEffects] == sympy.Matrix([0 for i in np.arange(numME * num2FI)]).reshape(numME, num2FI) 
    Alluncorr = Block == cinv # determine of all effect are uncorrelated
    
    # output correlation details
    if Alluncorr:
        if factors > 1:
            msg = msg + 'No effects are correlated \n'
    else:
        if MEuncorr:
            msg = msg + 'Main effects are uncorrelated \n'
        else:
            msg = msg + 'Main effects are correlated \n'
        if Intuncorr:
            if numInts > 1:
                msg = msg + 'Two-factor interactions are uncorrelated \n'
        else:
            if numInts > 1:
                msg = msg + 'Two-factor interactions are correlated \n'
        if MEIntuncorr:
            msg = msg + 'Main effects and two-factor interactions are uncorrelated \n'
        else:
            msg = msg + 'Main effects and two-factor interactions are correlated \n'
       
    outputs['msg'] = msg
    return outputs



def ConstructSets_All2fis(inputs):
    '''
    inputs:  a dictionary of all input variables, in this case: 
             levels, msize, tmts, gens, factors, det
    outputs: a dictionary of all output variables, in this case: 
             msg, chsets, bmat, lmat, cmat, cinv, correln
    '''
    
    levels = inputs['levels']
    choicesetsize = inputs['msize']
    tmts = inputs['tmts']
    generators = inputs['gens']
    optdet = inputs['det']
    
    # The text of this message string will be printed to the browser 
    msg = '' 
    
    # Create formatted outputs vars as a dictionary.
    outputs = {}
    
    # calculate a few little bits and pieces
    factors = len(levels) # number of factors
    # define all possible 2fis
    choose2fis = list(itertools.combinations(range(1, factors + 1), 2)) 
    t = len(tmts)       # number of tmt combinations
    g = len(generators) # number of generators
    numME = sum([lvl - 1 for lvl in levels]) # number of main effect parameters
    numInts = np.shape(choose2fis)[0] # number of interactions
    # a list of tuples indicating the number of main effects in each factor of the 2fi
    ME2fiCombos = [(levels[item[0]-1] - 1, levels[item[1]-1] - 1) for item in choose2fis] 
    num2FI = sum([np.prod(item) for item in ME2fiCombos]) # number of 2fi parameters
    numEffects = numME + num2FI; # total number of parameters 
    
    # check number of generators and levels
    if factors != np.shape(generators)[1]/(choicesetsize - 1):
        msg += 'Treatment combinations and generators must have the same number of columns.\n'
    
    if msg != '':
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
    
    # check the generators
    generators = np.array([np.reshape(item, (choicesetsize - 1, factors)) for item in generators]) # reshape first
    for gen in generators: # loop though each generator
        gSet = np.reshape(gen, (choicesetsize - 1, factors)) # reshape the generator into the tmt sets
        if len(unique(np.matrix(gSet))) != len(gSet): 
            msg += 'Repeated treatment combinations in the set of generators.\n'
        for tmt in gSet: # loop through each tmt in the given generator
            if all(tmt == [0 for i in range(factors)]): # check the tmt is not all zeros
                msg += 'Zero generator in the set of generators.\n'
    
    if msg != '':
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
    
    # convert a few things to myComb type
    tmts = np.array([myComb(val=item, nmod=levels) for item in tmts]) 
    generators = np.array([[myComb(val=chSet, nmod=levels) for chSet in gen] for gen in generators]) 
    
    # Construct the othogonal polynomial contrasts.
    orthogpolys = construct_poly_contrasts()
    
    # construct a matrix of choicesets
    choicesets = np.array([0 for i in np.arange(t*g * choicesetsize * factors)]).reshape(t*g, choicesetsize, factors)
    
    # get a list of tmt/generator combinations
    gen_tmt = [pair for pair in itertools.product(tmts, generators)] 
    # extract the first option (tmt) from the list
    firstOption = [item[0].val for item in gen_tmt] 
    # generate the remaining options by adding the generator to the tmt
    remainingOptions = [[row[0] + item for item in row[1]] for row in gen_tmt] 
    
    for ch1 in range(len(gen_tmt)): # loop thought each gen/tmt combo
       choicesets[ch1][0] = firstOption[ch1] # assign the first option
       for ch in range(len(remainingOptions[ch1])): # loop through each generator
          choicesets[ch1][ch+1] = remainingOptions[ch1][ch] # assign the generated option
    
    # check that each choiceset is made up of unique tmts
    for i in range(len(choicesets)): # loop through each choice set
        if len(unique(np.matrix(choicesets[i]))) != len(choicesets[i]):
            msg += 'Repeated treatment combination in choice set %d.\n' % (i+1)
    
    if msg != '':
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs
             
    # saved an unordered copy of the choicesets for output (reshaped into a 2D matrix)
    choicesets_out = np.matrix(np.vstack([np.hstack(item) for item in choicesets])) 
    
    # Save choicesets
    rows = '' 
    for row in choicesets_out:
        rows += ''.join(str(row)).replace('[','').replace(']','') + '\n'
    outputs['chsets'] = rows
    
    allTmts = np.matrix(np.vstack(choicesets)) # construct a matrix of all tmt combinations
    allTmts = unique(allTmts) # remove repeated tmt combos
    t = len(allTmts) # recalculate the number of tmt combinations
    
    # within each choiceset, sort the options lexicographically
    choicesets = [lexico(np.matrix(item)) for item in choicesets] 
    # reshape the choicesets into a 2D matrix
    choicesets = np.vstack([np.hstack(item) for item in choicesets]) 
    
    # check for duplicates
    dup = list() # initialise a list of duplicate choicesets
    for i in range(len(choicesets)-1): # loop through each choiceset except the last
        for j in range(i+1, len(choicesets)): # loop through each remaining choiceset 
            # check if all entries are the same in both choicesets
            if all([choicesets[i,k]==choicesets[j,k] for k in range(np.shape(choicesets[i])[1])]): 
                dup.append(j+1) # append to the list
    if len(dup) > 0:
        if len(dup) == 1:
            msg += 'Warning: choice set %s is a duplicate.\n' % dup[0]
        else:
            tmp = str(list(np.sort(dup))).replace('[','').replace(']','')
            msg += 'Warning: choice sets %s are duplicates.\n' % tmp
    
    choicesets = unique(choicesets) # remove repeated rows (if any)
    p = len(choicesets) # number of unique choice sets
    
    # update output info
    msg += 'Number of choicesets: %d \n' % p
    
    # construct the b matrix, initialise a matrix
    bmat = np.matrix([0 for i in np.arange(numEffects * t)]).reshape(numEffects, t) 
    
    # define the main effects contrasts
    for tmt in range(t): # loop through each tmt 
        TopRow = 0
        for f in range(factors): # loop through each factor
            BottomRow = TopRow
            TopRow = TopRow + levels[f] - 1
            # get the orthogonal polynomial contrasts for the given factor
            poly = orthogpolys[levels[f] - 2] 
            # assign the main effects
            bmat[BottomRow:TopRow,tmt] = poly[:,allTmts[tmt,f]] 
       
    # define the interaction contrasts
    if len(choose2fis) > 0:
        RowIndex = numME
        for i in range(len(choose2fis)): # loop through each interaction
            # get the orthogonal polynomial contrasts for the first factor
            poly1 = orthogpolys[levels[choose2fis[i][0]-1] - 2] 
            # get the orthogonal polynomial contrasts for the second factor
            poly2 = orthogpolys[levels[choose2fis[i][1]-1] - 2] 
            # loop through each main effect contrast of the first factor
            for me1 in range(len(poly1)): 
                # loop through each main effect contrast of the second factor
                for me2 in range(len(poly2)): 
                    for tmt in range(t): # loop through each tmt 
                        # define the interaction contrast componenet
                        bmat[RowIndex,tmt] = poly1[me1,allTmts[tmt,choose2fis[i][0]-1]] * poly2[me2,allTmts[tmt,choose2fis[i][1]-1]] 
                    RowIndex = RowIndex + 1
    
    # convert to sympy
    bmat = sympy.Matrix(bmat)
    levels = sympy.Matrix(levels)
    
    # normalise the main effects 
    TopRow = 0
    for f in range(factors): # loop through each factor
        BottomRow = TopRow
        TopRow = TopRow + levels[f] - 1
        # get the orthogonal polynomial contrasts for the given factor
        poly =  sympy.Matrix(orthogpolys[levels[f] - 2]) 
        # calculate the normalising constant for each component
        norm = [sympy.sqrt(sum(([innerItem**2 for innerItem in poly[item,:]])*np.prod(levels))/levels[f]) for item in range(poly.shape[0])]  
        # normalise
        bmat[BottomRow:TopRow,:] = [bmat[BottomRow:TopRow,:][i,:]/norm[i] for i in range(len(norm))] 
    
    # normalise the interactions
    if len(choose2fis) > 0:
        RowIndex = numME
        for i in range(len(choose2fis)): # loop through each interaction
            # get the orthogonal polynomial contrasts for the first factor
            poly1 = orthogpolys[levels[choose2fis[i][0]-1] - 2] 
            # get the orthogonal polynomial contrasts for the second factor
            poly2 = orthogpolys[levels[choose2fis[i][1]-1] - 2] 
            # loop through each main effect contrast of the first factor
            for me1 in range(poly1.shape[0]): 
                # loop through each main effect contrast of the second factor
                for me2 in range(poly2.shape[0]): 
                    # define... a thing
                    poly = [poly1[me1,lv1] * poly2[me2,lv2] for lv1 in range(poly1.shape[1]) for lv2 in range(poly2.shape[1])] 
                    # calculate the normalising constant 
                    norm = sympy.sqrt(sum(([innerItem**2 for innerItem in poly])*np.prod(levels))/(levels[choose2fis[i][0]-1] * levels[choose2fis[i][1]-1]))  
                    # normalise
                    bmat[RowIndex,:] = bmat[RowIndex,:]/norm 
                    RowIndex = RowIndex + 1
    
    
    # construct the lambda matrix, initialise a matrix
    lmat = np.matrix([0 for i in np.arange(t * t)]).reshape(t, t) 
    # initialise an array of indecies
    lind = np.matrix([0 for i in np.arange(p * choicesetsize)]).reshape(p, choicesetsize) 
    
    # get the index for each option in each choiceset
    for ch in range(p): # loop through each choiceset
        EndCol = 0
        for op in range(choicesetsize): # loop thought each option in the choiceset
            StartCol = EndCol
            EndCol = StartCol + factors
            for tmt in range(t): # loop thought each tmt
                if all([choicesets[ch,StartCol+k] == allTmts[tmt,k] for k in range(factors)]): 
                    lind[ch,op] = tmt 
    
    # calculate lambda
    for ch in range(p): # loop through each choiceset
        for i in range(choicesetsize-1): # loop through each option except the last
            for j in range(i+1, choicesetsize): # loop through each remaining option
                lmat[lind[ch,i], lind[ch,j]] = lmat[lind[ch,i], lind[ch,j]] - 1
                lmat[lind[ch,j], lind[ch,i]] = lmat[lind[ch,j], lind[ch,i]] - 1
    
    # calculate the diagonal entries of lambda
    for diag in range(t):
        lmat[diag,diag] = -np.sum(lmat[diag])
    
    lmat = sympy.Matrix(lmat)/(p*(choicesetsize**2))
    
    # Save bmat and lmat.
    rows = ''
    rows += ''.join(str(bmat)).replace('[','').replace(']','').replace(',','')
    outputs['bmat'] = rows
    
    rows = ''
    rows += ''.join(str(lmat)).replace('[','').replace(']','').replace(',','')
    outputs['lmat'] = rows
    
    # Exit if this calc is taking too long.
    if (datetime.now() - START).seconds > MAX_TIME: 
        msg += 'Calculation is taking too long ... exiting.\n'
        outputs['msg'] = msg
        return outputs 
    
    # calculate the c matrix
    try:
        cmat = bmat*lmat*bmat.T # the c matrix
    except:
        msg += 'Unable to calculate the C matrix.\n'
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
    
    cRank = np.linalg.matrix_rank(cmat) # the rank of the c matrix
    
    # Save cmat
    rows = ''
    rows += ''.join(str(cmat)).replace('[','').replace(']','').replace(',','')
    outputs['cmat'] = rows
    
    # check the c matrix is of sufficient rank
    if cRank < numEffects:
        msg += 'The determinant of the C matrix is zero. At least one of the effects cannot be estimated\n'
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
    
    try:
        detc = cmat.det() # the determinant of the c matrix
    except:
        msg += 'Unable to calculate the determinant of the C matrix\n' 
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
    
    msg += 'Det C is: %s \n' % str(float(detc))
    
    try:
        cinv = cmat.inv() # invert the c matrix
    except:
        msg += 'Unable to calculate the inverse of the C matrix\n'  
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
    
    # initialise a matrix
    correln = np.matrix([0 for i in np.arange(numEffects * numEffects)]).reshape(numEffects, numEffects) 
    correln = sympy.Matrix(correln)     # convert to sympy
    for i in range(numEffects):         # loop through each row
        for j in range(numEffects):      # loop through each column
            correln[i, j] = cinv[i, j]/sympy.sqrt(cinv[i, i] * cinv[j, j])
    
    # Save cinv and correln.
    rows = ''
    rows += ''.join(str(cinv)).replace('[','').replace(']','').replace(',','')
    outputs['cinv'] = rows
    
    rows = ''
    rows += ''.join(str(correln)).replace('[','').replace(']','').replace(',','')
    outputs['correln'] = rows
    
    # If all factor are binary then calculate calculate the determinant 
    # of the optimal design for the input choice set size.
    BinLvls = all([item==2 for item in levels]) # determine if all levels are binary
    if BinLvls: 
        if factors%2 == 0:
            optdet = np.power(((choicesetsize-1)*(factors+2)/(choicesetsize*(factors+1)*np.power(2,factors))), (factors+factors*(factors-1)/2))
        else:
            optdet = np.power(((choicesetsize-1)*(factors+1)/(choicesetsize*factors*np.power(2,factors))), (factors+factors (factors-1)/2))
    
    # calculate efficiency
    if detc > 0 and optdet > 0:
        eff = 100*np.power(detc/optdet,sympy.Rational(1, numEffects)) 
        if BinLvls:
            msg += 'Efficiency compared with optimal design: %s%% \n' % round(eff, 6)
        else:
            msg += 'Efficiency compared with input det C: %s%% \n' % round(eff, 6)
    
    # initialise a zero matrix
    Block = sympy.Matrix([0 for i in np.arange(numEffects**2)]).reshape(numEffects, numEffects) 
    End = 0
    for f in range(factors): # loop through each factor
        Start = End
        End = Start + levels[f] - 1
        # get the block of main effects
        Block[Start:End, Start:End] = cinv[Start:End, Start:End] 
    for i in range(numInts): # loop through each interactions
        Start = End
        End = Start + np.prod([levels[item-1] - 1 for item in choose2fis[i]])
        # get the block of interactions
        Block[Start:End, Start:End] = cinv[Start:End, Start:End] 
    
    # determine if the main effect are uncorrelated
    MEuncorr = Block[0:numME, 0:numME] == cinv[0:numME, 0:numME] 
    # determine if the interactions are uncorrelated
    Intuncorr = Block[numME:numEffects, numME:numEffects] == cinv[numME:numEffects, numME:numEffects] 
    # determine if the ME are uncorrelated with the intereactions
    MEIntuncorr = cinv[:numME, numME:numEffects] == sympy.Matrix([0 for i in np.arange(numME * num2FI)]).reshape(numME, num2FI) 
    # determine of all effect are uncorrelated
    Alluncorr = Block == cinv 
    
    # output correlation details
    if Alluncorr:
        if factors > 1:
            msg = msg + 'No effects are correlated \n'
    else:
        if MEuncorr:
            msg = msg + 'Main effects are uncorrelated \n'
        else:
            msg = msg + 'Main effects are correlated \n'
        if Intuncorr:
            if numInts > 1:
                msg = msg + 'Two-factor interactions are uncorrelated \n'
        else:
            if numInts > 1:
                msg = msg + 'Two-factor interactions are correlated \n'
        if MEIntuncorr:
            msg = msg + 'Main effects and two-factor interactions are uncorrelated \n'
        else:
            msg = msg + 'Main effects and two-factor interactions are correlated \n'
       
    outputs['msg'] = msg
    return outputs


def ConstructSets_Some2fis(inputs):
    '''
    inputs:  a dictionary of all input variables, in this case: 
             levels, msize, tmts, gens, factors, det, twofis
    outputs: a dictionary of all output variables, in this case: 
             msg, chsets, bmat, lmat, cmat, cinv, correln
    '''
    levels = inputs['levels']
    choicesetsize = inputs['msize']
    tmts = inputs['tmts']
    generators = inputs['gens']
    optdet = inputs['det']
    choose2fis = inputs['twofis']
    
    # The text of this message string will be printed to the browser 
    msg = '' 
    
    # Create formatted outputs vars as a dictionary.
    outputs = {}
    
    # calculate a few little bits and pieces
    factors = len(levels) # number of factors
    t = len(tmts) # number of tmt combinations
    g = len(generators) # number of generators
    numME = sum([lvl - 1 for lvl in levels]) # number of main effect parameters
    numInts = np.shape(choose2fis)[0] # number of interactions
    # a list of tuples indicating the number of main effects in each factor of the 2fi
    ME2fiCombos = [(levels[item[0]-1] - 1, levels[item[1]-1] - 1) for item in choose2fis] 
    num2FI = sum([np.prod(item) for item in ME2fiCombos]) # number of 2fi parameters
    numEffects = numME + num2FI; # total number of parameters 
    
    # check number of generators and levels
    if factors != np.shape(generators)[1]/(choicesetsize - 1):
        msg = msg + 'Treatment combinations and generators must have the same number of columns\n'

    if msg != '':
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
    
    # check the generators, reshape first
    generators = np.array([np.reshape(item, (choicesetsize - 1, factors)) for item in generators]) 
    for gen in generators: # loop though each generator
        # reshape the generator into the tmt sets
        gSet = np.reshape(gen, (choicesetsize - 1, factors)) 
        if len(unique(np.matrix(gSet))) != len(gSet): 
            msg += 'Repeated treatment combinations in the set of generators.\n'
        for tmt in gSet: # loop through each tmt in the given generator
            if all(tmt == [0 for i in range(factors)]): # check the tmt is not all zeros
                msg += 'Zero generator in the set of generators.\n'
    
    if msg != '':
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
    
    # convert a few things to myComb type
    tmts = np.array([myComb(val=item, nmod=levels) for item in tmts]) 
    generators = np.array([[myComb(val=chSet, nmod=levels) for chSet in gen] for gen in generators]) 
    
    # Construct the othogonal polynomial contrasts.
    orthogpolys = construct_poly_contrasts()
    
    # construct a matrix of choicesets
    choicesets = np.array([0 for i in np.arange(t*g * choicesetsize * factors)]).reshape(t*g, choicesetsize, factors)
    
    # get a list of tmt/generator combinations
    gen_tmt = [pair for pair in itertools.product(tmts, generators)] 
    # extract the first option (tmt) from the list
    firstOption = [item[0].val for item in gen_tmt] 
    # generate the remaining options by adding the generator to the tmt
    remainingOptions = [[row[0] + item for item in row[1]] for row in gen_tmt] 
    
    for ch1 in range(len(gen_tmt)): # loop thought each gen/tmt combo
        choicesets[ch1][0] = firstOption[ch1] # assign the first option
        for ch in range(len(remainingOptions[ch1])): # loop through each generator
            choicesets[ch1][ch+1] = remainingOptions[ch1][ch] # assign the generated option
       
    # check that each choiceset is made up of unique tmts
    for i in range(len(choicesets)): # loop through each choice set
        if len(unique(np.matrix(choicesets[i]))) != len(choicesets[i]):
               msg += 'Repeated treatment combination in choice set %d.\n' % (i+1)
    
    if msg != '':
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs
             
    # saved an unordered copy of the choicesets for output (reshaped into a 2D matrix)
    choicesets_out = np.matrix(np.vstack([np.hstack(item) for item in choicesets])) 
    
    # Save choicesets
    rows = '' 
    for row in choicesets_out:
        rows += ''.join(str(row)).replace('[','').replace(']','') + '\n'
    outputs['chsets'] = rows
    
    allTmts = np.matrix(np.vstack(choicesets)) # construct a matrix of all tmt combinations
    allTmts = unique(allTmts) # remove repeated tmt combos
    t = len(allTmts) # recalculate the number of tmt combinations
    
    # within each choiceset, sort the options lexicographically
    choicesets = [lexico(np.matrix(item)) for item in choicesets] 
    # reshape the choicesets into a 2D matrix
    choicesets = np.vstack([np.hstack(item) for item in choicesets]) 
    
    # check for duplicates
    dup = list() # initialise a list of duplicate choicesets
    for i in range(len(choicesets)-1): # loop through each choiceset except the last
        for j in range(i+1, len(choicesets)): # loop through each remaining choiceset 
            # check if all entries are the same in both choicesets
            if all([choicesets[i,k]==choicesets[j,k] for k in range(np.shape(choicesets[i])[1])]): 
                dup.append(j+1) # append to the list
    if len(dup) > 0:
        if len(dup) == 1:
               msg += 'Warning: choice set %s is a duplicate.\n' % dup[0]
        else:
               tmp = str(list(np.sort(dup))).replace('[','').replace(']','')
               msg += 'Warning: choice sets %s are duplicates.\n' % tmp
    
    choicesets = unique(choicesets) # remove repeated rows (if any)
    p = len(choicesets) # number of unique choice sets
    
    # update output info
    msg += 'Number of choicesets: %d \n' % p
    
    # construct the b matrix, initialise a matrix
    bmat = np.matrix([0 for i in np.arange(numEffects * t)]).reshape(numEffects, t) 
    
    # define the main effects contrasts
    for tmt in range(t): # loop through each tmt 
       TopRow = 0
       for f in range(factors): # loop through each factor
            BottomRow = TopRow
            TopRow = TopRow + levels[f] - 1
            poly = orthogpolys[levels[f] - 2] 
            # get the orthogonal polynomial contrasts for the given factor
            bmat[BottomRow:TopRow,tmt] = poly[:,allTmts[tmt,f]] # assign the main effects

    # define the interaction contrasts
    if len(choose2fis) > 0:
        RowIndex = numME
        for i in range(len(choose2fis)): # loop through each interaction
            # get the orthogonal polynomial contrasts for the first factor
            poly1 = orthogpolys[levels[choose2fis[i][0]-1] - 2] 
            # get the orthogonal polynomial contrasts for the second factor
            poly2 = orthogpolys[levels[choose2fis[i][1]-1] - 2] 
            # loop through each main effect contrast of the first factor
            for me1 in range(len(poly1)): 
                # loop through each main effect contrast of the second factor
                for me2 in range(len(poly2)): 
                    for tmt in range(t): # loop through each tmt 
                        # define the interaction contrast componenet
                        bmat[RowIndex,tmt] = poly1[me1,allTmts[tmt,choose2fis[i][0]-1]] * poly2[me2,allTmts[tmt,choose2fis[i][1]-1]] 
                    RowIndex = RowIndex + 1
    
    # convert to sympy
    bmat = sympy.Matrix(bmat)
    levels = sympy.Matrix(levels)
    
    # normalise the main effects 
    TopRow = 0
    for f in range(factors): # loop through each factor
        BottomRow = TopRow
        TopRow = TopRow + levels[f] - 1
        # get the orthogonal polynomial contrasts for the given factor
        poly =  sympy.Matrix(orthogpolys[levels[f] - 2]) 
        # calculate the normalising constant for each component
        norm = [sympy.sqrt(sum(([innerItem**2 for innerItem in poly[item,:]])*np.prod(levels))/levels[f]) for item in range(poly.shape[0])]  
        # normalise
        bmat[BottomRow:TopRow,:] = [bmat[BottomRow:TopRow,:][i,:]/norm[i] for i in range(len(norm))] 
    
    # normalise the interactions
    if len(choose2fis) > 0:
        RowIndex = numME
        for i in range(len(choose2fis)): # loop through each interaction
            # get the orthogonal polynomial contrasts for the first factor
            poly1 = orthogpolys[levels[choose2fis[i][0]-1] - 2] 
            # get the orthogonal polynomial contrasts for the second factor
            poly2 = orthogpolys[levels[choose2fis[i][1]-1] - 2] 
            # loop through each main effect contrast of the first factor
            for me1 in range(poly1.shape[0]): 
                # loop through each main effect contrast of the second factor
                for me2 in range(poly2.shape[0]): 
                    # define... a thing
                    poly = [poly1[me1,lv1] * poly2[me2,lv2] for lv1 in range(poly1.shape[1]) for lv2 in range(poly2.shape[1])] 
                    # calculate the normalising constant 
                    norm = sympy.sqrt(sum(([innerItem**2 for innerItem in poly])*np.prod(levels))/(levels[choose2fis[i][0]-1] * levels[choose2fis[i][1]-1]))  
                    bmat[RowIndex,:] = bmat[RowIndex,:]/norm # normalise
                    RowIndex = RowIndex + 1
    
    # construct the lambda matrix, initialise a matrix
    lmat = np.matrix([0 for i in np.arange(t * t)]).reshape(t, t) 
    # initialise an array of indecies
    lind = np.matrix([0 for i in np.arange(p * choicesetsize)]).reshape(p, choicesetsize) 
    
    # get the index for each option in each choiceset
    for ch in range(p): # loop through each choiceset
        EndCol = 0
        for op in range(choicesetsize): # loop thought each option in the choiceset
            StartCol = EndCol
            EndCol = StartCol + factors
            for tmt in range(t): # loop thought each tmt
                if all([choicesets[ch,StartCol+k] == allTmts[tmt,k] for k in range(factors)]): 
                    lind[ch,op] = tmt 
    
    # calculate lambda
    for ch in range(p): # loop through each choiceset
        for i in range(choicesetsize-1): # loop through each option except the last
            for j in range(i+1, choicesetsize): # loop through each remaining option
                lmat[lind[ch,i], lind[ch,j]] = lmat[lind[ch,i], lind[ch,j]] - 1
                lmat[lind[ch,j], lind[ch,i]] = lmat[lind[ch,j], lind[ch,i]] - 1
    
    # calculate the diagonal entries of lambda
    for diag in range(t):
        lmat[diag,diag] = -np.sum(lmat[diag])
    
    lmat = sympy.Matrix(lmat)/(p*(choicesetsize**2))
    
    # Save bmat and lmat.
    rows = ''
    rows += ''.join(str(bmat)).replace('[','').replace(']','').replace(',','')
    outputs['bmat'] = rows
    
    rows = ''
    rows += ''.join(str(lmat)).replace('[','').replace(']','').replace(',','')
    outputs['lmat'] = rows
    
    # Exit if this calc is taking too long.
    if (datetime.now() - START).seconds > MAX_TIME: 
        msg += 'Calculation is taking too long ... exiting.\n'
        outputs['msg'] = msg
        return outputs 
    
    # calculate the c matrix
    try:
        cmat = bmat*lmat*bmat.T # the c matrix
    except:
        msg += 'Unable to calculate the C matrix.\n'
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
    
    cRank = np.linalg.matrix_rank(cmat) # the rank of the c matrix
    
    # Save cmat
    rows = ''
    rows += ''.join(str(cmat)).replace('[','').replace(']','').replace(',','')
    outputs['cmat'] = rows
    
    # check the c matrix is of sufficient rank
    if cRank < numEffects:
        msg += 'The determinant of the C matrix is zero. At least one of the effects cannot be estimated\n'
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
    
    try:
        detc = cmat.det() # the determinant of the c matrix
    except:
        msg += 'Unable to calculate the determinant of the C matrix\n' 
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
    
    msg += 'Det C is: %s \n' % str(float(detc))
    
    try:
        cinv = cmat.inv() # invert the c matrix
    except:
        msg += 'Unable to calculate the inverse of the C matrix\n'  
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
    
    # initialise a matrix
    correln = np.matrix([0 for i in np.arange(numEffects * numEffects)]).reshape(numEffects, numEffects) 
    correln = sympy.Matrix(correln)     # convert to sympy
    for i in range(numEffects):         # loop through each row
        for j in range(numEffects):     # loop through each column
            correln[i, j] = cinv[i, j]/sympy.sqrt(cinv[i, i] * cinv[j, j])
    
    # Save cinv and correln.
    rows = ''
    rows += ''.join(str(cinv)).replace('[','').replace(']','').replace(',','')
    outputs['cinv'] = rows
    
    rows = ''
    rows += ''.join(str(correln)).replace('[','').replace(']','').replace(',','')
    outputs['correln'] = rows
    
    # calculate efficiency
    if detc > 0 and optdet > 0:
        eff = 100*np.power(detc/optdet,sympy.Rational(1, numEffects)) 
        # output to user
        msg += 'Efficiency compared with input det C: %s%% \n' % round(eff, 6)
    
    # initialise a zero matrix
    Block = sympy.Matrix([0 for i in np.arange(numEffects**2)]).reshape(numEffects, numEffects) 
    End = 0
    for f in range(factors): # loop through each factor
        Start = End
        End = Start + levels[f] - 1
        # get the block of main effects
        Block[Start:End, Start:End] = cinv[Start:End, Start:End] 
    for i in range(numInts): # loop through each interactions
        Start = End
        End = Start + np.prod([levels[item-1] - 1 for item in choose2fis[i]])
        # get the block of interactions
        Block[Start:End, Start:End] = cinv[Start:End, Start:End] 
    
    # determine if the main effect are uncorrelated
    MEuncorr = Block[0:numME, 0:numME] == cinv[0:numME, 0:numME] 
    # determine if the interactions are uncorrelated
    Intuncorr = Block[numME:numEffects, numME:numEffects] == cinv[numME:numEffects, numME:numEffects] 
    # determine if the ME are uncorrelated with the intereactions
    MEIntuncorr = cinv[:numME, numME:numEffects] == sympy.Matrix([0 for i in np.arange(numME * num2FI)]).reshape(numME, num2FI) 
    # determine of all effect are uncorrelated
    Alluncorr = Block == cinv 
    
    # output correlation details
    if Alluncorr:
        if factors > 1:
            msg = msg + 'No effects are correlated \n'
    else:
        if MEuncorr:
            msg = msg + 'Main effects are uncorrelated \n'
        else:
            msg = msg + 'Main effects are correlated \n'
        if Intuncorr:
            if numInts > 1:
                msg = msg + 'Two-factor interactions are uncorrelated \n'
        else:
            if numInts > 1:
                msg = msg + 'Two-factor interactions are correlated \n'
        if MEIntuncorr:
            msg = msg + 'Main effects and two-factor interactions are uncorrelated \n'
        else:
            msg = msg + 'Main effects and two-factor interactions are correlated \n'
       
    outputs['msg'] = msg
    return outputs


def ConstructSets_MainEffects(inputs):
    '''
    inputs : a dictionary of all input variables, in this case: 
             levels, msize, tmts, gens, factors
    outputs: a dictionary of all output variables, in this case: 
             msg, chsets, bmat, lmat, cmat, cinv, correln
    '''

    levels = inputs['levels']
    choicesetsize = inputs['msize']
    tmts = inputs['tmts']
    generators = inputs['gens']
    optdet = 1  # optimal det
    
    # Create formatted outputs vars as a dictionary.
    outputs = {}
    
    # The text of this message string will be printed to the browser 
    # to provide an informative message to the user.
    msg = '' 
    
    # calculate a few little bits and pieces
    # The number of factors (k) is calculated from the length of 'levels' 
    factors = len(levels)   # number of factors
    t = len(tmts)           # number of tmt combinations
    g = len(generators)     # number of generators
    numME = sum([lvl - 1 for lvl in levels]) # number of main effect parameters
    numInts = 0     # number of interactions
    num2FI = 0      # number of 2-factor interaction parameters
    numEffects = numME + num2FI; # total number of parameters 
    
    # check number of generators and levels
    if factors != np.shape(generators)[1]/(choicesetsize - 1):
        msg += 'Treatment combinations and generators must have the same number of columns.\n'

    # TODO Emily here factors will always be = length of levels !
    if factors != len(levels):
        msg += 'Treatment combinations and levels must have the same number of columns.\n'
   
    if msg != '':
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
    
    # check the generators
    # reshape first; [(3, 2, 2, 2)] --> [[[3 2 2 2]]]
    generators = np.array([np.reshape(item, (choicesetsize - 1, factors)) for item in generators]) 
    # loop though each generator
    for gen in generators: 
        # reshape the generator into the tmt sets
        gSet = np.reshape(gen, (choicesetsize - 1, factors)) 
        # check that all tmts are unique
        if len(unique(np.matrix(gSet))) != len(gSet): 
            msg += 'Repeated treatment combinations in the set of generators.\n'
        # loop through each tmt in the given generator
        for tmt in gSet: 
            # check the tmt is not all zeros
            if all(tmt == [0 for i in range(factors)]): 
                msg += 'Zero generator in the set of generators.\n'
    
    if msg != '':
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
    
    # convert a few things to myComb type
    tmts = np.array([myComb(val=item, nmod=levels) for item in tmts]) 
    generators = np.array([[myComb(val=chSet, nmod=levels) for chSet in gen] for gen in generators]) 
    
    # Construct the othogonal polynomial contrasts.
    orthogpolys = construct_poly_contrasts()

    # construct a matrix of choicesets
    choicesets = np.array([0 for i in np.arange(t*g * choicesetsize * factors)]).reshape(t*g, choicesetsize, factors)
    
    # get a list of tmt/generator combinations
    gen_tmt = [pair for pair in itertools.product(tmts, generators)] 
    
    # extract the first option (tmt) from the list
    firstOption = [item[0].val for item in gen_tmt] 
    
    # generate the remaining options by adding the generator to the tmt
    remainingOptions = [[row[0] + item for item in row[1]] for row in gen_tmt] 
    
    # loop though each gen/tmt combo
    for ch1 in range(len(gen_tmt)): 
        # assign the first option
        choicesets[ch1][0] = firstOption[ch1] 
        # loop through each generator
        for ch in range(len(remainingOptions[ch1])): 
            # assign the generated option
            choicesets[ch1][ch+1] = remainingOptions[ch1][ch] 
    
    # check that each choiceset is made up of unique tmts
    for i in range(len(choicesets)): # loop through each choice set
        if len(unique(np.matrix(choicesets[i]))) != len(choicesets[i]):
            msg += 'Repeated treatment combination in choice set %d.\n' % (i+1)
   
    if msg != '':
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs
        
    # saved an unordered copy of the choicesets for output (reshaped into a 2D matrix)
    choicesets_out = np.matrix(np.vstack([np.hstack(item) for item in choicesets])) 
   
    # Save choicesets
    rows = '' 
    for row in choicesets_out:
        rows += ''.join(str(row)).replace('[','').replace(']','') + '\n'
    outputs['chsets'] = rows

    allTmts = np.vstack(choicesets) # construct a matrix of all tmt combinations
    allTmts = unique(np.matrix(allTmts)) # remove repeated tmt combos
    t = len(allTmts) # recalculate the number of tmt combinations
    
    # within each choiceset, sort the options lexicographically
    choicesets = [lexico(np.matrix(item)) for item in choicesets] 
    # reshape the choicesets into a 2D matrix
    choicesets = np.vstack([np.hstack(item) for item in choicesets]) 
    
    # check for duplicates
    dup = [] # a list of duplicate choicesets
    # loop through each choiceset except the last
    for i in range(len(choicesets)-1): 
        # loop through each remaining choiceset 
        for j in range(i+1, len(choicesets)): 
            # check if all entries are the same in both choicesets
            if all([choicesets[i,k]==choicesets[j,k] for k in range(np.shape(choicesets[i])[1])]): 
                dup.append(j+1) # append to the list

    if len(dup) > 0:
        if len(dup) == 1:
            msg += 'Warning: choice set %s is a duplicate.\n' % dup[0]
        else:
            tmp = str(list(np.sort(dup))).replace('[','').replace(']','')
            msg += 'Warning: choice sets %s are duplicates.\n' % tmp
    
    choicesets = unique(choicesets) # remove repeated rows (if any)
    p = len(choicesets) # number of unique choice sets
    
    # update output info
    msg += 'Number of choicesets: %d \n' % p
    
    # construct the b matrix
    bmat = np.matrix([0 for i in np.arange(numEffects * t)]).reshape(numEffects, t) 
    
    # define the main effects contrasts
    for tmt in range(t): # loop through each tmt 
        TopRow = 0
        for f in range(factors): # loop through each factor
            BottomRow = TopRow
            TopRow = TopRow + levels[f] - 1
            # get the orthogonal polynomial contrasts for the given factor
            poly = orthogpolys[levels[f] - 2] 
            # assign the main effects
            bmat[BottomRow:TopRow,tmt] = poly[:,allTmts[tmt,f]] 
    
    # convert to sympy
    bmat = sympy.Matrix(bmat)
    levels = sympy.Matrix(levels)
    
    # normalise the main effects 
    TopRow = 0
    for f in range(factors): # loop through each factor
        BottomRow = TopRow
        TopRow = TopRow + levels[f] - 1
        # get the orthogonal polynomial contrasts for the given factor
        poly =  sympy.Matrix(orthogpolys[levels[f] - 2]) 
        # calculate the normalising constant for each component
        norm = [sympy.sqrt(sum(([innerItem**2 for innerItem in poly[item,:]])*np.prod(levels))/levels[f]) for item in range(poly.shape[0])] 
        # normalise
        bmat[BottomRow:TopRow,:] = [bmat[BottomRow:TopRow,:][i,:]/norm[i] for i in range(len(norm))] 
    
    # construct the lambda matrix
    # initialise a matrix
    lmat = np.matrix([0 for i in np.arange(t * t)]).reshape(t, t) 
    # initialise an array of indicies
    lind = np.matrix([0 for i in np.arange(p * choicesetsize)]).reshape(p, choicesetsize) 
    
    # get the index for each option in each choiceset
    for ch in range(p): # loop through each choiceset
        EndCol = 0
        for op in range(choicesetsize): # loop thought each option in the choiceset
            StartCol = EndCol
            EndCol = StartCol + factors
            for tmt in range(t): # loop though each tmt
                if all([choicesets[ch,StartCol+k] == allTmts[tmt,k] for k in range(factors)]): 
                    lind[ch,op] = tmt 
    
    # calculate lambda
    for ch in range(p): # loop through each choiceset
        for i in range(choicesetsize-1): # loop through each option except the last
            for j in range(i+1, choicesetsize): # loop through each remaining option
                lmat[lind[ch,i], lind[ch,j]] = lmat[lind[ch,i], lind[ch,j]] - 1
                lmat[lind[ch,j], lind[ch,i]] = lmat[lind[ch,j], lind[ch,i]] - 1
    
    # calculate the diagonal entries of lambda
    for diag in range(t):
        lmat[diag,diag] = -np.sum(lmat[diag])
     
    lmat = sympy.Matrix(lmat)/(p*np.power(choicesetsize,2))
   
    # Save bmat and lmat.
    rows = ''
    rows += ''.join(str(bmat)).replace('[','').replace(']','').replace(',','')
    outputs['bmat'] = rows
    
    rows = ''
    rows += ''.join(str(lmat)).replace('[','').replace(']','').replace(',','')
    outputs['lmat'] = rows
    
    # Exit if this calc is taking too long.
    if (datetime.now() - START).seconds > MAX_TIME: 
        msg += 'Calculation is taking too long ... exiting.\n'
        outputs['msg'] = msg
        return outputs 
    
    # calculate the c matrix
    try:
        cmat = bmat*lmat*bmat.T # the c matrix
    except:
        msg += 'Unable to calculate the C matrix.\n'
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
        
    cRank = np.linalg.matrix_rank(cmat) # the rank of the c matrix
   
    # Save cmat
    rows = ''
    rows += ''.join(str(cmat)).replace('[','').replace(']','').replace(',','')
    outputs['cmat'] = rows

    # check the c matrix is of sufficient rank
    if cRank < numEffects:
        msg += '''
The determinant of the C matrix is zero. At least one of the effects cannot be estimated\n
Efficiency compared with optimal design for choice set size m = %s: 0%%\n
Efficiency compared with optimal design for optimal choice set size m = %s: 0%%\n''' % (choicesetsize, lcm(levels))
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
    
    try:
        detc = cmat.det() # the determinant of the c matrix
    except:
        msg += 'Unable to calculate the determinant of the C matrix\n' 
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
     
    msg += 'Det C is: %s \n' % str(float(detc))
    
    try:
        cinv = cmat.inv() # invert the c matrix
    except:
        msg += 'Unable to calculate the inverse of the C matrix\n'  
        msg += 'Cannot continue calculation.\n'
        outputs['msg'] = msg
        return outputs 
    
    # initialise a matrix
    correln = np.matrix([0 for i in np.arange(numEffects * numEffects)]).reshape(numEffects, numEffects) 
    correln = sympy.Matrix(correln)     # convert to sympy
    for i in range(numEffects):         # loop through each row
        for j in range(numEffects):     # loop through each column
            correln[i, j] = cinv[i, j]/sympy.sqrt(cinv[i, i] * cinv[j, j])

    # Save cinv and correln.
    rows = ''
    rows += ''.join(str(cinv)).replace('[','').replace(']','').replace(',','')
    outputs['cinv'] = rows

    rows = ''
    rows += ''.join(str(correln)).replace('[','').replace(']','').replace(',','')
    outputs['correln'] = rows

    # calculate the determinant of the optimal design
    prodlevels = np.product(levels)
    Sumdiffs = list(np.repeat(0, factors))
    optdet = 1
    optdet2 = np.power((1/prodlevels), numEffects)
    for q in range(factors):
        if levels[q] == 2:
            if choicesetsize%2 == 0:
                Sumdiffs[q] = np.power(choicesetsize, 2)/4
            else:
                Sumdiffs[q] = (np.power(choicesetsize, 2) - 1)/4
        else:
            if levels[q] >= choicesetsize:
                Sumdiffs[q] = choicesetsize * (choicesetsize - 1)/2
            else:
                x = choicesetsize//levels[q]
                y = choicesetsize%levels[q]
                Sumdiffs[q] = (np.power(choicesetsize, 2) - (levels[q] * np.power(x, 2) + 2 * x * y + y))/2
        optdet = optdet * np.power(((2 * levels[q] * Sumdiffs[q])/(np.power(choicesetsize, 2) * (levels[q] - 1) * prodlevels)), (levels[q] - 1))
    
    # calculate efficiency
    if detc > 0 and optdet > 0:
        eff = 100*np.power(detc/optdet,sympy.Rational(1, numEffects))
        eff2 = 100*np.power(detc/optdet2,sympy.Rational(1, numEffects))
        # output to user
        msg += 'Efficiency compared with optimal design for choice set size m = %s: %s%% \n' % (choicesetsize, round(eff, 6))
        msg += 'Efficiency compared with optimal design for optimal choice set size m = %s: %s%% \n' % (lcm(levels), round(eff2, 6))
    
    # initialise a zero matrix
    Block = sympy.Matrix([0 for i in np.arange(numEffects**2)]).reshape(numEffects, numEffects)
    End = 0
    for f in range(factors): # loop through each factor
        Start = End
        End = Start + levels[f] - 1
        # get the block of main effects
        Block[Start:End, Start:End] = cinv[Start:End, Start:End] 
    
    # Determine if all effects (i.e. the main effects) are uncorrelated.
    # MEuncorr will be True if Block == cinv
    MEuncorr = Block == cinv 
    
    # Output correlation details.
    if MEuncorr:
        if factors > 1:
            msg += 'Main effects are uncorrelated \n'
    else:
        msg += 'Main effects are correlated \n'
   
    outputs['msg'] = msg
    return outputs



##################
# Main starts here
##################

def main():

    # Here we can test if we are runnning from the command line or under the 
    # Bottle web framework. If under Bottle then there will be a 
    # key 'BOTTLE_CHILD' in os.environ; and os.environ['BOTTLE_CHILD'] will be True.
    '''
    if 'BOTTLE_CHILD' in os.environ:
        pass
    else:
        pass
    '''

    ##########################
    # Check program arguments
    ##########################
        
    # There must be three args. 
    if len(sys.argv) != 4: 
        usage()
        print 'Error, number of args must be three.'
        sys.exit()

    # First arg must be a directory which contains the input data files. 
    # We attempt to change into this directory.
    input_dir = sys.argv[1]
    try:
        os.chdir(input_dir)
    except:
        usage()
        print 'Error, input data directory %s does not exist.' % input_dir
        sys.exit()

    # Second arg must be either check or construct i.e. the operation to perform.
    operation = sys.argv[2]
    if operation != 'check' and operation != 'construct':
        usage()
        print 'Error, second arg options must be: check | construct'
        sys.exit()

    # Third arg must be either main, mplusall or mplussome i.e. the effects to estimate.
    effects = sys.argv[3]
    if effects != 'main' and effects != 'mplusall' and effects != 'mplussome':
        usage()
        print 'Error, third arg options must be: main | mplusall | mplussome'
        sys.exit()

 
    ################################################################# 
    # Construct list of expected input files, open them, extract data
    ################################################################# 

    # This is a list of the expected data input and output variables. 
    (expected_inputs, expected_outputs) = get_expected_io(operation, effects)

    # Read in data and do some checking of all input values. 
    # If a file contains nothing or text strings instead of numbers then 
    # the inputs value for that variable will be boolean False.
    inputs = read_input_files(input_dir, expected_inputs)

    #print expected_inputs
    #print inputs
    #print type(inputs['twofis'])

    ######################
    # Perform calculations
    ######################

    # At this stage we expect all inputs to be present. 
    # The program now runs one of these funcs depending on the web input.
    if operation == 'check' and effects == 'main':
        outputs = CheckSets_MainEffects(inputs)
    elif operation == 'check' and effects == 'mplusall':
        outputs = CheckSets_All2fis(inputs)
    elif operation == 'check' and effects=='mplussome':
        outputs = CheckSets_Some2fis(inputs)
    elif operation == 'construct' and effects == 'main':
        outputs = ConstructSets_MainEffects(inputs)
    elif operation == 'construct' and effects == 'mplusall':
        outputs = ConstructSets_All2fis(inputs)
    elif operation == 'construct' and effects == 'mplussome':
        outputs = ConstructSets_Some2fis(inputs)
    else:
        pass

    #actual_outout = outputs.keys()
    #actual_outout.sort()
    #print 'EI: ', expected_inputs   # Expected Input 
    #print 'AI: ', inputs
    #print 'EO: ', expected_outputs  # Expected Output
    #print 'AO: ', actual_outout     # Actual Output

    # Write output files. 
    write_output_files(outputs)

if __name__ == '__main__':
    main()

