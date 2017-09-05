import os

def populate():
    try:
        user = User.objects.create_user( username = 'SuperAdmin', email = 'bull@shit.com', password = 'defpassword' )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        ToolType.objects.create(type = "Hammer")
        ToolType.objects.create(type = "Screwdriver")
        ToolType.objects.create(type = "Wrench")
        ToolType.objects.create(type = "Ratchet")
        ToolType.objects.create(type = "Saw")
        ToolType.objects.create(type = "Pliers")
        ToolType.objects.create(type = "Power Drill")
        ToolType.objects.create(type = "Power Saw")
        ToolType.objects.create(type = "Tape Measure/Square")
        ToolType.objects.create(type = "other")
    except:
        pass
    
# Start execution here!
if __name__ == '__main__':
    print ("Starting ToolShare population script...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ToolShare.settings')
    from django.contrib.auth.models import User, Group
    from tools.models import UserData, Notification, Reservation, ToolType, Tool, ShareZone, CommunityShed
    populate()    