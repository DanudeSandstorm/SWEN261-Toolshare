import datetime
#import pytz

from django.db.models import F
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required

from tools.models import UserData, ShareZone, CommunityShed
from tools.models import Reservation, Tool, ToolType, Notification

def index( request ):
    if request.user.is_authenticated():
        #See if the user has a UserData and isn't just an admin
        try:
            u = UserData.objects.get( user = request.user )
            return redirect ( "/tools/me.html" )
        except:
            pass
    return render( request, "tools/index.html" )

def name_invalid( name ):
    return any( char.isdigit() for char in name )

def email_invalid( email ):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email( email )
        return False
    except ValidationError:
        return True

def password_invalid( password ):
    return len( password ) < 10

def birthday_invalid( birthday ):
    birthYear = int( birthday[0:4] )
    birthMonth = int( birthday[5:7] )
    birthDay = int( birthday[8:] )
    try:
        dateOfBirth = datetime.date( birthYear, birthMonth, birthDay )
        return datetime.date( birthYear, birthMonth, birthDay ) > datetime.date.today()
    except:
        return True


def state_invalid( state ):
    state = state.upper()
    states = {'AL', 'AK', 'AS', 'AZ', 'AR_', 'CA', 'CO', 'CT', 'DE', 'DC', 'FM', 'FL',
        'GA', 'GU', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MH', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC',
        'ND', 'MP', 'OH', 'OK', 'OR', 'PW', 'PA', 'PR', 'RI', 'SC', 'TN', 'TX', 'UT',
        'VT', 'VI', 'VA', 'WA', 'WV', 'WI', 'WY', 'AA', 'AP'
    }
    return state not in states

def get_num_notifications( userData ):
    return len( Notification.objects.filter( to = userData, isNew = True ) )

def get_login_context( user ):
    context = {}
    if user.is_authenticated():
        context['loggedin'] = True

        # check if the user is in charge or any ShareZones
        szAdminGroups = []
        szAdminGroupNames = []
        for sz in ShareZone.objects.all():
            szAdminGroupNames.append( sz.name[0:20] + '_admins' )
        for szagn in szAdminGroupNames:
            szAdminGroups.append( Group.objects.get( name = szagn ) )
        context['groups'] = szAdminGroupNames

        for g in szAdminGroups:
            if g in user.groups.all():
                context['admin'] = True

        userData = UserData.objects.get( user = user )

        # Check if the user is in charge of any Community Sheds
        csAdminGroups = []
        for cs in CommunityShed.objects.filter( shareZone = userData.shareZone ):
            if 'house' not in cs.name:
                # This community shed isn't a house! Oh me oh my!
                csagn = cs.shareZone.name[0:20] + '_' + cs.name[0:40] + '_admins'
                csAdminGroups.append( Group.objects.get( name = csagn ) )
        for g in csAdminGroups:
            if g in user.groups.all():
                context['csadmin'] = True

        context['numNotifs'] = get_num_notifications( userData )
        context['userData'] = userData
    return context
   
