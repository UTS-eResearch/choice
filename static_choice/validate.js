
// Data validation javascript functions
// 2007.00.00: Tony Maher wrote first version.
// 2013.10.03: MRL changed choose2fis to twofis (can't start with numeric).
// 2013.12.03: MRL changed mplus2 to plusall as det validate didn't not work.


// Does the form element have any value or even exist
function hasData(field) {
	with (field)
		{
		if (value==null||value=="")
			{ return false; }
		else
			{ return true; }
		}
	}


// Return the value that a radio button group returns
function radioValue(button) {
	var chosen = "";
	var len = button.length;

	for (i = 0; i <len; i++)
		{
		if (button[i].checked)
			{ chosen = button[i].value }
		}
	return chosen
	}


// Cannot simply do is 'x in array'. It only looks at keys of object
// (like associative array). So create an associative array.
// Taken from http://www.snook.ca/archives/javascript/testing_for_a_v/
// oc stands for object converter.
function oc(a) {
	var o = {};
	for(var i=0;i<a.length;i++)
		{ o[a[i]]=''; }
	return o;
	}


// Cannot use parseInt() as it accepts '2x' as an integer.
// According to manual pp 686 parseInt stops parsing once it sees a non-digit
// in the radix digit set and the value is returned.
// This may be useful if you have strings like "2m/s" but not here!
function isInt(str) { return str.match(/\s*^[-+]?\d+\s*$/); }

function isFraction(str) { return str.match(/^\s*[-+]?\d+\s*\/\s*\d+\s*$/); }

function isExponent(str) { return str.match(/^\s*[-+]?\d+.?\d*[eE][-+]?\d+\s*$/); }

function isDecimal(str) { return str.match(/^\s*[-+]?\d+.?\d*\s*$/); }

function popUp(URL) {
	day = new Date();
	id = day.getTime();
	eval("page" + id + " = window.open(URL, '" + id + "', 'toolbar=0,scrollbars=1,location=0,statusbar=0,menubar=1,resizable=1,width=920,height=800');");
}


// Individual form element check functions
// Separate out as can add onchange verification later.
// xxx will need to rewrite since we pass in values that come from
// verify function that predigests things.

// parseInt safety.
// While parseInt does not really parse integers correctly, it just stops
// at the first character it does not recognize, it is safe to use.  
// o Anything processed by parseInt is just used for comparison tests for
//   limits/sizes. Additionally there is a check like isInt to actually 
//   confirm elements are of correct form.
// o We use parseInt on internally generated values (e.g. index in a for loop)
//   which is safe.


// Check factors
function checkFactors(form, factors, ls) {
	form.factors.className = "valid";
	var msg = '';
	if (!isInt(factors))
		{ msg += "o The " + ls["factors"] + " value is not an integer.\n"; }
	else if (!(factors > 1 && factors < 21))
		{
		msg += "o The " + ls["factors"] +
				" must be between 2 and 20 inclusive.\n";
		}
	if (msg != '')
		{ form.factors.className = "invalid"; }
	return msg
}


// Check levels
function checkLevels(form, levels, factors, ls) {
	var msg = '';
	form.levels.className = "valid";
	if (hasData(form.levels))
		{
		var values = levels.split(/\s+/g)
		var nval = values.length
		// check have correct number of levels
		if (nval > parseInt(factors)) // ok factors is already checked.
			{ msg += "o Too many values for " + ls["levels"] + ".\n"; }
		else if (nval < parseInt(factors)) // ok
			{ msg += "o Too few values for " + ls["levels"] + ".\n"; }
		// check individual levels to make sure in range and integers
		else
			for (i in values)
				{
				val = values[i]
				if (! isInt(val))
					{ msg += "o Non-integer data in " + ls["levels"] + ".\n" }
				if (val < 2 || val > 20)
					{ msg += "o Values in " + ls["levels"] + " out of range.\n"; } 
				}
		}
	else
		{ msg += "o The " + ls["levels"] + " field is empty.\n" }

	if (msg != '')
		{ form.levels.className = "invalid"; }

	return msg
}


