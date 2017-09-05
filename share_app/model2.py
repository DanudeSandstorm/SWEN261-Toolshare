from django.db import models
from django.contrib.auth import authenticate

# Creates a new login form 
class loginModel(models.Model):
    error_css_class = 'alert alert-danger'
    username = models.CharField(max_length=30)
    password = models.CharField()
	
    # Redefines the clean method to include error raising
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username = username, password = password)
        if (not user or not user.is_active) and username != None and password != None:
            raise models.ValidationError("Sorry, that login was invalid. Please try again.")
        return self.cleaned_data

    # Redefines the login method
    def login(self, request):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        return user