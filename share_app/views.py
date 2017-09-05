from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q, F
from datetime import datetime

from share_app.models import *

#TODO: serverside validation

# *********************************************************************
# home page
# *********************************************************************
def index(request):
	if request.POST.get('invalid') is not None:
		template = loader.get_template('share_app/index.html')
		context = RequestContext(request, {'error':'error'})
	else:
		if request.user.is_authenticated():
			template = loader.get_template('share_app/user_panel.html')
			member = Member.objects.get(username = request.user.username)
			username = member.username
			first_name = member.first_name;
			last_name = member.last_name;
			zone = member.zone
			allUsernames = Member.objects.all().filter(zone = zone).values_list('username', flat = True)
			rating = member.rating if member.rating != 0 else 'N/A'
			owned = Tool.objects.filter(owner = member)
			tools = getAvailableTools(member)
			borrowed = Tool.objects.filter(holder = member).filter(~Q(owner = member))
			shedTools = Tool.objects.filter(zone = zone).filter(inShed = True)
			open = member.zone.shed.open
			address = member.address
			shedaddress = member.zone.shed.address
			email = member.email
			zipcode = member.zip
			notifs = Notification.objects.filter(read = False).filter(receiver = member)
			allMessages = Message.objects.filter(receiver = member)
			zoneRequests = SharezoneRequest.objects.filter(zone = member.zone).filter(answered = False)
			active = request.user.is_active
			isAdmin = member.isAdmin
			context = RequestContext(request, {'allUsernames':allUsernames, 'username':username, 'first_name':first_name, 'last_name':last_name, 'email':email, 'address':address, 'zone':zone, 'rating':rating,
					'owned':owned, 'borrowed':borrowed, 'tools':tools, 'shedTools':shedTools, 'isAdmin':isAdmin, 'open':open, 'shedaddress':shedaddress, 'zipcode':zipcode, 'notifs':notifs, 'allMessages':allMessages, 'active':active, 'zoneRequests':zoneRequests})
		else:
			template = loader.get_template('share_app/index.html')
			context = RequestContext(request, {})
	return HttpResponse(template.render(context))

# *********************************************************************
# signup
# *********************************************************************
def signup(request):
	"""
	"	called by signup.html to create a new user in the server
	"	if this is a new sharezone, an Admin is created
	"	if not, a member is created that is not activated
	"""
	if request.POST:
		zone_name = request.POST['zone']
		if zone_name == 'new':
			# create new sharezone if the user inputted a new one
			zone = ShareZone.objects.create(name = request.POST['newzone'],
											shed = Shed.objects.create(address = ' ', open = False))
		else:
			# otherwise, get the sharezone by the selected name
			zone = ShareZone.objects.get(id = 1)

		# compile date of birth
		dob = request.POST['month'] + '/' + request.POST['day'] + '/' + request.POST['year']

		authUser = User.objects.create_user(username = request.POST['username'], password = request.POST['password'])

		if zone_name == 'new':
			# create admin if new sharezone
			member = Admin.objects.create(
				user			= authUser,
				username		= request.POST['username'],
				password		= request.POST['password'],
				first_name		= request.POST['firstname'],
				last_name		= request.POST['lastname'],
				email			= request.POST['email'],
				
				gender			= request.POST['gender'],
				dob				= dob,
				zip				= request.POST['zip'],
				address			= request.POST['address'],
				rating			= 0.00,
				zone			= zone,
				isAdmin			= True)
		else:
			# otherwise, create member
			authUser.is_active = False
			authUser.save()
			member = Member.objects.create(
				user			= authUser,
				username		= request.POST['username'],
				password		= request.POST['password'],
				first_name		= request.POST['firstname'],
				last_name		= request.POST['lastname'],
				email			= request.POST['email'],
				
				gender			= request.POST['gender'],
				dob				= dob,
				zip				= request.POST['zip'],
				address			= request.POST['address'],
				rating			= 0.00,
				zone			= zone)

			zoneRequest = SharezoneRequest.objects.create(sender = member, zone = zone)

		return tryLogin(request)
	else:
		sharezones = ShareZone.objects.all()
		return render(request, 'share_app/signup.html', RequestContext(request,{'sharezones':sharezones}))

# *********************************************************************
# Change Account Information
# *********************************************************************
def editAccountInfo(request):
	"""
	"	called by userPanel.html to open the template to edit account info
	"""
	if request.user.is_authenticated():
		template = loader.get_template('share_app/edit_info.html')

		member = Member.objects.get(username = request.user.username)

		context = RequestContext(request, {'password':member.password, 'first_name':member.first_name, 'last_name':member.last_name,
											'email':member.email, 'zip':member.zip, 'address':member.address})
		return HttpResponse(template.render(context))
	else:
		return HttpResponseRedirect('/share_app')

def saveAccountInfo(request):
	"""
	"	called by userPanel.html to write the changes made to the server (if current password)
	"""
	if request.POST:
		member = Member.objects.get(username = request.user.username)
		oldPassword = request.POST['oldPassword']

		if oldPassword == member.password:
			#update all info
			if request.POST['password'] != '':
				member.password				= request.POST['password']
				request.user.set_password(request.POST['password'])
				request.user.save()

			member.first_name				= request.POST['firstname']
			member.last_name				= request.POST['lastname']
			member.email					= request.POST['email']

			member.zip						= request.POST['zip']
			member.address					= request.POST['address']

			member.save()
	return HttpResponseRedirect('/share_app/')

