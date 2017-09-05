from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm

class create_user_form(forms.ModelForm):
	name = forms.CharField(max_length=32)
	
	class Meta:
		model = Category

class user_creation_form(UserCreationForm):
	"""
	Creation of new Users
	- username
	- birthdate
	- gender
	- email
	- address
	-zip
	"""
	email		= forms.EmailField(label = "Email", required = True)
	birthdate	= forms.DateField(label = "birthdate", required = True)
	gender		= forms.CharField(label = "Gender", required = True)
	address		= forms.TextField(label = "Address", required = True)
	zip			= forms.IntegerField(label = "zip", required = True)
	
	class Meta:
		model = User
		fields = ["username","birthdate","gender","email","address","zip"]

class share_zone_creation_form(ModelForm):
	"""
	Creation of new Share zone
	"""
	name		= forms.CharField(required = True, label = "name")
	address		= forms.TextField(required = True, label = "address")
	zip			= forms.IntegerField(required = True, label = "zip")
	summary		= forms.CharField(required = False, label = "summary")
	
	def __init__(self, *arg, **kwargs):
		super(share_zone_creation_form, self).__init__(*arg, **kwargs)
		
	class Meta:
		model = ShareZone
		fields = ["name", "summary"]
		
class share_zone_selection_form(ModelForm):
	"""
	Selct a ShareZone from active ones
	"""
	# in order for one to select an active share zone it must be approved and created first
	share_zone  = forms.ModelChoiceField(queryset=Sharezone.objects.filter(is_approved=True, is_active=True), label='Sharezone', required=True)
	
	class Meta:
		model = User
		fields = ["share_zone"]
	