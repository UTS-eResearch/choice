#!/usr/bin/env python

'''
Discrete Choice Experiments for Deborah Street and Leonie Burgess
Author: Mike Lake, eResearch UTS
Copyright 2013-2015 Mike Lake

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Versions: 
2013.08.28: First draft.
2013.09.29: First version working at Nectar.
2013.10.02: Write all input files.
2013.10.04: Removed writing out_code.dat.
2013.10.08: Added read_output_files. Release to Nectar.
2013.10.09: Moved functions common to choice.py & process_choices.py to a module. 
            Added remaining form values to get_form_data(). 
            Added final_validation(). errors.tpl page changed errors to a simple string.
            Removed return_code.
2013.10.10: Lots of validation code added. Release to Nectar.
2013.10.22: Added DEBUG flag and debug to results template.
            Release to Nectar.
2013.10.23: Release to Nectar.
2013.10.24: Added time taken. Changed Censoc logo to Maths logo.
2013.10.29: Changed inputs_validation() to return useful strings. 
2013.10.30: Added an errors.txt file. Release to Nectar. 
2013.11.08: Added try in opening output files. Moved creating a debug temp dir
            to inside of try. Added validation for det. 
2013.11.15: Changed DEBUG to TEST. Release to Nectar.
2013.11.18: Added check for permission denied on executable. Release to Nectar.
2013.11.21: Release to Nectar.
2013.11.27: Added check for negative ints for levels. Added try to catch missing
            form elements. Added check that twofis values are in range 1,k.
            Release to Nectar.
2013.12.03: Changed in validate.js; mplus2 to mplusall. Release to Nectar.
2014.01.07: Added bottle.app() at end of main to run as WSGI. Release to Nectar. 
2014.09.08: Version info is now in github
            Release to Nectar.
2014.10.10: Fixed display of det entered as per Emily's request. 
            Release to Nectar.
2014.10.13: Added timeout.  
            Release to Nectar.
2015.06.30: Timeout set for long running calculations.
            Release to Nectar.

Don't forget to update version number below!
'''

version = '2015.06.30'


from bottle import route, run, template, request
from bottle import static_file
from bottle import debug
from bottle import FlupFCGIServer
import bottle    # added for bottle.app()

# subprocess is the native one for Pyth0n 2.7 but I have installed subprocess32
# which is a backport from Python 3.0 which supports a timeout arg. 
import subprocess32 as subprocess

import os, datetime
from tempfile import mkdtemp
import shutil   # for removing a dir tree
import datetime
import re       # only used once in validation

# Our own modules
from choice_common import get_expected_io, write_errors

TIMEOUT = 300 # the maximum time in seconds for a process_choices.py to run 

# Test for test or not. Just touch TEST.
# and remove the file TEST to go back to production.
# If TEST is True then the following will change:
# - the app will run under a local fastcgi server,
# - the temp dir will be a local one in your current directory,
# - files in the temp dir will not be deleted at the end of the script.
if os.path.isfile('TEST'):
    TEST = True
else:
    TEST = False


def get_form_data(request):
    '''
    Get ALL the forms data that we expect and return a dictionary where the 
    keys are the form variables. Example: a form with e.g. 
    <input type="text" name="factors"/> will be got with request.forms['factors']
    Some form validation is done with javascript on the form page but nasty users 
    can subvert these checks. What we do here is: 
    * If the form contains a name that we don't expect such as 
      <input name="blah" value="nasty.js" /> then it won't be included in the 
      returned inputs dict. 
    * If a user does not enter a value in a form (e.g. for an optional input) then
      the value will be an empty string. 
    '''
    input = {}

    try:
        # Base data
        input['factors'] = request.forms['factors']
        input['levels'] = request.forms['levels']
        input['msize'] = request.forms['msize']
    
        # Data if constructing your own sets.
        input['gens'] = request.forms['gens']
        input['tmts'] = request.forms['tmts']
    
        # Data if checking a set.
        input['chsets'] = request.forms['chsets']
    
        # Data if more effects are requested.
        input['det'] = request.forms['det']
        input['twofis'] = request.forms['twofis']
    
        # Radio buttons 
        input['corc'] = request.forms['corc']
        input['effect'] = request.forms['effect']
    except KeyError:
        # Occurs if the web page is missing one of the above form elements. 
        # This should really never occur unless someone messes with the submitted page.  
        return False

    return input


