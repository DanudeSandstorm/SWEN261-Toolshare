from django.contrib import admin
from share_app.models import Member, ShareZone

class UserAdmin(admin.ModelAdmin):
	fieldsets	= [
				("Personal Info",		{"fields": ["fname", "lname", "gender", "dob", "zone"]}),
				("Account Info",		{"fields": ["username", "password"]}),
				("Contact Info",		{"fields": ["zip", "email", "address"]}),
			]

class ZoneAdmin(admin.ModelAdmin):
	fieldsets	= [
				("Personal Info",		{"fields": ["name"]})
			]
			
admin.site.register(Member, UserAdmin)
admin.site.register(ShareZone, ZoneAdmin)