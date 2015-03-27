#!/usr/bin/env python

'''
This generates the javascript that is required for a given test directory.
You need to manually insert the javascript into examples.js

in_factors.dat 
    4

in_levels.dat
    4 3 3 3

in_msize.dat   
    2

in_chsets.dat   
    0 0 0 0 3 2 2 2
    2 2 0 2 1 1 2 1
    3 0 0 0 2 2 2 2


function check_main_1() {
    allclear();
    show('change'); hide('gen');
    document.getElementById('corc_chk').checked=true;
    document.getElementById('corc_con').checked=false;
    document.getElementsByName('factors')[0].value = 4;
    document.getElementsByName('levels')[0].value = '4 3 3 3';
    document.getElementsByName('msize')[0].value = 2;
    document.getElementsByName('chsets')[0].value = '0 0 0 0 3 2 2 2\n2 2 0 2 1 1 2 1\n3 0 0 0 2 2 2 2';}

Check or construct
document.getElementById('corc_chk').checked = true | false ; // check is checked 
document.getElementById('corc_con').checked = true | false ; // construct is checked 
document.getElementById('effect1').checked = true | false ;  // main effects only
document.getElementById('effect2').checked = true | false ;  // main effects + all two-factor interactions 
document.getElementById('effect3').checked = true | false ;  // main effects + some two-factor interactions 
document.getElementById('id_det').style.display = 'none';    // hide determinant
document.getElementById('id_twofis').style.display = 'none'; // hide two-factor interactions
interactions 

'''

import sys, os, glob


def main():

    # There must be one arg, a path to a test name e.g. 'test/check_main_1'
    if len(sys.argv) != 2: 
        print 'Error, number of args must be one.'
        sys.exit()

    test_dir = sys.argv[1]
    test_dir = test_dir.strip('/')
    test_name = os.path.basename(test_dir)
    js_output  = 'test_%s.js' % test_name
    
    fh_out = open(js_output, 'w')
    fh_out.write(
    '''// Generated automatically from test directory files. 
function %s() {
    allclear();
''' % test_name)

    for file in glob.glob("%s/in_*.dat" % test_dir):
        fh_in = open(file, 'r')
        contents = fh_in.read()
        if os.path.basename(file) == 'in_det.dat': 
            show('id_det'); 
            fh_out.write("    document.getElementsByName('det')[0].value = %s;\n" % contents)
        if os.path.basename(file) == 'in_twofis.dat': 
            show('id_twofis');
            fh_out.write("    document.getElementsByName('twofis')[0].value = %s;\n" % contents)
        if os.path.basename(file) == 'in_gens.dat': 
            fh_out.write("    document.getElementsByName('gens')[0].value = %s;\n" % contents)
        if os.path.basename(file) == 'in_factors.dat': 
            fh_out.write("    document.getElementsByName('factors')[0].value = %s;\n" % contents)
        if os.path.basename(file) == 'in_msize.dat': 
            fh_out.write("    document.getElementsByName('msize')[0].value = %s;\n" % contents)
        if os.path.basename(file) == 'in_levels.dat': 
            fh_out.write("    document.getElementsByName('levels')[0].value = '%s';\n" % contents)
        if os.path.basename(file) == 'in_chsets.dat':
            fh_out.write("    document.getElementById('corc_chk').checked = true;\n")
            fh_out.write("    document.getElementById('corc_con').checked = false;\n")
            contents = contents.strip('\n') 
            contents = contents.replace('\n','\\n')
            fh_out.write("    document.getElementsByName('chsets')[0].value = '%s';\n" % contents)
        if os.path.basename(file) == 'in_tmts.dat':
            fh_out.write("    show('change'); hide('gen');\n")
            fh_out.write("    document.getElementById('corc_chk').checked = false;\n")
            fh_out.write("    document.getElementById('corc_con').checked = true;\n")
            contents = contents.strip('\n') 
            contents = contents.replace('\n','\\n')
            fh_out.write("    document.getElementsByName('tmts')[0].value = '%s';\n" % contents)
        
        fh_in.close()
    
    fh_out.write("}\n")
    fh_out.close()


if __name__ == '__main__':
    main()

