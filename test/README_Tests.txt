Test Cases
==========


Test Name               Example     Approx          Description
                        in Jscript  Time (s) 
---------               -------     --------        -----------

check_main_1            yes         1               Check sets, main only.
check_main_2                        43              Main effects + all 2fis, no det C
check_main_3                       145              Check sets, Main only but long run time. 
    This was used to show an nginx "504 Gateway Timeout" which says:
    "The page you are looking for is temporarily unavailable".

check_mplusall_1                    0.5             Check sets, plusall, det=1  
check_mplusall_2                    0.5             Check sets, plusall, det=blank value
check_mplusall_3                    0.5             Check sets, plusall, det=blank value

check_mplussome_1                   2               Check sets, mplussome, det=1, twofis=1,2 

construct_main_1        yes         1  
construct_main_2        yes         0.5  

construct_mplussome_1   yes         2  
construct_mplussome_2   yes         2  

construct_mplusall_1                0.5

what is test_1()        yes

Scripts
-------

diffdirs.sh      Compares the dat and orig files between two directories.
set_perms.sh     Set all input and original output files to read only.