def write_input_files(inputs, tempdir):
    '''
    inputs is a dict where the keys are the input variable names and
    the key values are their values - in most cases as a string. 
    tempdir is the directory where these files should be found. 
    The inputs are written to files which the choice program reads.  
    Example: levels:'4 3 3 3' will write to file in_levels.dat

    Key        Filename
    ---        --------
    factors    in_factors (k) <-- calculated from the length of 'levels' instead
    levels     in_levels.dat    e.g. 4 3 3 3
    msize      in_msize.dat     e.g. 2
    chsets     in_chsets.dat    e.g. 4 x 16 matrix 
    tmts       in_tmts.dat      e.g. 4 x 16 matrix 
    gens       in_gens.dat      e.g. 3 2 2 2
    det        in_det.dat       e.g. 1
    twofis     in_twofis.dat    e.g. 1,2 1,3 1,4 1,5

    Note: if the user does not enter anything for an optional input 
    then the file for that will be created but it will be empty.
    '''

    for key in inputs.keys():
        filename = 'in_' + key + '.dat'
        filepath = os.path.join(tempdir, filename)
        fh = open(filepath, 'w')
        fh.write(inputs[key])
        fh.close()

    # Make sure there exists an errors file. The contents of this are 
    # never written to the users browser except for testing. 
    filepath = os.path.join(tempdir, 'errors.txt')
    fh = open(filepath, 'w')
    fh.write('')
    fh.close()

    return 0

    
def read_output_files(outputs_to_read, tempdir):
    '''
    args are a list of variables to read and a directory where the files are.
    We return a dictionary where the keys are the variables and the values 
    are the files contents.
    Q. What happens if the dict lists a variable but it's file does not exist?
    like we expect cinv but there is no out_cinv.dat ? 
    A. Just create a None value for it.
    '''

    outputs = {}
    for name in outputs_to_read:
        filename = 'out_' + name + '.dat'
        filepath = os.path.join(tempdir, filename)
        try:
            fh = open(filepath, 'r')
            data = fh.read()
            fh.close()
        except IOError as e:
            data = None
            # TODO 2014.09.15 temp disable this as we are getting a permissions problem.
            #write_errors('Output file: %s (%s)\n' % (filename, e))

        outputs[name] = data

    # Read contents of the errors file. This should always exist.
    # TODO after all is OK place this in an if TEST
    outputs['errors'] = ''
    filepath = os.path.join(tempdir, 'errors.txt')
    fh = open(filepath, 'r')
    outputs['errors'] = fh.read()
    fh.close()

    return outputs


