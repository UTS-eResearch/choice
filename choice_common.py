'''
Module that contains common functions for the choice experiments programs

Author: Mike Lake
Versions: 
Add a date here and a description of the changes to this file here. If the change
results in a new release at Nectar then document that in the main file choice.py.
2013.10.09: First version. 
2013.10.22: fixed extend vs append error. 
2013.10.23: Added a main() so this program can run independently for debugging. 
2013.10.29: Added sort() to output lists.
2013.11.08: Added write_errors(). 

'''

import sys  # Only needed in main()

def write_errors(errors=''):
    '''
    This appends any unexpected program errors to a file in the same directory 
    as where the data files reside. No newlines are added. 
    This is not for writing messages to the user's web browser.  
    '''
    if errors:
        fh = open('errors.txt', 'a')
        fh.write(errors)
        fh.close()


def get_expected_io (operation, effects):
    '''    
    This returns a tuple. The first member is a list of the expected input
    variables and the second member is a list of the expected output variables. 
    For both we just start with a base list and add to it depending on what
    options the user selected.
    '''

    # Work out the expected inputs and outputs.
    expected_inputs = ['factors', 'levels', 'msize'] 
    expected_outputs = ['bmat', 'cinv', 'correln', 'cmat', 'lmat', 'msg'] 

    # Options for operation are 'check' or 'construct'.
    if operation == 'check':
        expected_inputs.append('chsets')
    elif operation == 'construct':
        expected_inputs.extend(['tmts', 'gens'])
        expected_outputs.append('chsets')
    else:
        pass
   
    # Options for effects are main, mplusall or mplussome.
    if effects == 'main':
        pass
    elif effects == 'mplusall':
        expected_inputs.append('det')
    elif effects == 'mplussome':
        expected_inputs.extend(['det', 'twofis'])
    else:
        pass

    # We sort the output as its easier to compare the expected lists 
    # with actual list if they are sorted alphabetically.  
    expected_inputs.sort() 
    expected_outputs.sort()

    return (expected_inputs, expected_outputs)


def main():

    # There must be just two args:
    # <check | construct> and <main | mplusall | mplussome>
    if len(sys.argv) != 3: 
        print 'This is normally used as a module and not run as a main program.'
        print 'python ./choice_common.py <check | construct> and <main | mplusall | mplussome>'
        sys.exit()
    
    (operation, effects) = (sys.argv[1], sys.argv[2])
    (expected_inputs, expected_outputs) = get_expected_io (operation, effects)
    print 'Inputs:  ', expected_inputs
    print 'Outputs: ', expected_outputs


if __name__ == '__main__':
    main()

