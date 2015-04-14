
// Example input data for choice experiments.
// 2013.10.09: MRL added examples to here.
// 2013.10.22: MRL fixed example 3.
// 2013.11.08: Added hide id_det & id_twofis to allclear(), added allclear() to all examples. 
// 2013.11.18: Added set effect1,2,3 to "Check", added clearing twofis value.
//             Renamed fact2 to id_twofis


// Clears values from input boxes.
function allclear() {
	//var elem = document.getElementsByName('factors')[0];
    //elem.value = null;
	document.getElementsByName('factors')[0].value = null;
	document.getElementsByName('levels')[0].value = null;
	document.getElementsByName('msize')[0].value = null;
	document.getElementsByName('tmts')[0].value = null;
	document.getElementsByName('gens')[0].value = null;
	document.getElementsByName('chsets')[0].value = null;
	document.getElementsByName('det')[0].value = null;
	document.getElementsByName('twofis')[0].value = null;
    // Set "Which effects do you want to estimate?" to "Main effects".
    document.getElementById('effect1').checked = true;
    document.getElementById('effect2').checked = false;
    document.getElementById('effect3').checked = false;
    // Hide det and twofis input boxes 
    document.getElementById('id_det').style.display = 'none';
    document.getElementById('id_twofis').style.display = 'none';
    show('change'); hide('gen');
    // Set default to be check sets
    check_sets();
}
    
function check_sets() {
    // Set "What type of operation do you wish to perform?" to "Check"
    document.getElementById('corc_chk').checked = true;
    document.getElementById('corc_con').checked = false;
}

function construct_sets() {
    // Set "What type of operation do you wish to perform?" to "Construct"
    document.getElementById('corc_chk').checked = false;
    document.getElementById('corc_con').checked = true;
}


function check_main_1() {
    allclear();
    show('change'); hide('gen');
	document.getElementsByName('factors')[0].value = 4;
	document.getElementsByName('levels')[0].value = '4 3 3 3';
	document.getElementsByName('msize')[0].value = 2;
	document.getElementsByName('chsets')[0].value = '0 0 0 0 3 2 2 2\n2 2 0 2 1 1 2 1\n3 0 0 0 2 2 2 2\n1 1 0 1 0 0 2 0\n1 0 2 0 0 2 1 2\n3 2 1 0 2 1 0 2\n2 1 0 0 1 0 2 2\n0 0 0 2 3 2 2 1\n3 0 0 1 2 2 2 0\n0 2 2 1 3 1 1 0\n1 2 0 0 0 1 2 2\n1 0 1 2 0 2 0 1\n2 0 2 0 1 2 1 2\n2 0 1 1 1 2 0 0\n3 1 2 2 2 0 1 1\n0 1 1 0 3 0 0 2';
}

function construct_main_1() {
    allclear(); construct_sets();
    show('gen'); hide('change');
	document.getElementsByName('factors')[0].value = 4;
	document.getElementsByName('levels')[0].value = '4 3 3 3';
	document.getElementsByName('msize')[0].value = 2;
	document.getElementsByName('gens')[0].value = '3 2 2 2';
	document.getElementsByName('tmts')[0].value = '0 0 0 0\n2 2 0 2\n3 0 0 0\n1 1 0 1\n1 0 2 0\n3 2 1 0\n2 1 0 0\n0 0 0 2\n3 0 0 1\n0 2 2 1\n1 2 0 0\n1 0 1 2\n2 0 2 0\n2 0 1 1\n3 1 2 2\n0 1 1 0';
    document.getElementById('effect1').checked = true;
    document.getElementById('effect2').checked = false;
    document.getElementById('effect3').checked = false;
}

function construct_main_2() {
    allclear(); construct_sets();
    show('gen'); hide('change');
	document.getElementsByName('factors')[0].value = 2;
	document.getElementsByName('levels')[0].value = '2 2';
	document.getElementsByName('msize')[0].value = 2;
	document.getElementsByName('gens')[0].value = '1 1';
	document.getElementsByName('tmts')[0].value = '0 0\n0 1\n1 0\n1 1';
}