def inputs_validation(inputs):
    '''
    We need to check the following input keys which should be matrices of integers:
        factors, msize, levels, chsets, gens, tmts, twofis, 
    and this one only can be int, float, fraction or exponential notation in range (0,1):
        det, 
    and these inputs should be known text:
        corc, effect

    If anything is wrong immediately return a plain text string, being a
    message that will be displayed to the user.   
    If all is OK we should return False. 
    '''

    # Check radio buttons of name="corc". They must be either "check" or "construct".
    if inputs['corc'] != 'check' and inputs['corc'] != 'construct':
        return 'Problem with radio buttons. Not either check or construct.'
    
    # Check radio buttons of name="effect". They must be either "check" or "construct".
    if inputs['effect'] != 'main' and inputs['effect'] != 'mplusall' and inputs['effect'] != 'mplussome':
        return 'Problem with effects selected. Not either main or mplusall or mplussome.'

    # Check name="det". 
    # It must be either integer, float, fraction or exponential or just blank. 
    # e.g. 0 or 1 or 0.123 or 17/12524124635136 or 1.35738e-12 in range (0,1) or '' or ' '.
    # TODO maybe we should check for key in this dict.
    if inputs['det']:
        det = inputs['det']
        det_is_OK = False

        # Here we try an int, float or exponent e.g. '1' or '0.12' or '1.2e-12'.
        try:
            float(det)        # ValueError if not castable to float. 
            det_is_OK = True
        except ValueError:
            # It's not int, float or exponent, still might be '' or ' ' or a fraction.
            pass 
        # Here we try a fraction     
        try: 
            (numerator, denominator) = det.split('/') # ValueError if can't split.
            float(numerator)      
            float(denominator)
            det_is_OK = True
        except ValueError:
            # It's not a fraction, still might be  '' or ' '.
            pass
        # Here we try a blank or nothing.
        pat = re.compile('\s*$') # will match just nothing or only whitespace
        if re.match(pat, det):
            # Matches blank so OK
            det_is_OK = True

        if det_is_OK: 
            pass
        else:
            return 'Problem with determinant, not integer or fraction or exponent or blank.'

    # Check name="factors" 1 < k <= 20 
    # This is checked in the js but we need to get its value here anyways as 
    # we check in this func that each twofix is <= factors.
    if inputs['factors']:
        try:
            factors = int(inputs['factors'])
        except ValueError:
            return 'Problem with factors, not an integer.'
    
    # Check name="twofis". 
    # Must be positive integers, can be separated by white space and/or commas.
    # We split the string on whitespace or commas and we should then have a list of 
    # integers as strings. For each one we try to convert to integers.   
    # We also check they are in range 1 to k (k=factors). 
    if inputs['twofis']:
        sep = re.compile('[\s,]+')
        temp_list = re.split(sep, inputs['twofis'])
        for item in temp_list:
            try:
                temp = int(item)
                if temp < 1:
                    return 'Problem with two-factor interactions, some items are < 1'
                if temp > factors:
                    return 'Problem with two-factor interactions, some items are > k.'
            except ValueError:
                return 'Problem with two-factor interactions, some items are not positive integers.'
 

    # Check all remaining inputs. Must be integers separated by white space and newlines.
    remaining = ['levels','msize','chsets','tmts','gens']
    temp_list = [] 
    for key in remaining:
        # print key, type(inputs[key]) # shows the matrices are all strings
        # print inputs[key].split()
        if key in inputs.keys():
            temp_list = temp_list + inputs[key].split()

    temp_set = set(temp_list)
    for item in temp_set:
        try:
            int(item)
        except ValueError:
            return 'Problem something is not an integer in one of factors, levels, msize, chsets, tmts or gens.'

    # All inputs are probably OK
    return False



#####################
# Routes defined here
#####################

# A route decorator @route() binds a piece of code to a URL path.

# Serve static files such as CSS, images and javascript.
@route('/static_choice/<filename:path>')
#@route('/static/:filename#.*#')
#@route('/static/')
def static(filename):
    return static_file(filename, root='./static_choice/')


# Serve a help page.
@route('/choice/help')
@route('/choice/help/')
def help():
    return template('help')


# This is not used.
@route('/choice/e504')
@route('/choice/e504/')
def error504():
    now = datetime.datetime.now().strftime('%y.%m.%d   %I:%M:%S %P')
    return template('error_page', errors='A timeout occurred.', now=now)


# Serve a simple test page.
@route('/choice/test')
@route('/choice/test/')
@route('/choice/test/<name>')
@route('/choice/test/<name>/')
def test(name='Mike'):
    now = datetime.datetime.now().strftime('%Y.%m.%d  %I:%M:%S %P')
    page='''
    <html>
    <body>
    <h2>Choice Test Page </h2>
    <p>Time: %s </p>
    <p>Name: %s </p>
    </p>
    </body>
    </html>
    '''  % (now, name)
    return page


# Serve main entry point page. 
@route('/')
@route('/choice')
@route('/choice/')
def start_page():
    now = datetime.datetime.now().strftime('%Y.%m.%d at %I:%M:%S %P')
    return template('start_page', now=now, version=version)


