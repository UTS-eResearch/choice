//
// miscellaneous javascript functions
//

//
// hide a <div> section
//
function hide(id)
	{
	var obj = document.getElementById(id);
	obj.style.display = "none";
	}

//
// show a <div> section
//
function show(id)
	{ 
	var obj = document.getElementById(id);
	obj.style.display = "block";
	}

//
// Update height/width of textarea
//
function resizeTextarea(id, rows, cols)
	{
	var obj = document.getElementById(id);
	if (!obj || (typeof(obj.rows) == "undefined"))
		return;
	obj.rows = rows
	obj.cols = cols
	}

