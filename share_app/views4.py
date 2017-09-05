from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render, redirect

from share_app.models import *

def addTool(request):
	if request.POST:
		tool = Tool.objects.create(
			name		= request.POST['name']
			type		= request.POST['type']
			restricted	= request.POST['restricted'])
		return HttpResponseRedirect('/sharezone/')
	else:
        return HttpResponseRedirect('/share_app/')
		
def addShed(request):
	if request.POST:
		admin = Member.objects.get(type=2, zone = request.POST['zone'])
		admin.shed = Shed.objects.create(address = request.POST['address'])
	else:
		return HttpResponseRedirect('share_app/')
def borrowTools(request):
        if request.POST:
                if request.user.is_authenticated():
                        tool = Tool.object.get(
                                holder  = request.username.get[''])
                        return HttpResponseRedirect('/sharezone/')
                else:
                return HttpResponseRedirect('/share_app/')

def borrowTools(request):
        if request.POST:
                if request.user.is_authenticated():
                        tool = Tool.object.get(
                                holder  = request.owner.username.get[''])
                        
                        return HttpResponseRedirect('/sharezone/')
                else:
                return HttpResponseRedirect('/share_app/')
                                
                
def addToShed(request):
	if request.POST:
		tool = Tool.objects.create(
			name		= request.POST['name']
			type		= request.POST['type']
			restricted	= request.POST['restricted'])
		return HttpResponseRedirect('/sharezone/')
	else:
        return HttpResponseRedirect('/share_app/')