# David is done with this function and all above it.
def register( request ):
    context = get_login_context( request.user )
    context['sharezones'] = ShareZone.objects.filter(isActive = True)

    if request.method == 'POST':
        for i in request.POST:
            context[i] = request.POST[i].strip()

        firstName   = context['fname']
        lastName    = context['lname']
        email       = context['email']
        password    = context['password']
        password_confirm = context['password_confirm']
        birthday    = context['bday']
        sex         = context['sex']
        address     = context['address']
        state       = context['state']
        city        = context['city']

        valid = True

        # Determine if the user is creating a new ShareZone or not
        if 'shareZone' in context:
            shareZone   = context['shareZone']
            context['oldsz'] = 'join'
            joining = True
        elif 'newSZName' in context:
            newSZName = context['newSZName']
            newSZName = newSZName + " @ " + context['newSZZip']
            newSZAge = context['newSZAge']
            context['oldsz'] = 'create'
            joining = False
        else:
            context['szerror'] = "You must either join a ShareZone or create a new one"
            valid = False

        #make sure the password, zip code, address, birthday, etc are all valid
        if name_invalid( firstName ):
            value = False
            context['fname_error'] = 'No numbers allowed in first name'
        if name_invalid( lastName ):
            valid = False
            context['lname_error'] = 'No numbers allowed in last name'
        if email_invalid( email ):
            valid = False
            context['email_error'] = 'Invalid email address'
        if password_invalid( password ):
            valid = False
            context['password_error'] = 'Passwords must be at least 10 characters'
        if birthday_invalid( birthday ):
            valid = False
            context['bday_error'] = 'You must have been born to use this site'
        if state_invalid( state ):
            valid = False
            context['state_error'] = 'Please enter the postal code of a US state'
        if name_invalid( city ):
            valid = False
            context['city_error'] = 'Cities cannot have numbers'
        if password != password_confirm:
            valid = False
            context['password_different_error'] = 'Please make sure that your passwords are the same'

        if valid:
            #create the Django authentication user
            try:
                user = User.objects.create_user( username = email, email = email, password = password )
            except:
                context['email_error'] = 'Sorry, this e-mail address is already taken'
                return render( request, 'tools/register.html', context )
            user.first_name = firstName
            user.last_name = lastName
            user.is_active = False
            user.save()
            
            #create the ToolShare User
            birthYear = int( birthday[0:4] )
            birthMonth = int( birthday[5:7] )
            birthDay = int( birthday[8:] )

            isMale = False;
            if sex == 'male':
                isMale = True;
            
            if joining: 
                selectedShareZone = ShareZone.objects.get( name = shareZone )
            else:
                selectedShareZone = ShareZone.objects.create( name = newSZName, restrictedAge = newSZAge, isActive = False )
                selectedShareZone.save()
 
                newGroupName =  selectedShareZone.name[0:20] + '_admins'
                newGroup = Group.objects.create( name = newGroupName )
                newGroup.save()
        
                #add all the superadmins to this group
                superAdmins = User.objects.filter( is_staff = True )
                for sa in superAdmins:
                    sa.groups.add( newGroup )
                    sa.save()

            nullZones = ShareZone.objects.filter( name = 'DANGERZONE')
            if len(nullZones) == 0:
                nullZone = ShareZone.objects.create( name = 'DANGERZONE', restrictedAge = 0, isActive = False )
                nullZone.save()
                nZoneAdminName = nullZone.name[0:20] + '_admins'
                nZoneAdminGroup = Group.objects.create( name = nZoneAdminName )
                nZoneAdminGroup.save() 

            userData = UserData( user = user, birthday = datetime.date( birthYear, birthMonth, birthDay ), location = address + ' ' + city + ' ' + state, isMale = isMale )
            
            #If there's no one in this ShareZone, the user should become the admin
            usersInShareZone = UserData.objects.filter( shareZone = selectedShareZone )
           
            if not usersInShareZone:
                #make the user the ShareZone's admin
                szAdminName = selectedShareZone.name[0:20] + '_admins'
                szAdminGroup = Group.objects.get( name = szAdminName )
                szAdminGroup.user_set.add( user )
                user.is_active = True
                szAdminGroup.save()
                
            userData.shareZone = selectedShareZone
                
            #create a new CommunityShed to serve as the user's house
            csName = user.first_name +'_' +user.last_name +'_house'
            #alreadyExistingHouses = CommunityShed.objects.filter( name == csName )
            house = CommunityShed( name = csName, maxNumberOfTools = 100, location = userData.location, shareZone = selectedShareZone )
            house.isHouse = True
            house.numberOfTools = 0
            house.save()
            
            userData.house = house
            
            #create a new permissions group for the user's house
            csPermGroupName = house.shareZone.name[0:20] +'_' +house.name[0:40] +'_admins'
            houseGroup = Group.objects.create( name = csPermGroupName )
            houseGroup.save()
            houseGroup.user_set.add( user )
            
            user.save()
            userData.save()
            house.save()
            houseGroup.save()
            
            return redirect( "/tools/login.html", context )
        else:
            return render( request, "tools/register.html", context )
    return render( request, "tools/register.html", context )