// Check msize
function checkMsize(form, msize, ls) {
	form.msize.className = "valid";
	var msg = '';
	if (!isInt(msize))
		{ msg += "o The " + ls["msize"] + " value is not an integer.\n" }
	else if (!(msize > 1 && msize < 21))
		{ msg += "o The " + ls["msize"] + "must be between 2 and 20 inclusive.\n"; }

	if (msg != '')
		{ form.msize.className = "invalid"; }

	return msg
}


// Check chsets
// from Page Info - form box the text area lines are split by a VT
// Number of columns must equal factors x msize
// There must be at least one row (which will be satisfied by above).
function checkChsets(form, chsets, factors, msize, levels, ls) {
	form.chsets.className = "valid";
	var msg = '';
	var lv = levels.split(/\s+/g);
	for (i = 1; i < msize; i++)
		{ lv = lv.concat(lv); }
	if (hasData(form.chsets))
		{
		var rows = chsets.split(/\s*\n/g);
		var elen = factors * msize; // expected row length
		var nline = 0;	// number of lines with data
		loop:
			for (i in rows)
				{
				row = parseInt(i) + 1; // ok internal
				// skip blank lines
				if (rows[i].search(/^\s*$/) != -1)
					{ continue; }
				nline += 1;
				// check the row lengths are correct
				var rlen = rows[i].split(/\s+/g).length;
				if (rlen != elen)
					{
					msg += "o Incorrect row length in " + ls['chsets'] +
						" row " + row + ".\n";
					break loop;
					}
				// Check the individual values in the row
				var cols = rows[i].split(/\s+/g)
				for (j in cols)
					{
					col = parseInt(j) + 1; // ok internal
					val = parseInt(cols[j]) // ok as we use isInt next
					if (! isInt(cols[j]))
						{
						msg += "o In " +  ls['chsets'] + " position (" +
							row + "," + col + ") the value " + cols[j] +
							" is not an integer.\n";
						}
					else if (val < 0 || val >= lv[j])
						{
						msg += "o In " +  ls['chsets'] + " position (" +
							row + "," + col + ") the value " + cols[j] +
							" is invalid.\n";
						break loop;
						}
					}
				}
			// loop breaks to here.
		// check that there was something other than blank lines
		if (nline == 0)
			{ msg += "o Only blank lines in " + ls['chsets'] + ".\n"; }
		}
	// completely empty data
	else
		{ msg += "o No data in " + ls['chsets'] + ".\n"; }

	if (msg != '')
		{ form.chsets.className = "invalid"; }

	return msg
}


// Check tmts
// Number of columns must equal factors
// Must be at least one row (which will be satisifed by above).
// The allowed range for values in each column is detemined by
// the corresponding value in the levels vector.
function checkTmts(form, tmts, factors, msize, levels, ls) {
	form.tmts.className = "valid";
	var msg = '';
	var lv = levels.split(/\s+/g);

	if (hasData(form.tmts))
		{
		var rows = tmts.split(/\s*\n/g);
		var elen = factors; // expected row length
		var nline = 0;	// number of lines with data
		loop:
			for (i in rows)
				{
				row = parseInt(i) + 1; // ok internal
				// skip blank lines
				if (rows[i].search(/^\s*$/) != -1)
					{ continue; }
				nline += 1;
				// check the row lengths are correct
				var rlen = rows[i].split(/\s+/g).length;
				if (rlen != elen)
					{
					msg += "o Incorrect row length in " + ls['tmts'] +
						" row " + row + ".\n";
					break loop;
					}
				// Check the individual values in the row
				var cols = rows[i].split(/\s+/g);
				for (j in cols)
					{
					col = parseInt(j) + 1; // ok internal
					val = parseInt(cols[j]) // ok as use isInt next
					if (! isInt(cols[j]))
						{
						msg += "o In " +  ls['tmts'] + " position (" +
							row + "," + col + ") the value " + cols[j] +
							" is not an integer.\n";
						}
					else if (val < 0 || val >= lv[j])
						{
						msg += "o In " +  ls['tmts'] + " position (" +
							row + "," + col + ") the value " + cols[j] +
							" is invalid.\n";
						break loop;
						}
					}
				}
			// loop breaks to here.
		// check that there was something other than blank lines
		if (nline == 0)
			{ msg += "o Only blank lines in " + ls['tmts'] + ".\n"; }
		}
	// completely empty data
	else
		{ msg += "No data in " + ls['tmts'] + ".\n" }

	if (msg != '')
		{ form.tmts.className = "invalid"; }

	return msg
}