def approveUser(request):
	if request.POST:
		zone = Member.objects.get(username = request.user.username).zone
		for sRequest in SharezoneRequest.objects.filter(zone = zone):
			if sRequest.answered == False:
				member = sRequest.sender
				if request.POST.get('reqName' + str(member.id), '') != '':
					if request.POST.get('approve', '') == 'Approve':
						member.user.is_active = True
						member.user.save()
						member.save()
					sRequest.answered = True
					sRequest.save()
	return HttpResponseRedirect('/share_app/')

# *********************************************************************
# login/logout
# *********************************************************************
def tryLogin(request):
	if request.POST:
		user = authenticate(username = request.POST['username'], password = request.POST['password'])
		
		if user is not None:
			login(request, user)
			return HttpResponseRedirect('/share_app/')
		else:
			invalid = 1
			loader.get_template('share_app/index.html').render(RequestContext(request, {'error':'error'}))
	return HttpResponseRedirect('/share_app/')

def tryLogout(request):
	logout(request)
	return HttpResponseRedirect('/share_app/')

# *********************************************************************
# tool uploading
# *********************************************************************
def addTool(request):
	if request.POST:
		if request.user.is_authenticated():
			member = Member.objects.get(username = request.user.username)
			tool = Tool.objects.create(
				name		= request.POST['toolName'],
				type		= request.POST['toolType'],
				quality		= request.POST['toolQuality'],
				restricted	= request.POST.get('toolRestricted', False),
				zone		= member.zone,
				rating		= 0,
				numRatings	= 0,
				owner		= member,
				holder		= member)
	return HttpResponseRedirect('/share_app/')

def editTools(request):
	"""
	"	called by save button of user_panel.html to save the update information of each of the member's tools
	"""
	if request.POST:
		if request.user.is_authenticated():
			member = Member.objects.get(username = request.user.username)
			tools = Tool.objects.filter(owner = member)
			for tool in tools:
				if request.POST.get('n' + str(tool.id), '') != '':
					tool.name = request.POST['n' + str(tool.id)]
				tool.quality = request.POST.get('q' + str(tool.id), 1)
				tool.restricted = request.POST.get('rst' + str(tool.id), False)
				tool.registered = request.POST.get('reg' + str(tool.id), False)
				tool.inShed = request.POST.get('shd' + str(tool.id), False)
				tool.save()
	return HttpResponseRedirect('/share_app/')

# *********************************************************************
# tool searching
# *********************************************************************
def borrowTool(request):
	if request.POST:
		tool = Tool.objects.get(id = request.POST['tool'])
		tool.holder = Member.objects.get(username = request.user.username)
		tool.save()
		return HttpResponseRedirect('/share_app/')

def returnTools(request):
	"""
	"	called by return button of user_panel.html to return all the selected tools
	"""
	if request.POST:
		if request.user.is_authenticated():
			member = Member.objects.get(username = request.user.username)
			tools = Tool.objects.filter(holder = member).filter(~Q(owner = member))
			for tool in tools:
				if request.POST.get('ret' + str(tool.id), False):
					if request.POST['rate' + str(tool.id)] != '0':
						tool.rating *= tool.numRatings
						tool.rating += int(request.POST['rate' + str(tool.id)])
						tool.rating /= tool.numRatings + 1
						tool.numRatings += 1
					tool.holder = tool.owner
					tool.save()
					# send notifcation
		return HttpResponseRedirect('/share_app/')

def getAvailableTools(member):
	"""
	"	returns a list of all the tools in the member's sharezone that are available for borrowing
	"""
	return Tool.objects.filter(zone = member.zone).filter(holder = F('owner')).filter(~Q(owner = member)).filter(registered = True)
# *********************************************************************
# shed creation
# *********************************************************************
def addShed(request):
	if request.POST:
		if request.user.is_authenticated():
			if isinstance(request.user, Admin):
				shed = Member.objects.get(username = request.user.username).zone.shed
				shed.open = True
				shed.address = request.POST['shedAddress']
				shed.save()
				return HttpResponseRedirect('/share_app/')
	else:
		return HttpResponseRedirect('/share_app/')

# *********************************************************************
# messaging
# *********************************************************************
def sendMessage(request):
	if request.POST:
		if request.user.is_authenticated():
			sender = Member.objects.get(username = request.user.username)
			receiver = Member.objects.get(username = request.POST['receiver'])
			messageText = request.POST['message']
			notifText = "Message from " + request.user.username

			message = Message.objects.create(
				sender			= sender,
				receiver		= receiver,
				text			= messageText,
				send_time		= datetime.now()
			)

			notification = Notification.objects.create(
				sender			= sender,
				receiver		= receiver,
				message			= message,
				text			= notifText,
				send_time		= datetime.now()
			)

	return HttpResponseRedirect('/share_app/')

# *********************************************************************
# user and tool ratings
# *********************************************************************
def rateTool(request):
	if request.POST:
		if request.user.is_authenicated():
			rating = ToolRating.objects.create(
				rater		= Member.objects.get(username = request.user.username),
				member		= Member.objects.get(username = request.POST['username']),
				value		= request.POST['userrating']
			)
		
def rateUser(request):
	if request.POST:
		if request.user.is_authenicated():
			rating = UserRating.objects.create(
				rater		= Member.objects.get(username = request.user.username),
				tool		= Tool.objects.get(name = request.POST['toolname']),
				value		= request.POST['toolrating']
			)