@login_required
def changeprefs( request ):
    userData = UserData.objects.get( user = request.user)
    context = get_login_context( request.user )
    context['fname'] = userData.user.first_name
    context['email'] = userData.user.email
    context['bday'] = userData.birthday
    context['lname'] = userData.user.last_name
    context['location'] = userData.location
    context['password'] = ""
    
    if request.method == 'POST':
        for i in request.POST:
            context[i] = request.POST[i]
            
        fname = context['fname']
        lname = context['lname']
        email = context['email']
        bday = context['bday']
        location = context['location']
        pswd = context['password']
        pswd2 = context['password_confirm']
        
        valid = True
        
        if name_invalid( fname ):
            value = False
            context['fname_error'] = 'No numbers allowed in first name'
        if name_invalid( lname ):
            valid = False
            context['lname_error'] = 'No numbers allowed in last name'
        if email_invalid( email ):
            valid = False
            context['email_error'] = 'Invalid email address'
        if birthday_invalid( bday ):
            valid = False
            context['bday_error'] = 'You must have been born to use this site'
        #if len(pswd) > 0:
        if password_invalid( pswd ):
            valid = False
            context['password_error'] = 'Passwords must be at least 10 characters'
        if pswd != pswd2:
            valid= False
            context['password_different_error'] = 'Please make sure that your passwords are the same'        
        

        if valid:            

            birthYear = int( bday[0:4] )
            birthMonth = int( bday[5:7] )
            birthDay = int( bday[8:] )
            birthDate = datetime.date( birthYear, birthMonth, birthDay )
            #if len(pswd) > 0:
  
            userData.updateUser(fname,lname,pswd,email,location,birthDate)
            #elif len(pswd) == 0:
                #userData.updateUser(fname,lname,userData.user.password,email,location,birthDate)
            return redirect( "/tools/me.html" )
        return render( request, "tools/changeprefs.html", context )            
    return render( request, "tools/changeprefs.html", context )
    
def get_login_page( request ): 
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate( username=username, password=password )
        if user is not None:
            login( request, user )
            context = get_login_context( user ) 
            if user.is_active:
                context['active'] = True
            else:
                context['active'] = False
            return redirect( "/tools/me.html" )
        context['invalidInfo'] = True
    else:
        context['invalidInfo'] = False
    return render( request, "tools/login.html", context )

@login_required
def logout_view( request ):
    logout( request )
    return redirect( "/tools/" )
    
@login_required
def me( request ):
    userData = UserData.objects.get( user = request.user )
    context = get_login_context( request.user )
    context['rating'] = userData.getRating()
    context['userData'] = userData
    
    unfinishReserv = Reservation.objects.filter( tool__owner = userData, status = 0 )
    if request.method == 'POST':
        reserv = Reservation.objects.get( id = request.POST['reservID'] )
        if request.POST['action'] == 'Approve':
            reserv.status = 2
        elif request.POST['action'] == 'Confirm':
            reserv.status = 1
            Notification.objects.create( to = reserv.borrower, sender = userData, date = timezone.now(), message = "Your reservation request has been denied for the following reason: " + request.POST['msg'] )
        reserv.save()
        
    context['openReserves'] =  Reservation.objects.filter( tool__owner = userData, status = 0 )
    
    context['Tools'] = userData.getTools()
     
    return render( request, "tools/me.html", context )

@login_required
def zoneAll( request ):
    context = get_login_context( request.user )
    shareZoneList =  ShareZone.objects.all()
    context['list'] = shareZoneList
    return render( request, "tools/zoneAll.html", context )
    
@login_required
def zone( request ):
    userData = UserData.objects.get( user = request.user )
    shareZone = userData.shareZone
    context = get_login_context( request.user )
    context['ShareZone'] = shareZone
    context['Users'] = shareZone.getActiveUsers()
    context['CSheds'] = shareZone.getCSs()
    context['aTools'] = shareZone.getAvailableTools()
    context['uTools'] = shareZone.getUnavailableTools()
    context['needB'] = False
    if(len(context['CSheds']) == 0):
        context['needB'] = True
    return render( request, "tools/zone.html", context )	

#when a ShareZone is created, a new UserGroup is created with that ShareZone's name then _admins
#when a new CommunityShed is created, a new UserGroup is creates with the ShareZone's name, then an underscore
#   and the CommunityShed's name, then _admins
def createShareZone( request ):
    context = get_login_context( request.user )
    if request.method == 'POST':
        name = request.POST['sname']
        rage = request.POST['rage']
           
        #create the ShareZone itself
        shareZone = ShareZone.objects.create( name = name, restrictedAge = rage, isActive = False )
        shareZone.save()
        
        #create a new UserGroup for this ShareZone
        shareZoneFront = shareZone.name[0:20]
        newGroupName =  shareZoneFront + '_admins'
        newGroup = Group.objects.create( name = newGroupName )
        newGroup.save()
        
        #add all the superadmins to this group
        superAdmins = User.objects.filter( is_staff = True )
        for sa in superAdmins:
            sa.groups.add( newGroup )
            sa.save()

        
        return HttpResponse( "ShareZone created! Please close this page and refresh the previous page." )
        
    return render( request, "tools/createsharezone.html", context )

