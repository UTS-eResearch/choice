%include head
%include top.tpl title='Discrete Choice Experiments'

<p>If you use this software to contruct or check a design please use the
following citation: <br>
&nbsp;&nbsp; Burgess, L. (2007) Discrete Choice Experiments [computer software], <br>
&nbsp;&nbsp; Department of Mathematical Sciences, University of Technology, Sydney, <br>
&nbsp;&nbsp; available from http://maths.science.uts.edu.au/maths/wiki/SPExpts <br>
</p>

<form id="mf" action="/choice/process/" method="post" onsubmit="return verify();"> 
<p>
<input type="button" value="Construct Example 1" onclick="example_1();"/> &nbsp; 
<input type="button" value="Construct Example 2" onclick="example_2();"/> &nbsp; 
<input type="button" value="Construct Example 3" onclick="example_3();"/> &nbsp; 
<input type="button" value="Check Example 4"     onclick="example_4();"/> &nbsp; 
<input type="button" value="Clear" onclick="allclear();" /> &nbsp; 
<a href="/choice/help">Detailed Help Page</a> 
<br>
<input type="button" value="Test 1" onclick="test_1();"/> &nbsp; 

</p>
<p>
<input type="submit"/> 
</p>

<h2>Enter experiment parameters</h2>

<div id="basedata" class="inputdata">
<!-- inputs: factors levels msize -->
<table>
<tr>
    <td align="right">Number of attributes (k): </td>
    <td><input type="text" name="factors" size="1" maxlength="2" value="4"/></td>
    <td>1 &lt;<i>k</i> &le; 20 
    <a class="help" href="#" title="Enter the number of attributes (k) in the choice experiment. This number must be an integer in the range 1 < k ≤ 20." onclick="return false;">?</a>
    </td>
</tr>
<tr>
	<td align="right">Levels for each attribute: </td>
	<td><input type="text" name="levels" size="20" maxlength="60"/ value="4 3 3 3"></td>
	<td>1 x <i>k</i> vector of space separated <br/>integer values in range 2 to 20 
	<a class="help" href="#" title="For each of the attributes enter the number of levels (lq, q=1,...,k) in the choice experiment, separating the numbers with spaces. Each of the number of levels must be an integer in the range 2 to 20. For example, if there are three attributes (k = 3), two with two levels (l1 = l2 = 2) and one with three levels (l3 = 3), then enter the levels as 2 2 3.">?</a> </td>
</tr>
<tr>
	<td align="right">Number of options in each choice set (m): </td>
	<td><input type="text" name="msize" size="1" maxlength="2" value="2" />
	</td>
	<td>1 &lt; <i>m</i> &lt; 20  
	<a class="help" href="#" title="Enter the number of options in each choice set (m). This number must be an integer in the range 2 to 20.">?</a></td>
</tr>
</table>
</div> <!-- end id "basedata" -->

<h2>What type of operation do you wish to perform?</h2>

<div id="corc1" class="radiobuttons">
<!-- inputs: corc[check|construct]--> 
<p>
<input type="radio" id="corc_chk" name="corc" value="check" onclick="show('change'); hide('gen');"/> 
        Check your own choice sets <br>
<input type="radio" id="corc_con" name="corc" value="construct" onclick="show('gen'); hide('change');" checked="checked" /> 
        Construct choice sets 
</p>
</div> <!-- end id "corc1" --> 


<!-- The default "display: block" only if "corc" radio button has default value "check" -->
<!-- inputs: chsets -->
<div id="change" class="inputdata" style="display:none;">
<table>
<tr>
	<td>Enter the Choice Sets to be checked: </td>
</tr>
<tr>
	<td><textarea name="chsets" rows="15" cols="45"></textarea></td>
</tr>
<tr>
	<td>The number of columns must equal <i>m</i> x <i>k</i>. <br />
		There must be at least one row.</td>
</tr>
</table>
</div> <!-- end of id "change" -->


<!-- The default "display: none" only if "corc" radio button has default value "check" -->
<!-- inputs: tmts gens -->
<div id="gen" class="inputdata" style="display:block;">
<table>
<tr>
	<td>Enter the treatment combinations in the <br/> starting design: </td>
	<td>Enter the sets of generators to construct <br/> the choice set: </td>
</tr>
<tr>
	<td><textarea name="tmts" rows="15" cols="45"></textarea></td>
	<td><textarea name="gens" rows="5"  cols="45"></textarea><br>
	There must  be at least one vector entered. <br />
		The length of each vector must equal
		(<i>m</i> - 1) x <i>k</i>. <br />
		A vector consisting of all elements of value 0 is not
		allowed. See detailed help page.
</td>
</tr>
<tr>
	<td style="padding-right:2em;">The number of columns must equal <i>k</i>. <br />
		There must be at least one row. <br />
		The allowed values in each column are determined by
		corresponding values in the &quot;"Levels for each attribute&quot;. <br> 
        See the detailed help page.
	</td>
	<td>&nbsp; 
	</td>
</tr>
</table>
</div> <!-- end of id "gen" --> 

<h2>Which effects do you want to estimate?</h2>

<div id="id_effect" class="radiobuttons">
	<p>
	<input type="radio" id="effect1" name="effect" value="main" checked="checked"
		onclick="hide('id_det'); hide('id_twofis');"/>
		Main effects <br />
	<input type="radio" id="effect2" name="effect" value="mplusall"
		onclick="show('id_det'); hide('id_twofis');"/>
		Main effects + all two-factor interactions <br>
	<input type="radio" id="effect3" name="effect" value="mplussome"
		onclick="show('id_det'); show('id_twofis');"/>
		Main effects + some two-factor interactions <br>
	</p>
</div> <!-- end of id "effect1" -->


<!-- The default is "display: none" only if "effect" radio button has default value "main" -->
<div id="id_det" class="inputdata" style="display:none;">
<table width="100%">
<tr>
	<td align="right" style="width:30%;">Enter determinant of C (optional): </td>
	<td><input type="text" name="det" size="20" maxlength="40"/></td>
	<td>e.g. 17/12524124635136 or 1.35738e-12 <br /> in range (0,1).</td>
</tr>
</table>
</div> <!-- end of id "id_det" -->


<!-- The default is "display: none" only if "effect" radio button has default value "main" -->
<div id="id_twofis" class="inputdata" style="display:none;">
<table width="100%">
<tr>
	<td align="right" style="width:30%;">
        Enter the two-factor <br>interactions to be estimated:
	</td>
	<td><input type="text" name="twofis" size="30" maxlength="100"/></td>
	<td>Pairs of integers in range 1 to <i>k</i> <br> e.g. 1,2 1,3 2,3</td>
</tr>
</table>
</div>


<div id="submission" class="submission">
<input type="submit"/> &nbsp;&nbsp;&nbsp; 
	<!-- XXX it depends what the default corc value is as to which
     	items are shown or not shown. Current set for corc = "check" -->
</div>
</form>
<p>Today's date and time is {{ now }} EST.</p>
<p>Software Version: {{ version }}</p>

%include tail

