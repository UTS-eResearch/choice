%include head
%include top.tpl title='Help Page for Discrete Choice Experiments'

<p><a href="/choice">Return to Choice Experiments</a></p>

<h3>Introduction</h3>
<p>The form allows for either checking the user's own choice sets
or constructing choice sets from a starting design and adding generators.
The theory underpinning the calculations is given in
<blockquote>
&quot;The Construction of Optimal Stated Choice Experiments&quot; <br>
Deborah J. Street, Leonie Burgess <br>
ISBN: 978-0-470-05332-4 <br>
Hardcover, 344 pages <br>
June 2007
</blockquote>
</p>

<p>The computational software is written in Python and we have had to place
time constraints on the matrix calculations.  So choice sets that result in an
information matrix with a challenging structure, may not run to completion.  If
the program runs successfully, the output will include the contrast matrix (B),
the &#923; matrix, the information matrix (C), the determinant of C, the
variance-covariance matrix (C<sup>-1</sup>), and the correlation matrix.  If
the choice sets are to be constructed then the choice sets will also be in the
output. 
</p>

<h3 id="attributes">Attributes:</h3>
<p>
Enter the number of attributes <i>(k)</i> in the choice experiment.
This number must be an integer in the range 1 &lt; k &le; 20.
</p>

<h3 id="levels">Levels for each attribute:</h3>
<p>For each of the attributes enter the number of levels
(<i>l<sub>q</sub></i>, <i>q</i>=1,...,<i>k</i>) in the choice experiment,
separating the numbers with spaces. Each of the  number of levels must be an
integer in the range 2 to 20. <br />
For example, if there are three attributes (<i>k</i> = 3), two with two levels
(<i>l<sub>1</sub></i> = <i>l<sub>2</sub></i> = 2) and one with three levels
(<i>l<sub>3</sub></i> = 3), then enter the levels as  2 2 3.
</p>

<h3 id="msize">Number of options in each choice set:</h3>
<p>Enter the number of options in each choice set <i>(m)</i>.
This number must be an integer in the range 2 to 20.
</p>

<h3 id="corc">What type of operation do you wish to perform?</h3>
<ul>
	<li>If choice sets are to be constructed then the user is required
		to enter a starting design,<br />
		i.e. the treatment combinations, and the sets of generators.
	</li>
	<li>If choice sets are to be checked then these choice sets must
		be entered.
	</li>
</ul>

<h3 id="tmts">Enter the treatment combinations in the starting design:</h3>
<p>The treatment combinations must be entered as a table of numbers, separating
the numbers with spaces.  Each row represents a treatment combination and there
is one column for each attribute.  The numbers in the column for attribute
<i>q</i> can be any integers from 0 up to (<i>l<sub>q</sub></i> - 1), where
<i>l<sub>q</sub></i> is the number of levels for this attribute.
There must be <i>k</i> columns, where <i>k</i> is the number of attributes.
The treatment combinations in the starting design will be used as the
profiles in the first option of the choice sets.
</p>

<p>Starting designs can be obtained from various sources including:
</p>

<ul>
	<li>A Library of Orthogonal Arrays maintained by Neil Sloane at  
    <a href="http://neilsloane.com/oadir/">http://neilsloane.com/oadir/</a>
	</li>
	<li>Orthogonal Arrays maintained by Warren Kuhfeld at
		<a href="http://support.sas.com/techsup/technote/ts723.html">http://support.sas.com/techsup/technote/ts723.html</a>
	</li>
</ul>

<p>Example: Treatment combinations in the starting design for three attributes
(<i>k</i> = 3), two with two levels (<i>l<sub>1</sub></i> = <i>l<sub>2</sub></i> = 2),
and one with three levels (<i>l<sub>3</sub></i> = 3). The numbers in the first
two columns can be 0 or 1, and in the third column the numbers can be 0, 1 or 2.</p>

<p>Enter the treatment combinations in the following form: </p>

<pre>
0 0 0
0 0 1
0 0 2
0 1 0
0 1 1
0 1 2
1 0 0
1 0 1
1 0 2
1 1 0
1 1 1
1 1 2
</pre>

<h3 id="gens">Enter the sets of generators to construct the choice sets:</h3>
<p>Enter the sets of (<i>m</i> - 1) generators as a table of  numbers,
separating the numbers with spaces.
Each row represents one set of generators and must have
(<i>m</i> - 1)<i>k</i>
columns, i.e. (<i>m</i> - 1) generators each of which has <i>k</i> columns,
one for each attribute.
The numbers in the column for attribute <i>q</i> can be any integers from 
0 up to (<i>l<sub>q</sub></i> - 1), where <i>l<sub>q</sub></i>
is the number of levels for this attribute.
At least one set of generators must be entered and a row of all zeros in
invalid.
</p>