@login_required
def viewCommunityShed( request ):
    context = get_login_context( request.user )
    if request.method == 'POST':
        context['cs'] = CommunityShed.objects.get( id = request.POST['shedID'] )       
        shed = context['cs']
        context['curTools'] = shed.getCurTools()
        homeTools = shed.getDefTools()
        loanTools = []
        for tool in homeTools:
            if tool.currentLocation != shed:
                loanTools += tool
        context['loanTools'] = loanTools
                
        return render( request, "tools/csview.html", context )
    return HttpResponse( "That's not a valid CommunityShed" )

# things have been added here
@login_required
def toolView( request ):
    context = get_login_context( request.user )
    if request.method == 'POST':
        thisUser = context['userData']
        context['tool'] = Tool.objects.get( id = request.POST['toolID'] )
        
        # tool during this data. Hopefully I can compare these dates.
        # Hopefully...
        tool = context['tool']
        
        tReserv = Reservation.objects.filter( tool = tool, status = 2, borrower = thisUser )
        context['tReserv'] = tReserv
        today = timezone.now()
        for r in tReserv:
            if r.startDate <= today and r.endDate > today:
                context['curReserv'] = r

            
        if thisUser == tool.owner and tool.currentLocation != tool.defaultLocation:
            context['canReturn'] = True
        else:
            context['canReturn'] = False   
        if thisUser == tool.owner:
            context['canDel'] = True
        else:
            context['canDel'] = False

        # see if the owner has wanted to move the tool recently
        if 'action' in request.POST:
            if request.POST['action'] == 'Move to Community Shed':
                # get the user's ShareZone's CS
                zone = thisUser.shareZone
                shed = CommunityShed.objects.get( shareZone = zone, isHouse = False )
                if tool.defaultLocation == tool.currentLocation:
                    tool.currentLocation = shed
                tool.defaultLocation = shed
                tool.save()
                context['item'] = tool
                context['prompt'] = ' has been successfully logged moved'
                return render( request, "tools/confirm.html", context  )
            elif request.POST['action'] == 'Move to your house':
                if tool.defaultLocation == tool.currentLocation:
                    tool.currentLocation = thisUser.house
                tool.defaultLocation = thisUser.house
                tool.save()
                context['item'] = tool
                context['prompt'] = ' has been successfully logged moved'
                return render( request, "tools/confirm.html", context  )
            if request.POST['action'] == 'Take this tool home':
                tool.currentLocation = thisUser.house
                tool.save()
                r = Reservation.objects.get( id = request.POST['reservID'] )
                r.status = 3
                r.save()
                context['item'] = tool
                context['prompt'] = ' has been successfully logged as borrowed'
                return render( request, "tools/confirm.html", context  )
            
            if request.POST['action'] == 'Tool has been returned':
                tool.currentLocation = tool.defaultLocation
                tool.save()
                context['item'] = tool
                context['prompt'] = ' has bee successfully logged as returned'
                return render( request, "tools/confirm.html", context  )

            if request.POST['action'] == 'De-register tool':
                if thisUser == tool.owner and tool.currentLocation == tool.defaultLocation and tool.status != 0:
                    tool.status = 0
                tool.save()
                context['item'] = tool
                context['prompt'] = ' has been successfully removed'
                return render( request, "tools/confirm.html", context  )
        # If the user owns this tool, give them the option to change its
        # default location
        
        isOwner = tool.owner == thisUser
        if isOwner:
            context['canChangeLoc'] = True
            if tool.defaultLocation == thisUser.house:
                try:
                    zone = CommunityShed.objects.get( shareZone = thisUser.shareZone, isHouse = False )
                    context['moveToShed'] = True
                except:
                    pass
            else:
                context['moveToHome'] = True

        if tool.defaultLocation != tool.currentLocation:
            context['status'] = 'On Loan'
        else:
            if tool.defaultLocation == thisUser.house:
                context['status'] = 'At House'
            else:
                context['status'] = 'At Shed'
                         
        return render( request, "tools/toolview.html", context )
    return HttpResponse( "That's not a valid Tool" )
    

