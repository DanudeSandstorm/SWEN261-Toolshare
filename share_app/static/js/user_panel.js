// ************************************************************************************************
// topbar show/hide actions
// ************************************************************************************************
function addShedFields() {
	div = document.getElementById('shedFields');
	div.removeChild(document.getElementById('shedButton'));
	div.innerHTML += '																				\
						<h4>Add Community Shed</h4>													\
						Address																		\
						<input type="text" name="shedAddress" required>								\
						<input type="submit" class="button" value="Create Shed">					\
					';
}

function addSearchFields() {
	removeFields();
	show(document.getElementById('searchField'));
}

function addToolFields() {
	removeFields();
	show(document.getElementById('newToolField'));
}

function addMessageFields() {
	removeFields();
	show(document.getElementById('newMessageField'));
}

function addEditInfoFields() {
	removeFields();
	show(document.getElementById('editInfoField'));
}

function removeFields() {
	hide(document.getElementById('editInfoField'));
	hide(document.getElementById('newToolField'));
	hide(document.getElementById('searchField'));
	hide(document.getElementById('newMessageField'));
}

// ************************************************************************************************
// manage owned tools
// ************************************************************************************************
function showToolManager() {
	hide(document.getElementById('borrowedList'));
	hide(document.getElementById('ownedList'));
	show(document.getElementById('manageList'));
}

// ************************************************************************************************
// return borrowed tool
// ************************************************************************************************
function showToolReturn() {
	hide(document.getElementById('borrowedList'));
	hide(document.getElementById('ownedList'));
	show(document.getElementById('returnList'));
}

function show(div) {
	div.style.display = 'block';
} 
function hide(div) {
	div.style.display = 'none';
}

// ************************************************************************************************
// messages
// ************************************************************************************************
function showMessages() {
	hide(document.getElementById('notifications'));
	hide(document.getElementById('userInfoTable'));
	show(document.getElementById('messagesTable'));
	show(document.getElementById('backButton'));
}

// ************************************************************************************************
// account info
// ************************************************************************************************
function showUserInfo() {
	hide(document.getElementById('messagesTable'));
	hide(document.getElementById('backButton'));
	show(document.getElementById('userInfoTable'));
}