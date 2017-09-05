from django.db					import models
from django						import forms
from django.contrib.auth.models	import User

class Shed(models.Model):
	address		= models.CharField(max_length = 32)
	open		= models.BooleanField()

class ShareZone(models.Model):
	name		= models.CharField(max_length = 32)
	shed		= models.OneToOneField(Shed)
	#users		= forms.ModelMultipleChoiceField(User.objects.all())
	#trans		= forms.ModelMultipleChoiceField(Transaction.objects.all())
	
	def __str__(self):
		return self.name

class Member(models.Model):
	user		= models.OneToOneField(User)

	username	= models.CharField(max_length = 32)
	password	= models.CharField(max_length = 32)

	first_name	= models.CharField(max_length = 32)
	last_name	= models.CharField(max_length = 32)
	
	gender		= models.CharField(max_length = 1, blank = True)
	dob			= models.CharField(max_length = 100)
	zip			= models.IntegerField(max_length = 5, blank = True)
	email		= models.EmailField(max_length = 254, blank = True)
	address		= models.TextField(blank = True)
	rating		= models.DecimalField(max_digits = 3, decimal_places = 2, blank = True)
	zone		= models.ForeignKey(ShareZone)

	isAdmin		= models.BooleanField(default = False)
	
	def __str__(self):
		return self.username
	
class Admin(Member):
	pass

class SuperAdmin(Admin):
	pass

class Tool(models.Model):
	name		= models.CharField(max_length = 32)
	type		= models.CharField(max_length = 32)
	
	restricted	= models.BooleanField(default = False)
	inShed		= models.BooleanField(default = False)
	zone		= models.CharField(max_length = 32)
	quality		= models.IntegerField()

	rating		= models.DecimalField(max_digits = 3, decimal_places = 2, blank = True)
	numRatings	= models.IntegerField(blank = True)

	owner		= models.ForeignKey(Member, related_name = "Owner")
	holder		= models.ForeignKey(Member, related_name = "Holder")

	registered	= models.BooleanField(default = True)

class Transaction(models.Model):
	borrow_date	= models.DateTimeField("Date Borrowed")
	return_date	= models.DateTimeField("Date Returned")
	due_date	= models.DateTimeField("Date Due")
	
	zone		= models.ForeignKey(ShareZone)
	borrower	= models.ForeignKey(Member, related_name = "Borrower")
	lender		= models.ForeignKey(Member, related_name = "Lender")
	tool		= models.ForeignKey(Tool)

class ToolRequest(models.Model):
	sender 			= models.ForeignKey(Member, related_name = "ToolRequestSender")
	receiver 		= models.ForeignKey(Member, related_name = "ToolRequestReceiver")

class SharezoneRequest(models.Model):
	sender			= models.ForeignKey(Member)
	zone			= models.ForeignKey(ShareZone)
	answered		= models.BooleanField(default = False)

class Message(models.Model):
	sender			= models.ForeignKey(Member, related_name = "MessageSender")
	receiver		= models.ForeignKey(Member, related_name = "MessageReceiver")
	text			= models.TextField()
	send_time		= models.DateTimeField("Time Sent")

class Notification(models.Model):
	sender 			= models.ForeignKey(Member, related_name = "NotificationSender")
	receiver 		= models.ForeignKey(Member, related_name = "NotificationReceiver")
	message			= models.ForeignKey(Message)
	text			= models.TextField(blank = True)
	send_time		= models.DateTimeField("Time Sent")
	read			= models.BooleanField(default = False)