function construct_mplussome_1() {
    allclear(); construct_sets();
    show('gen'); hide('change');
    show('id_det'); show('id_twofis');
    document.getElementById('effect1').checked = false;
    document.getElementById('effect2').checked = false;
    document.getElementById('effect3').checked = true;
	document.getElementsByName('det')[0].value = 1;
	document.getElementsByName('factors')[0].value = 4;
	document.getElementsByName('levels')[0].value = '4 3 3 3';
	document.getElementsByName('msize')[0].value = 2;
	document.getElementsByName('gens')[0].value = '3 2 2 2';
	document.getElementsByName('tmts')[0].value = '0 0 0 0\n2 2 0 2\n3 0 0 0\n1 1 0 1\n1 0 2 0\n3 2 1 0\n2 1 0 0\n0 0 0 2\n3 0 0 1\n0 2 2 1\n1 2 0 0\n1 0 1 2\n2 0 2 0\n2 0 1 1\n3 1 2 2\n0 1 1 0';
	document.getElementsByName('twofis')[0].value = '1,2';
}

function construct_mplussome_2() {
    allclear(); construct_sets();
    show('gen'); hide('change');
    show('id_det'); show('id_twofis');
    document.getElementById('effect1').checked = false;
    document.getElementById('effect2').checked = false;
    document.getElementById('effect3').checked = true;
	document.getElementsByName('factors')[0].value = 2;
	document.getElementsByName('levels')[0].value = '2 2';
	document.getElementsByName('msize')[0].value = 2;
	document.getElementsByName('gens')[0].value = '0 1\n1 1';
	document.getElementsByName('tmts')[0].value = '0 0\n0 1\n1 0\n1 1';
	document.getElementsByName('twofis')[0].value = '1,2';
}