// Check gens
// There must be at least one row.
// The length of each vector must equal factors x (msize -1)
function checkGens(form, gens, factors, msize, levels, ls) {
	form.gens.className = "valid";
	var msg = '';
	var lv = levels.split(/\s+/g);
	for (i = 1; i < msize - 1; i++)
		{ lv = lv.concat(lv); }
	if (hasData(form.gens))
		{
		var rows = gens.split(/\s*\n/g);
		var elen = (msize - 1) * factors; // expected row length
		var nline = 0;	// number of lines with data
		loop:
			for (i in rows)
				{
				row = parseInt(i) + 1; // ok internal
				// skip blank lines
				if (rows[i].search(/^\s*$/) != -1)
					{ continue; }
				nline += 1;
				// check the row lengths are correct
				var rlen = rows[i].split(/\s+/g).length;
				if (rlen != elen)
					{
					msg += "o Incorrect row length in " + ls['gens'] +
						" row " + row + ".\n";
					break loop;
					}
				// Check the individual values in the row
				var cols = rows[i].split(/\s+/g)
				var nonzero = 'false';
				for (j in cols)
					{
					col = parseInt(j) + 1; // ok internal
					val = parseInt(cols[j]) // ok as use isInt below
					if (val != 0)
						{ nonzero = 'true' }
					if (! isInt(cols[j]))
						{
						msg += "o In " +  ls['gens'] + " position (" +
							row + "," + col + ") the value " + cols[j] +
							" is not an integer.\n";
						}
					else if (val < 0 || val >= lv[j])
						{
						msg += "o In " +  ls['gens'] + " position (" +
							row + "," + col + ") the value " + cols[j] +
							" is invalid.\n";
						break loop;
						}
					}
				if (nonzero == 'false')
					{ 
					msg += "o In " +  ls['gens'] +
						" one row is all zeros which is not allowed.\n";
					}
				}
			// loop breaks to here.
		// check that there was something other than blank lines
		if (nline == 0)
			{ msg += "o Only blank lines in " + ls['gens'] + ".\n"; }
		}
	// completely empty data
	else
		{ msg += "No data in " + ls['gens'] + ".\n" }

	if (msg != '')
		{ form.gens.className = "invalid"; }

	return msg
}


// Check det
// This is optional and can be expressed as a fraction.
// xxx what is valid range?
function checkDet(form, det, ls) {
	form.det.className = "valid";
	var msg = '';
	if (hasData(form.det))
		{
		if (!(isFraction(det) || isExponent(det) || isDecimal(det)))
			{
			msg += "o The " + ls["det"] + " is not a fraction" +
				" or in exponent form\n";
			}
		else if ((eval(det) < 0) || (eval(det) > 1))
			{ msg += "o The " + ls["det"] + " is outside range (0,1).\n"; }
		}
	// optional so does not matter if it does not exist.
	if (msg != '')
		{ form.det.className = "invalid"; }

	return msg
}