# Process the submission. 
@route('/choice/process',  method='POST')
@route('/choice/process/', method='POST')
def process():
    now = datetime.datetime.now().strftime('%y.%m.%d   %I:%M:%S %P')

    # We get take the request object which contains all input fields from 
    # the submission page, including any that the user may have added :-)
    # The get_form_data() only returns input fields that we might expect,  
    # including optional fields. Any of the fields could still be empty 
    # or contain invalid data. 
    inputs = get_form_data(request)
    if not inputs:
        return template('error_page', errors='A form input value is missing.', now=now)

    # Here we do data input validation. If there are no errors then 
    # inputs_validation() will return False, otherwise it will return an error.
    errors = inputs_validation(inputs)
    if errors:
        # It returned something other than False so we don't write any files to disk! 
        # Send these messages to the users web browser and end immediately.
        errors = 'Your input data did not pass validation.\n' + errors
        return template('error_page', errors=errors, now=now)
    else:
        # Returned False so all inputs are OK. We can proceed.
        pass

    # Work out what is being asked for e.g. 'construct', 'main' etc. 
    operation = inputs['corc']
    effect = inputs['effect']
    (inputs_to_write, outputs_to_read) = get_expected_io(operation, effect)
    
    # The keys in inputs must match expected inputs_to_write.
    # Form inputs that will not be used can be deleted. 
    for key in inputs.keys():
        if key not in inputs_to_write:
            del inputs[key]

    # Inputs are OK so now create a temp directory and write the input files.
    try:
        if TEST:
            tempdir = 'temp'    # Use a local temp dir.
        else:
            tempdir = mkdtemp(dir='/tmp', prefix='choice.')
    except:
        errors = 'Error: unable to create temporary directory.'
        return template('error_page', errors=errors, now=now)

    # Writes input files to the tempdir.  
    write_input_files(inputs, tempdir)

    # We will time how long the processing takes. 
    start_time = datetime.datetime.now()
    
    # Here is where we run the program that calculates the "discrete choices".
    # It reads it's input data and writes it's output data as files from /tmp
    # subprocess.call(args, *, stdin=None, stdout=None, stderr=None, shell=False, timeout=None)
    try:
        subprocess.check_output(['./process_choices.py', tempdir, operation, effect], stderr=subprocess.STDOUT, timeout=TIMEOUT)
    except subprocess.CalledProcessError as e: 
        # Just return a simple string rather than a dict like errors['output']. 
        errors = 'Error: %s (returncode %d)' % (e.output, e.returncode) 
        return template('error_page', errors=errors, now=now)
    except subprocess.TimeoutExpired as e:
        # Command '['./process_choices.py', 'temp', 'construct', 'main']' timed out after 5 seconds
        errors = 'Error: the calculation was taking too long so it had to be ended. The maximum time allowed is %d seconds.' % TIMEOUT
        return template('error_page', errors=errors, now=now)
    except OSError as e: 
        errors = 'Error: %s ' % e 
        return template('error_page', errors=errors, now=now)
    

    # Get the finishing time as a timedelta object.
    dt = datetime.datetime.now() - start_time
    tt = '%.2f' % dt.total_seconds()  # time taken 

    outputs = read_output_files(outputs_to_read, tempdir)

    # Cleanup but only if not in TEST mode. 
    if not TEST:
        shutil.rmtree(tempdir)
    
    # Return results page. 
    return template('results_page', inputs=inputs, outputs=outputs, time=tt, test=TEST)


#####################
# Run the application
#####################


if TEST:
    # If debug(True) uncommented then Exception and Traceback output 
    # will go to the web browser screen.
    debug(True)
    # Use this to run using Bottle's inbuilt server. 
    run(host='localhost', port=8080, reloader=True )
else:
    # Use this to run under a FastCGI server on a TCP port. 
    # This host & port must also be specified in the nginx conf file for this site. 
    # and the nginx service must be running.  
    #run(server=FlupFCGIServer, port=9000, host='localhost')
    # Now see it at: http://localhost:9090/choice

    # https://groups.google.com/forum/#!topic/bottlepy/wRfgm4obLXk
    application = bottle.app()