@login_required
def createTool( request ):
    userData = UserData.objects.get( user = request.user )
    context = get_login_context( request.user )
    context['rage'] = userData.shareZone.restrictedAge
    context['toolTypes'] = ToolType.objects.all()
    context['locations'] = list(CommunityShed.objects.filter(isHouse = False))
    context['locations'].append(userData.house)

    if request.method == 'POST':
        name = request.POST['name']
        Type = request.POST['toolType']
        loc = request.POST['location']
        cond = request.POST['cond']
        manufacturer = request.POST['manufacturer']
        details = request.POST['details']
        if 'restriction' in request.POST:
            restriction = request.POST['restriction']
        else:
            restriction = True

        context['name'] = name
        context['toolType'] = Type
        context['location'] = loc
        context['cond'] = cond
        context['manufacturer'] = manufacturer
        context['details'] = details

        valid = True
        try:
            condition = int( cond )
            if condition < 1 or condition > 5:
                context['tcond_error'] = 'Please enter a number from 1 to 5'
                valid = False
        except Exception as e:
            context['tcond_error'] = "Please enter a number from 1 to 5"
            valid = False
        
        if not valid:
            return render( request, "tools/createTool.html", context )

        tRestrict = True;
        if restriction == True:
            tRestrict = False

        toolTypes = list(ToolType.objects.filter(type = Type))
        toolType = toolTypes.pop(0)
        location = CommunityShed.objects.get(name = loc)
        location.numberOfTools+=1
        tool = Tool( name = name, toolType = toolType, owner = userData, defaultLocation = location, currentLocation = location, manufacturer = manufacturer, condition=condition, additionalDetails = details, isRestricted = tRestrict )
        tool.save()
        location.save()
        context['item'] = tool
        context['prompt'] = ' has been successfully created'
        return render( request, "tools/confirm.html", context  )
         
    return render( request, "tools/createTool.html", context  )
    
def createcs( request ):
    userData = UserData.objects.get( user = request.user )
    context = get_login_context( request.user )
    
    if request.method == 'POST':
        name = request.POST['name']
        mts = request.POST['maxTls']
        location = request.POST['loc']
        cs = CommunityShed( name = name, maxNumberOfTools = mts, numberOfTools = 0, location = location, shareZone = userData.shareZone, isHouse = False)
        cs.save()

        # Create a group to hold the admins of thie community shed
        csAdminGroupName = userData.shareZone.name[0:20] + '_' + cs.name[0:40] + '_admins'
        g = Group( name = csAdminGroupName )
        g.save()

        g.user_set.add( userData.user )
        g.save()

        context['item'] = cs
        context['prompt'] = ' has been successfully created'
        return render( request, "tools/confirm.html", context  )
    return render( request, "tools/createcs.html", context  )

def admin( request ):
    if request.user.is_staff:
        return redirect( "/admin/" )
    return szAdmin( request )
    
@login_required
def szAdmin( request ):
    userData = UserData.objects.get( user = request.user )
    sz = userData.shareZone
    szAdminName = sz.name[0:20] + '_admins'
    szAdminGroup = Group.objects.get( name = szAdminName )
    if szAdminGroup in userData.user.groups.all():
        context = get_login_context( request.user )
        context['admin'] = True
        context['sz'] = sz
        context['szUsers'] = sz.getActiveUsers()
        context['unUsers'] = sz.getInactiveUsers()
        context['szTools'] = sz.getTools()
        szAdmins = []
        for u in UserData.objects.all():
            if szAdminGroup in u.user.groups.all():
                szAdmins += [u]
        context['szAdmins'] = szAdmins
        return render( request, "tools/szadmin.html", context )
    return HttpResponse( "You shouldn't be here. Go back." )
   
@login_required
def approveUser( request ):
    userData = UserData.objects.get( user = request.user )
    sz = userData.shareZone
    szAdminName = sz.name[0:20] + '_admins'
    szAdminGroup = Group.objects.get( name = szAdminName )
    context = get_login_context( request.user )
    if szAdminGroup in userData.user.groups.all():
        if request.method == 'POST':
            #sz = request.user.userData.shareZone
            unUser = UserData.objects.get( id = request.POST['userDataID'] )
            if request.POST['Status'] == 'Approve':
                unUser.user.is_active = True
                unUser.user.save()
                unUser.save()
                Notification.objects.create( to = unUser, sender = context['userData'], date = timezone.now(), message = "You have been approved!" )
            else:
                unUser.shareZone = ShareZone.objects.get( name = 'DANGERZONE' )
                unUser.save()
                Notification.objects.create( to = unUser, sender = context['userData'], date = timezone.now(), message = "You have been denied :(" )
        context['admin'] = True
        context['sz'] = sz
        context['szUsers'] = UserData.objects.filter( shareZone = sz, user__is_active = True )
        context['unUsers'] = UserData.objects.filter( shareZone = sz, user__is_active = False )
        tools = Tool.objects.filter( defaultLocation__shareZone = sz )
        szTools = []
        for tool in tools:
            if tool.status > 0:
                szTools.append( tool )
        context['szTools'] = szTools

        return render( request, "tools/szadmin.html", context )
    return HttpResponse( "You shouldn't be here. Go back." )
    
