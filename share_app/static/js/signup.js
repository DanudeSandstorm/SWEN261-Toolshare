window.onload = function loadPage() {
	addNew();
	showDays(document.getElementById("dayDiv"));
}

// ********************************************************************
// sharezone creation
// ********************************************************************
function checkNew() {
	if (document.getElementById("zoneSelect").value == 'new') addNew();
	else removeNew();
}

function addNew() {
	newField = document.createElement("INPUT");
	newField.setAttribute("id", "newField");
	newField.setAttribute("type", "text");
	newField.setAttribute("name", "newzone");
	newField.setAttribute("maxLength", "32");
	newField.setAttribute("placeholder", "Sharezone Name");
	newField.required = true;
	document.getElementById("zone").appendChild(newField);
}

function removeNew() {
	document.getElementById("zone").removeChild(document.getElementById("newField"));
}

// ********************************************************************
// date selections
// ********************************************************************
function showDays(dob) {
	/* creates the dropdown box for the day of the month (assumes the month is January) */
	var dropdown = '<select id="day" name="day">';
	for (var i = 1; i < 10; i++)	dropdown += '<option value="0' + i + '">' + i + '</option>';
	for (var i = 10; i <= 31; i++)	dropdown += '<option value="' + i + '">' + i + '</option>';
	dropdown += '</select>';
	dob.innerHTML += dropdown;
}

function updateDays() {
	/* changes the number of days availible depending on the month */
	var element		= document.getElementById('day');
	var prevDays	= element.options.length;
	var newDays		= 31;
	var month		= document.getElementById('month').value;
	
	// determine how many days there are in the month
	if (month == 2) newDays = 29;
	else if (month == 4 || month == 6 || month == 9 || month == 11) newDays = 30;
	
	// remove all extra days
	while (element.options.length > newDays)
		element.remove(element.options.length - 1);
	
	// append missing days
	while (element.options.length < newDays) {
		prevDays += 1;
		var opt		= document.createElement('option');
		opt.text	= prevDays;
		opt.value	= prevDays;
		element.add(opt, element.options.length);
	}
}

// ********************************************************************
// input restricting
// ********************************************************************
function numOnly(e, input) {
	/**
	*	onclick function used to limit an input to numerals
	*	if an input is passed, this function allows periods, but only one
	*/
	var allow = [46, 8, 9, 27, 13, 110];								// allow backspace, delete, escape, enter
	if (input && input.value.indexOf('.') === -1) allow.push(190);		// allow periods if there is not one already
	if	($.inArray(e.keyCode, allow) !== -1 ||
		(e.keyCode == 65 && e.ctrlKey === true) ||						// ctrl + a
		(e.keyCode >= 35 && e.keyCode <= 39))							// home, end, left, right
			return;					
	if 	((e.shiftKey || (e.keyCode < 48 || e.keyCode > 57)) &&
		(e.keyCode < 96 || e.keyCode > 105))
			e.preventDefault();
}

function fixLength(id, len) {
	/**
	*	returns true if there is a value in the input field, false otherwise
	*	if true, appends 0s to the beginning of the value until length len is reached
	*/
	var input = document.getElementById(id);
	if (input.value.length == 0) return false;
	while (input.value.length < len)
		input.value = '0' + input.value;
	return true;
}