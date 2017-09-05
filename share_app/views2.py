
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from login.models import loginModel


# Logout user method 
def logoutUser(request):
    logout(request)
    return HttpResponseRedirect('/login/')  # Redirect to a success page.

# Login user method
def loginUser(request):
    # Checks if user is already logged in
    if request.user.is_authenticated():
        return HttpResponseRedirect("/tooldirectory/")  # Redirect to a tool directory page.
    model = loginModel(request.POST or None)
    # Logs in user and sends user to a page redirect
    if request.POST and model.is_valid():
        user = model.login(request)
        if user:
            login(request, user)
            return HttpResponseRedirect("/tooldirectory/")  # Redirect to a success page.
    return render(request, 'login/login.html')