@login_required
def administrateUser( request ):
    context = get_login_context( request.user )
    
    for u in UserData.objects.all():
        if str( u.id ) in request.POST:
            context['aUserData'] = u
            return render( request, "tools/uadmin.html", context )
        if request.method == 'POST':
            unUser = UserData.objects.get( id = request.POST['userDataID'] )
            if 'Action' in request.POST:
                if request.POST['Action'] == 'Kick':
                    unUser.shareZone = ShareZone.objects.get( name = 'DANGERZONE' )
                    unUser.user.is_active = False
                    unUser.save()
                    Notification.objects.create( to = unUser, sender = context['userData'], date = timezone.now(), message = "You have been kicked :(" )
                    return szAdmin( request )
    return HttpResponse( "Server error 418. This server may be considered to be short and stout for all practical purposes." )
def adminChangePrefs( request ):

    context = get_login_context( request.user )
    for u in UserData.objects.all():
        if str( u.id ) in request.POST:
            context['aUser'] = u
            return render( request, "tools/adminChangePrefs.html", context )
    uData = UserData.objects.get( id = request.GET['aUser'] )
    context['fname'] = uData.user.first_name
    context['email'] = uData.user.email
    context['bday'] = uData.birthday
    context['lname'] = uData.user.last_name
    context['location'] = uData.location
    #context['password'] = ""
    
    if request.method == 'POST':
        for i in request.POST:
            context[i] = request.POST[i]
            
        fname = context['fname']
        lname = context['lname']
        email = context['email']
        bday = context['bday']
        location = context['location']
        pswd = context['password']

        
        valid = True
        
        if name_invalid( fname ):
            value = False
            context['fname_error'] = 'No numbers allowed in first name'
        if name_invalid( lname ):
            valid = False
            context['lname_error'] = 'No numbers allowed in last name'
        if email_invalid( email ):
            valid = False
            context['email_error'] = 'Invalid email address'
        if birthday_invalid( bday ):
            valid = False

            context['bday_error'] = 'Cannot change user\'s birthday to future date'
        
        if password_invalid( pswd ):
            valid = False
            context['password_error'] = 'Passwords must be at least 10 characters'

        if valid:            

            birthYear = int( bday[0:4] )
            birthMonth = int( bday[5:7] )
            birthDay = int( bday[8:] )
            birthDate = datetime.date( birthYear, birthMonth, birthDay )
  
            uData.updateUser(fname,lname,uData.password,email,location,birthDate)
            return redirect( request, "/tools/uadmin.html", context )
        return render( request, "tools/adminChangePrefs.html", context )            
    return render( request, "tools/adminChangePrefs.html", context )
    
