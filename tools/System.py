from django.db import models

class System( models.Model ):

    allUsers = []
    superAdmins = []
    allShareZones = []


    def createUser(name, password, birthday, isMale, location, email):
	
        newUser = User(name,password,birthday,isMale,location,email)		
        self.allUsers.append(newUser)
        return 1

    def deactivateUser(User):

        User.isActive = False
        return 1

	
    def createShareZone(admin, restrictedAge):

        newShare = ShareZone()
        self.allShareZones.append(newShare)
        return 1

	
    def deleteShareZone(ShareZone):

        ShareZone.isActive = False
	for Usr in ShareZone.shareZoneUsers:
            Usr.isActive = False
        return 1


    def makeSuperAdmin(User):

        self.superAdmins.append(User)
	return 1

    def removeSuperAdmin(User):

        self.superAdmins.remove(User)
        return 1