// Check twofis
// These are pair of integers separated by ',' and the pairs are
// separated by whitespace e.g. 1,2 3,4 1,3
// Only print out first error detected.
function checkFactor2(form, twofis, ls) {
	form.twofis.className = "valid";
	var msg = '';
	if (hasData(form.twofis))
		{
		var pairlist = twofis.split(/\s+/g);
		loop:
			for (var i in pairlist)
				{
				var vals = pairlist[i].split(',');
				if (vals.length != 2)
					{
					msg += "o In " + ls['twofis'] +
							" there is an invalid format\n";
					break loop;
					}
				for (var j in vals)
					{
					if (! isInt(vals[j]))
						{
						if (vals[j] == '')
							{ msg += "o In " + ls['twofis'] +
								" there is a missing value.\n"; }
						else
							{ msg += "o In " + ls['twofis'] + " " + vals[j] +
								" is not an integer\n"; }
						break loop;
						}
					}
				}
			// break loop to here
		}
	else
		{ msg += "o In " + ls['twofis'] + " there are no valid pairs.\n." }

	if (msg != '')
		{ form.twofis.className = "invalid"; }

	return msg
}


// Verify the form - note need to do in cgi-bin program as well
// to catch people who do not use the form.
function verify() {
	var MSG = "Discrete Choice Experiment.\n";
	var msg = "";

	// For convenience, get the values for the components of the form
	// into a simple var
	var form = document.forms[0];
	var factors = form.factors.value.replace(/^\W+/,'').replace(/\W+$/,'');
	var levels = form.levels.value.replace(/^\W+/,'').replace(/\W+$/,'');
	var msize = form.msize.value.replace(/^\W+/,'').replace(/\W+$/,'');
	var chsets = form.chsets.value.replace(/^\W+/,'').replace(/\W+$/,'');
	var tmts = form.tmts.value.replace(/^\W+/,'').replace(/\W+$/,'');
	var gens = form.gens.value.replace(/^\W+/,'').replace(/\W+$/,'');
	var det = form.det.value.replace(/^\W+/,'').replace(/\W+$/,'');
	var twofis = form.twofis.value.replace(/^\W+/,'').replace(/\W+$/,'');

	// mapping between form element name and what its label is.
	var ls = {
			"factors": "'Number of attributes'",
			"levels":  "'Levels for each attribute'",
			"msize":   "'Number of options in each choice set'",
			"chsets":  "'Choice Sets'",
			"tmts":    "'Treatment combinations'",
			"gens":    "'Sets of generator'",
			"det":     "'Determinant'",
			"twofis":  "'2 pair factors'"
			};

	// Because the form hide/display different parts of the form
	// depending on what radiobuttons are selected, we need to only
	// check the relevant form elements. There are two separate
	// radiobuttons groups.
	var expect = ["factors", "levels", "msize"];

	corc = radioValue(form.corc);     // check or construct
	effect = radioValue(form.effect); // main, mplus2 or mplussome

	if (corc == "check")
		{ expect = expect.concat("chsets") }
	else
		{ expect = expect.concat("tmts", "gens") }

	if (effect == "mplusall")
		{ expect = expect.concat("det") }
	else if (effect == "mplussome")
		{ expect = expect.concat("det", "twofis") }

	// Mandatory Checks
	msg += checkFactors(form, factors, ls);
	msg += checkLevels(form, levels, factors, ls);
	msg += checkMsize(form, msize, ls);

	// Only do more checking if mandatory checks ok, else get spurious
	// warnings. Also saw some extended processing time that looked like
	// browser had locked up but it eventually returned.
	if (msg == '') {
		// Optional Checks - depends on radiobutton selection.
		var oexpect = oc(expect);  // convert to assoc. array i.e. an object

		if ("chsets" in oexpect)
			{ msg += checkChsets(form, chsets, factors, msize, levels, ls) }
		if ("tmts" in oexpect)
			{ msg += checkTmts(form, tmts, factors, msize, levels, ls) }
		if ("gens" in oexpect)
			{ msg += checkGens(form, gens, factors, msize, levels, ls) }
		if ("det" in oexpect)
			{ msg += checkDet(form, det, ls) }
		if ("twofis" in oexpect)
			{ msg += checkFactor2(form, twofis, ls) }
	}

	// Finish. Print any messages and return appropriate state.
	if (msg == '')
		return true;
	else {
		MSG += msg;
		alert(MSG);
		return false;
	}
}