@login_required
def showBorrowTool( request ):
    # load the context with useful variables
    context = get_login_context( request.user )
    
    context['tool'] = Tool.objects.get( id = request.POST['toolID'] )
 
    if 'startDate' in request.POST:
        valid = True
        # get the date of the beginning and end of the reservation
        context['startDate'] = request.POST['startDate']
        context['endDate'] = request.POST['endDate']
        
        sbYear = int( context['startDate'][0:4] )
        sbMonth = int( context['startDate'][5:7] )
        sbDay = int( context['startDate'][8:] )
        
        ebYear = int( context['endDate'][0:4] )
        ebMonth = int( context['endDate'][5:7] )
        ebDay = int( context['endDate'][8:] )
        
        startDate = datetime.datetime( sbYear, sbMonth, sbDay )
        endDate = datetime.datetime( ebYear, ebMonth, ebDay ) + datetime.timedelta(days=1)
        context['date_error'] = ""
        
        if endDate < datetime.datetime.today():
            valid = False
            context['date_error'] += str(endDate) +" has already passed."
        
        if endDate < startDate:
            valid = False
            context['date_error'] += "You cannot reserve a tool for negative time."
            
        if endDate - startDate > datetime.timedelta(days=14):
            valid = False
            context['date_error'] += "You cannot reserve a tool for more than two weeks at a time."
            
        tool = context['tool']
        tReserv = Reservation.objects.filter( tool = tool )
        #Make sure no one else wants to reserve this tool when we do
        if len(tReserv) > 0:
            for r in tReserv:
                if startDate < r.endDate and startDate > r.startDate:
                    valid = False
                    context['date_error'] += "The tool is already reserved for " +str( startDate )
                    break
                if endDate < r.endDate and endDate > r.startDate:
                    valid = False
                    context['date_error'] += "The tool is already reserved for " +str( endDate )
                    break
                if startDate < r.startDate and endDate > r.endDate:
                    valid = False
                    context['date_error'] += "The tool is already reserved from " +str( r.startDate ) + " to " +str( r.endDate )
                    break
        
        if valid:
            # all the timezone.now() stuff is a hack until we make this work
            res = Reservation( startDate = startDate, endDate = endDate, tool = tool, borrower = UserData.objects.get( user = request.user ) )
            borrower = UserData.objects.get( user = request.user )
            owner = tool.owner
            if not tool.defaultLocation.isHouse:
                res.status = 2
            else:
                res.status = 0
                n = Notification( to = owner, sender = borrower, date = timezone.now(), message = 'Someone wants to borrow your tool! Go to your profile page to view their request' )
                n.save()
            res.save()
            
    return render( request, "tools/borrowTool.html", context )
 
def getNotifications( request ):
    context = get_login_context( request.user )
    nUser = UserData.objects.get( user = request.user )
    context['notifications'] = Notification.objects.filter( to = nUser )
    for notif in context['notifications']:
        notif.isNew = False
        notif.save()
        if 'Action' in request.POST:
            dNote = Notification.objects.get( id = request.POST['alert'] )
            if request.POST['Action'] == 'X':
                dNote.delete()
    return render( request, "tools/notifications.html", context )

def toolAll( request ):
    context = get_login_context( request.user )
    userData = UserData.objects.get( user = request.user )
    context['Tools'] = userData.getTools()

    return render( request, "tools/myTools.html", context )
    
def confirm( request ):
    

    return render( request, "tools/confirm.html", context )

def csadmin( request ):
    context = get_login_context( request.user )

    # figure out which Community Shed the user is an admin of
    cs = None
    csAdmins = []
    for shed in CommunityShed.objects.all():
        g = Group.objects.get( name = shed.shareZone.name[0:20] + '_' + shed.name[0:40] + '_admins' )
        if g in request.user.groups.all():
            cs = shed
        for user in User.objects.all():
            if g in user.groups.all():
                csAdmins.append( g )
    
    context['cs'] = cs
    context['csAdmins'] = csAdmins

    #get all the tools in the CommunityShed
    tools = Tool.objects.filter( defaultLocation = cs )
    toolList = []
    for tool in tools:
        if tool.status > 0:
            toolList.append( tool )

    if request.method == 'POST':
        tool = Tool.objects.get( id = int( request.POST['toolID'] ) )
        if request.POST['action'] == 'Mark as returned':
            tool.currentLocation = tool.defaultLocation
            tool.save()
        elif request.POST['action'] == 'Mark as missing':
            tool.status = 2
            tool.save()

    context['csTools'] = toolList

    return render( request, "tools/csadmin.html", context )


def messagepg( request):
    context = get_login_context( request.user )
    thisUser = UserData.objects.get( user = request.user )
    if request.method == 'POST':
        context['user'] = UserData.objects.get( id = request.POST['userID'] )
        toUser = context['user']
        if 'action' in request.POST:
            if request.POST['action'] == 'Send Message':
                mesg = request.POST['message']
                note = Notification.objects.create( to = toUser, sender = thisUser, date = timezone.now(), message = mesg )
                note.save()
                context['item'] = ''
                context['prompt'] = 'Message sent'
                return render( request, "tools/confirm.html", context  )
    return render( request, "tools/message.html", context )
    
    
