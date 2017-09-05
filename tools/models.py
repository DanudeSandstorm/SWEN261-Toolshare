from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
import hashlib
import uuid
    
class UserData( models.Model ): 
    user = models.ForeignKey( User )
    
    birthday = models.DateField()
    isMale = models.BooleanField()
    location = models.CharField( max_length = 200 ) 
    rating = models.FloatField( default = 0 )
    numRatings = models.IntegerField( default = 0 )
    shareZone = models.ForeignKey( 'ShareZone' )
    house = models.ForeignKey( 'CommunityShed' )

    def getTools(self):
        tools = Tool.objects.filter(owner = self, status = 1)
        return tools
    
    def getRating(self):
        rating = self.rating
        if rating < 0.001:
            rating = 'Unrated'
        return rating
        
    def updateUser(self,firstName,lastName,password,email,location,birthday):
        self.user.first_name = firstName
        self.user.last_name = lastName
        self.user.set_password(password)
        self.user.email = email
        self.user.username = email   
        self.location = location
        self.birthday = birthday
        self.user.save()
        self.save()

    
    def __str__( self ):
        return self.user.first_name + ' ' + self.user.last_name

class Notification( models.Model ):
    to = models.ForeignKey( 'UserData', related_name = 'recvMsg' )
    sender = models.ForeignKey( 'UserData', related_name = 'sentMsg' )
    date = models.DateTimeField()
    message = models.TextField()
    isNew = models.BooleanField( default = True )

class Reservation( models.Model ):
    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
    tool = models.ForeignKey( 'Tool' )
    borrower = models.ForeignKey( 'UserData' )
    status = models.IntegerField()
    comments = models.TextField( blank = True )

class ToolType( models.Model ):
    type = models.CharField( max_length = 200 )
    
    def __str__( self ):
        return self.type
    
class Tool (models.Model):
    name = models.CharField( max_length = 200 )
    owner = models.ForeignKey( UserData, related_name = 'ownedTool' )
    toolType = models.ForeignKey( 'ToolType' )
    defaultLocation = models.ForeignKey( 'CommunityShed', related_name = 'storedTool' )
    currentLocation = models.ForeignKey( 'CommunityShed', related_name = 'heldTool' )
    manufacturer = models.CharField( max_length = 200 )
    condition = models.IntegerField()
    additionalDetails = models.TextField()
    isRestricted = models.BooleanField()
    status = models.IntegerField( default = 1 )
        
    def __str__( self ):
        return self.name

class ShareZone( models.Model ):

    name = models.CharField( max_length = 200 )
    restrictedAge = models.IntegerField()
    isActive = models.BooleanField()

    def getActiveUsers(self):
        users = UserData.objects.filter(shareZone = self, user__is_active = True)
        return users
    
    def getInactiveUsers(self):
        users = UserData.objects.filter(shareZone = self, user__is_active = False)
        return users
    #This is a change
    
    def getAllCSs(self):
        cSheds = CommunityShed.objects.filter(shareZone = self)
        return cSheds
        
    def getCSs(self):
        cSheds = CommunityShed.objects.filter(shareZone = self, isHouse = False)
        return cSheds
        
    def getTools(self):
        cSheds = self.getAllCSs()
        tools=[]
        for shd in cSheds:
            tools += Tool.objects.filter(defaultLocation = shd, status = 1)
        return tools
        
    def getAllTools(self):
        cSheds = self.getAllCSs()
        tools=[]
        for shd in cSheds:
            tools += Tool.objects.filter(defaultLocation = shd)
        return tools
    
    def getAvailableTools( self ):
        tools = Tool.objects.filter( defaultLocation__shareZone = self, status = 1 )
        aTools = []
        for t in tools:
            if t.defaultLocation == t.currentLocation:
                aTools.append( t )
        return aTools

    def getUnavailableTools( self ):
        tools = Tool.objects.filter( defaultLocation__shareZone = self, status = 1 )
        uTools = []
        for t in tools:
            if t.defaultLocation != t.currentLocation:
                uTools.append( t )
        return uTools
       
    def __str__( self ):
        return self.name
        
        
class CommunityShed( models.Model ):
    name = models.CharField( max_length = 200 ) 
    maxNumberOfTools = models.IntegerField()
    numberOfTools = models.IntegerField()
    location = models.CharField( max_length = 200 )
    shareZone = models.ForeignKey( 'ShareZone' )
    isHouse = models.BooleanField()
    
    def getDefTools(self):
        tools = Tool.objects.filter(defaultLocation = self, status = 1)
        return tools
        
    def getCurTools(self):
        tools = Tool.objects.filter(currentLocation = self, status = 1)
        return tools    
        
        
    def __str__( self ):
        return self.name