// 
function test_1() {
    allclear(); construct_sets();
    show('gen'); hide('change');
    document.getElementById('effect1').checked = true;
    document.getElementById('effect2').checked = false;
    document.getElementById('effect3').checked = false;
	document.getElementsByName('factors')[0].value = 11;
	document.getElementsByName('levels')[0].value = '4 4 4 4 4 4 4 4 4 4 4';
	document.getElementsByName('msize')[0].value = 2;
	document.getElementsByName('gens')[0].value = '1 1 1 1 1 1 1 1 1 1 1';
	document.getElementsByName('tmts')[0].value = '1 1 1 1 1 1 1 1 1 1 1\n0 0 0 0 0 0 0 0 0 0 0\n0 0 0 2 2 2 3 3 3 1 0\n0 0 0 3 3 3 1 1 1 2 0\n0 1 3 0 2 1 1 2 3 3 0\n0 1 3 1 0 2 2 3 1 0 0\n0 1 3 2 1 0 3 1 2 2 0\n0 2 1 0 1 3 0 3 2 3 0\n0 2 1 1 3 0 2 0 3 1 0\n0 2 1 3 0 1 3 2 0 2 0\n0 3 2 1 2 3 2 1 0 3 0\n0 3 2 2 3 1 0 2 1 0 0\n0 3 2 3 1 2 1 0 2 1 0\n1 0 2 0 1 3 3 2 0 1 0\n1 0 2 1 3 0 0 3 2 2 0\n1 0 2 3 0 1 2 0 3 3 0\n1 1 1 1 1 1 1 1 1 1 0\n1 1 1 2 2 2 0 0 0 3 0\n1 1 1 3 3 3 2 2 2 0 0\n1 2 3 0 3 2 3 0 1 2 0\n1 2 3 2 0 3 0 1 3 0 0\n1 2 3 3 2 0 1 3 0 1 0\n1 3 0 0 2 1 3 1 2 0 0\n1 3 0 1 0 2 1 2 3 2 0\n1 3 0 2 1 0 2 3 1 3 0\n2 0 3 1 2 3 1 0 2 0 0\n2 0 3 2 3 1 2 1 0 1 0\n2 0 3 3 1 2 0 2 1 3 0\n2 1 0 0 1 3 2 0 3 2 0\n2 1 0 1 3 0 3 2 0 3 0\n2 1 0 3 0 1 0 3 2 1 0\n2 2 2 0 0 0 1 1 1 3 0\n2 2 2 1 1 1 3 3 3 0 0\n2 2 2 2 2 2 2 2 2 2 0\n2 3 1 0 3 2 1 3 0 0 0\n2 3 1 2 0 3 3 0 1 1 0\n2 3 1 3 2 0 0 1 3 2 0\n3 0 1 0 2 1 2 3 1 2 0\n3 0 1 1 0 2 3 1 2 3 0\n3 0 1 2 1 0 1 2 3 0 0\n3 1 2 0 3 2 0 1 3 1 0\n3 1 2 2 0 3 1 3 0 2 0\n3 1 2 3 2 0 3 0 1 0 0\n3 2 0 1 2 3 0 2 1 1 0\n3 2 0 2 3 1 1 0 2 3 0\n3 2 0 3 1 2 2 1 0 0 0\n3 3 3 0 0 0 2 2 2 1 0\n3 3 3 1 1 1 0 0 0 2 0\n3 3 3 3 3 3 3 3 3 3 0\n0 0 0 0 0 0 0 0 0 0 1\n0 0 0 2 2 2 3 3 3 1 1\n0 0 0 3 3 3 1 1 1 2 1\n0 1 3 0 2 1 1 2 3 3 1\n0 1 3 1 0 2 2 3 1 0 1\n0 1 3 2 1 0 3 1 2 2 1\n0 2 1 0 1 3 0 3 2 3 1\n0 2 1 1 3 0 2 0 3 1 1\n0 2 1 3 0 1 3 2 0 2 1\n0 3 2 1 2 3 2 1 0 3 1\n0 3 2 2 3 1 0 2 1 0 1\n0 3 2 3 1 2 1 0 2 1 1\n1 0 2 0 1 3 3 2 0 1 1\n1 0 2 1 3 0 0 3 2 2 1\n1 0 2 3 0 1 2 0 3 3 1\n1 1 1 1 1 1 1 1 1 1 1\n1 1 1 2 2 2 0 0 0 3 1\n1 1 1 3 3 3 2 2 2 0 1\n1 2 3 0 3 2 3 0 1 2 1\n1 2 3 2 0 3 0 1 3 0 1\n1 2 3 3 2 0 1 3 0 1 1\n1 3 0 0 2 1 3 1 2 0 1\n1 3 0 1 0 2 1 2 3 2 1\n1 3 0 2 1 0 2 3 1 3 1\n2 0 3 1 2 3 1 0 2 0 1\n2 0 3 2 3 1 2 1 0 1 1\n2 0 3 3 1 2 0 2 1 3 1\n2 1 0 0 1 3 2 0 3 2 1\n2 1 0 1 3 0 3 2 0 3 1\n2 1 0 3 0 1 0 3 2 1 1\n2 2 2 0 0 0 1 1 1 3 1\n2 2 2 1 1 1 3 3 3 0 1\n2 2 2 2 2 2 2 2 2 2 1\n2 3 1 0 3 2 1 3 0 0 1\n2 3 1 2 0 3 3 0 1 1 1\n2 3 1 3 2 0 0 1 3 2 1\n3 0 1 0 2 1 2 3 1 2 1\n3 0 1 1 0 2 3 1 2 3 1\n3 0 1 2 1 0 1 2 3 0 1\n3 1 2 0 3 2 0 1 3 1 1\n3 1 2 2 0 3 1 3 0 2 1\n3 1 2 3 2 0 3 0 1 0 1\n3 2 0 1 2 3 0 2 1 1 1\n3 2 0 2 3 1 1 0 2 3 1\n3 2 0 3 1 2 2 1 0 0 1\n3 3 3 0 0 0 2 2 2 1 1\n3 3 3 1 1 1 0 0 0 2 1\n3 3 3 3 3 3 3 3 3 3 1\n0 0 0 0 0 0 0 0 0 0 2\n0 0 0 2 2 2 3 3 3 1 2\n0 0 0 3 3 3 1 1 1 2 2\n0 1 3 0 2 1 1 2 3 3 2\n0 1 3 1 0 2 2 3 1 0 2\n0 1 3 2 1 0 3 1 2 2 2\n0 2 1 0 1 3 0 3 2 3 2\n0 2 1 1 3 0 2 0 3 1 2\n0 2 1 3 0 1 3 2 0 2 2\n0 3 2 1 2 3 2 1 0 3 2\n0 3 2 2 3 1 0 2 1 0 2\n0 3 2 3 1 2 1 0 2 1 2\n1 0 2 0 1 3 3 2 0 1 2\n1 0 2 1 3 0 0 3 2 2 2\n1 0 2 3 0 1 2 0 3 3 2\n1 1 1 1 1 1 1 1 1 1 2\n1 1 1 2 2 2 0 0 0 3 2\n1 1 1 3 3 3 2 2 2 0 2\n1 2 3 0 3 2 3 0 1 2 2\n1 2 3 2 0 3 0 1 3 0 2\n1 2 3 3 2 0 1 3 0 1 2\n1 3 0 0 2 1 3 1 2 0 2\n1 3 0 1 0 2 1 2 3 2 2\n1 3 0 2 1 0 2 3 1 3 2\n2 0 3 1 2 3 1 0 2 0 2\n2 0 3 2 3 1 2 1 0 1 2\n2 0 3 3 1 2 0 2 1 3 2\n2 1 0 0 1 3 2 0 3 2 2\n2 1 0 1 3 0 3 2 0 3 2\n2 1 0 3 0 1 0 3 2 1 2\n2 2 2 0 0 0 1 1 1 3 2\n2 2 2 1 1 1 3 3 3 0 2\n2 2 2 2 2 2 2 2 2 2 2\n2 3 1 0 3 2 1 3 0 0 2\n2 3 1 2 0 3 3 0 1 1 2\n2 3 1 3 2 0 0 1 3 2 2\n3 0 1 0 2 1 2 3 1 2 2\n3 0 1 1 0 2 3 1 2 3 2\n3 0 1 2 1 0 1 2 3 0 2\n3 1 2 0 3 2 0 1 3 1 2\n3 1 2 2 0 3 1 3 0 2 2\n3 1 2 3 2 0 3 0 1 0 2\n3 2 0 1 2 3 0 2 1 1 2\n3 2 0 2 3 1 1 0 2 3 2\n3 2 0 3 1 2 2 1 0 0 2\n3 3 3 0 0 0 2 2 2 1 2\n3 3 3 1 1 1 0 0 0 2 2\n3 3 3 3 3 3 3 3 3 3 2\n0 0 0 0 0 0 0 0 0 0 3\n0 0 0 2 2 2 3 3 3 1 3\n0 0 0 3 3 3 1 1 1 2 3\n0 1 3 0 2 1 1 2 3 3 3\n0 1 3 1 0 2 2 3 1 0 3\n0 1 3 2 1 0 3 1 2 2 3\n0 2 1 0 1 3 0 3 2 3 3\n0 2 1 1 3 0 2 0 3 1 3\n0 2 1 3 0 1 3 2 0 2 3\n0 3 2 1 2 3 2 1 0 3 3\n0 3 2 2 3 1 0 2 1 0 3\n0 3 2 3 1 2 1 0 2 1 3\n1 0 2 0 1 3 3 2 0 1 3\n1 0 2 1 3 0 0 3 2 2 3\n1 0 2 3 0 1 2 0 3 3 3\n1 1 1 1 1 1 1 1 1 1 3\n1 1 1 2 2 2 0 0 0 3 3\n1 1 1 3 3 3 2 2 2 0 3\n1 2 3 0 3 2 3 0 1 2 3\n1 2 3 2 0 3 0 1 3 0 3\n1 2 3 3 2 0 1 3 0 1 3\n1 3 0 0 2 1 3 1 2 0 3\n1 3 0 1 0 2 1 2 3 2 3\n1 3 0 2 1 0 2 3 1 3 3\n2 0 3 1 2 3 1 0 2 0 3\n2 0 3 2 3 1 2 1 0 1 3\n2 0 3 3 1 2 0 2 1 3 3\n2 1 0 0 1 3 2 0 3 2 3\n2 1 0 1 3 0 3 2 0 3 3\n2 1 0 3 0 1 0 3 2 1 3\n2 2 2 0 0 0 1 1 1 3 3\n2 2 2 1 1 1 3 3 3 0 3\n2 2 2 2 2 2 2 2 2 2 3\n2 3 1 0 3 2 1 3 0 0 3\n2 3 1 2 0 3 3 0 1 1 3\n2 3 1 3 2 0 0 1 3 2 3\n3 0 1 0 2 1 2 3 1 2 3\n3 0 1 1 0 2 3 1 2 3 3\n3 0 1 2 1 0 1 2 3 0 3\n3 1 2 0 3 2 0 1 3 1 3\n3 1 2 2 0 3 1 3 0 2 3\n3 1 2 3 2 0 3 0 1 0 3\n3 2 0 1 2 3 0 2 1 1 3\n3 2 0 2 3 1 1 0 2 3 3\n3 2 0 3 1 2 2 1 0 0 3\n3 3 3 0 0 0 2 2 2 1 3\n3 3 3 1 1 1 0 0 0 2 3\n3 3 3 3 3 3 3 3 3 3 3'; 
}