<p>Example: For the design with three attributes (<i>k</i> = 3), two with two levels 
(<i>l<sub>1</sub></i> = <i>l<sub>2</sub></i> = 2), and one with three levels 
(<i>l<sub>3</sub></i> = 3), and three options in each choice set <i>(m = 3)</i>,
enter at least one row of (<i>m</i> - 1)<i>k</i> = 6 integers.  The first three
columns represent the generator for constructing the treatment combinations in
the second option of the choice sets, and the second three columns represent
the generator for constructing the treatment combinations in the third option
in the choice sets.  In each generator there are <i>k</i> = 3 columns and the
numbers in the first two of these  columns can be 0 or 1, and in the third
column the numbers can be 0, 1 or 2. </p>

<p>Enter the sets of generators in the following form: </p>

<pre>
1 0 1 0 1 2
1 1 1 1 0 2
</pre>

<h3 id="chsets">Enter the choice sets to be checked:</h3>
<p>The choice sets must be entered as a table of numbers, separating the
numbers with spaces.  Each row represents one choice set and the first <i>k</i>
columns (attributes) represent the treatment combinations in option 1, the
second k columns represent the treatment combinations in option 2, and so on up
to the last <i>k</i> columns which represent the treatment combinations in
option <i>m</i>. The numbers in a  column for attribute <i>q</i> can be any
integers from 0 up to (<i>l<sub>q</sub></i> - 1), where <i>l<sub>q</sub></i> is
the number of levels for this attribute. There must be a total of <i>mk</i>
columns. 
</p>

<p>Example: Choice sets for three attributes (<i>k</i> = 3), two with two
levels  <i>(l<sub>1</sub></i> = <i>l<sub>2</sub></i>), and one with three
levels (<i>l<sub>3</sub></i>) and three options in each choice set 
(<i>m</i> = 3). The numbers in the first or second columns can be 0 or 1, and
in the third column the numbers can be 0, 1 or 2. 
</p>

<p>Enter the choice sets in the following form: </p>

<pre>
0 0 0 1 0 1 0 1 2
0 0 1 1 0 2 0 1 0
0 0 2 1 0 0 0 1 1
0 1 0 1 1 1 0 0 2
0 1 1 1 1 2 0 0 0
0 1 2 1 1 0 0 0 1
1 0 0 0 0 1 1 1 2
1 0 1 0 0 2 1 1 0
1 0 2 0 0 0 1 1 1
1 1 0 0 1 1 1 0 2
1 1 1 0 1 2 1 0 0
1 1 2 0 1 0 1 0 1
</pre>

<h3 id="effect">Which effects do you want to estimate?</h3>
<ul>
	<li>If main effects + all two-factor interactions,
		or main effects + some two-factor interactions is selected then
		a determinant of C to use in the efficiency calculations can
		be entered.
	</li>
	<li>If all of the attributes have two levels and
		main effects + all two-factor interactions is selected then this
		determinant is not required as the optimal design is known.
	</li>
	<li>If the optional determinant is not entered then no efficiency
		can be calculated.
	</li>
</ul>

<h3 id="determinant">Enter determinant of C (optional):</h3>
<p>
As noted above entering the determinant of C is optional.<br />
Examples of the input format style: 17/12524124635136 or 1.35738e-12
The determinant must be in range (0,1).
</p>

<h3 id="twofactor">Enter the two-factor interactions to be estimated:</h3>
<p>Enter the two-factor interactions that are to be estimated in pairs
of numbers, separating the numbers in a pair with a comma.
The two numbers in a pair must be different and have values in the range
[1,k].  For example if there are five attributes and the two-factor
interactions between the first attribute and each of the other
attributes are to be estimated then enter: 1,2 1,3 1,4 1,5.
</p>

<h3 id="notes">Browser Notes:</h3>

<p>This software has been tested on the following browsers:
<ul>
	<li> Firefox 8
	<li> Safari
	<li> Internet Explorer 8
</ul>
</p>

<p>When using Internet Explorer, there is an inconsistency when using
the back button to move from results page back to the original form.
When the back button is pressed it takes you back to the input form,
however it also (partially) resets the form to its default state.
You need to click on the radiobuttons that you previously had selected
(even though they appear to be already selected) to show the hidden
form elements and the data you had previously entered.
</p>

<p>For this reason we recommend using the firefox browser on all platforms
(or the safari browser on MacOSX machines).
</p>

<h3 id="contact">Additional Help:</h3>
<p>
If you are still having troubles using this site please contact us via
<a href="mailto:Leonie.Burgess@uts.edu.au?subject=Help with Choice Experiments.">email (click on this link)</a> giving a description of the problem, the experimental parameters entered,
the type of operation you are trying to perform, and which effects you wish 
to estimate (plus determinant and/or two factor interactions values
if they are specified).
</p>

%include tail