def findTool( request ):
    context = get_login_context( request.user )

    # load up the context with all the variables we need
    context['types'] = ToolType.objects.all()

    shareZone = UserData.objects.get( user = request.user ).shareZone
    context['sheds'] = shareZone.getAllCSs()

    context['users'] = UserData.objects.filter( shareZone = shareZone )

    if request.method == 'POST':
        # Determine which pieces of data have and haven't been supplied
        hasName = False
        hasType = False
        hasLoc = False
        hasOwn = False

        hasCondition = True
        # for a typeless language, Python sure does like yelling at me about types
        condition = int( request.POST['cond'] )
        conditionFunc = request.POST['condCmpFnc']

        if request.POST['toolname'] != '':
            hasName = True
            name = request.POST['toolname']

        if request.POST['type'] != '-1':
            hasType = True
            tType = ToolType.objects.get( id = request.POST['type'] )

        if request.POST['loc'] != '-1':
            hasLoc = True
            location = CommunityShed.objects.get( id = request.POST['loc'] )

        if request.POST['own'] != '-1':
            hasOwn = True
            owner = UserData.objects.get( id = request.POST['own'] )

        if 'rest' in request.POST:
            if request.POST['rest'] == 'True':
                incRestricted = True
            else:
                incRestricted = False
        else:
            incRestricted = False

        if 'unrest' in request.POST:
            if request.POST['unrest'] == 'True':
                incUnRestricted = True
            else:
                incUnRestricted = False
        else:
            incUnRestricted = False

        gottenTools = []
        if conditionFunc == '=':
            gottenTools = Tool.objects.filter( condition = condition )
        elif conditionFunc == '<':
            for tool in Tool.objects.filter( condition__lt = condition ):
                gottenTools.append( tool )
        elif conditionFunc == '>':
            for tool in Tool.objects.filter( condition__gt = condition ):
                gottenTools.append( tool )

        gottenTools = [t for t in gottenTools if t.status == 1]

        if hasName:
            gottenTools = [t for i in gottenTools if t. name == name]
        if hasLoc:
            gottenTools = [t for t in gottenTools if t.defaultLocation == location]
        if hasType:
            gottenTools = [t for t in gottenTools if t.toolType == tType]
        if hasOwn:
            gottenTools = [t for t in gottenTools if t.toolOwner == owner]
        if not incRestricted:
            gottenTools = [t for t in gottenTools if t.isRestricted != True]
        if not incUnRestricted:
            gottenTools = [t for t in gottenTools if t.isRestricted != False]

        context['results'] = gottenTools

    return render( request, "tools/findTool.html", context )

def getStats( request ):
    context = get_login_context( request.user )
    userData = UserData.objects.get( user = request.user )
    sz = userData.shareZone
    activeBorrowers = []
    activeLenders = []
    usedTools = []
    #recentTools = []
    ratedUsers = []
    for u in sz.getActiveUsers():
        borrows = Reservation.objects.filter( borrower = u, status__gt = 1 )
        userWithBorrows = ( u, len(borrows) )
        activeBorrowers += [userWithBorrows]
    activeBorrowers.sort( key=lambda tup: tup[1], reverse=True )    
    mostActiveBorrowers = []
    for i in activeBorrowers:
        mostActiveBorrowers += [i[0]]
    if len(mostActiveBorrowers) > 5:
        mostActiveBorrowers = mostActiveBorrowers[0:5]
    context['mostActiveBorrowers'] = mostActiveBorrowers
    
    for u in sz.getActiveUsers():
        lends = Reservation.objects.filter( tool__owner = u, status__gt = 1 )
        userWithLends = ( u, len(lends) )
        activeLenders += [userWithLends]
    activeLenders.sort( key=lambda tup: tup[1], reverse=True )
    mostActiveLenders = []
    for i in activeLenders:
        mostActiveLenders += [i[0]]
    if len(mostActiveLenders) > 5:
        mostActiveLenders = mostActiveLenders[0:5]
    context['mostActiveLenders'] = mostActiveLenders
    
    for t in sz.getAllTools():
        used = Reservation.objects.filter( tool = t, status__gt = 1 )
        toolUsed = ( t, len(used) )
        usedTools += [toolUsed]
    usedTools.sort( key=lambda tup: tup[1], reverse=True )
    mostUsedTools = []
    for s in usedTools:
        mostUsedTools += [s[0]]
    if len(mostUsedTools) > 5:
        mostUsedTools = mostUsedTools[0:5]
    context['mostUsedTools'] = mostUsedTools
    
    for u in sz.getActiveUsers():
        ratedUsers += [u]
    ratedUsers.sort( key=lambda usr: usr.rating, reverse=True )
    if len(ratedUsers) > 5:
        ratedUsers = ratedUsers[0:5]
    context['highestRatedUsers'] = ratedUsers
    return render( request, "tools/statistics.html", context )

