from django.test import TestCase
from django.utils import timezone

from tools.views import *

class TestsByDavid( TestCase ):
    def test_password_invalid( self ):
        self.assertEqual( password_invalid( "short" ), True )
        self.assertEqual( password_invalid( "LongEnoughPassword" ), False )

    def test_birthday_invalid( self ):
        self.assertEqual( birthday_invalid( "2012-02-02" ), False )
        self.assertEqual( birthday_invalid( "2015-03-05" ), True )
        self.assertEqual( birthday_invalid( "2012-23-02" ), True )
        self.assertEqual( birthday_invalid( "01-01-2014" ), True )


class TestSystem( TestCase ):
    def test_createUser( self ):
        sys = System()
        self.assertEqual( sys.allUsers, [] )
        sys.createUser( "John", "dragon", timezone.now(), True, "here", None, "email" )
        user = User( name = "John", password = "dragon", birthday = timezone.now(), isMale = True, location = "here", email = "email" )
        self.assertEqual( sys.allUsers, [user] )
        self.assertEqual( sys.allUsers[0].isActive, False )

    def test_createShareZone( self ):
        sys = System()
        sys.createUser( "John", "dragon", timezone.now(), True, "here", None, "email" )
        self.assertEqual( sys.allShareZones, [] )
        sys.createShareZone( sys.allUsers[0], 10 )
        share = ShareZone( admin = sys.allUsers[0], restrictedAge = 10 )
        self.assertEqual( sys.allShareZones, [share] )

    def test_addUserToShareZone( self ):
        sys = System()
        sys.createShareZone( None, 10 )
        sys.createUser( "John", "dragon", timezone.now(), True, "here", sys.allShareZones[0], "email" )
        share = sys.allShareZones[0]
        user = sys.allUsers[0]
        self.assertEqual( share.approveUser( user ), 1 )


    def test_deactivateUser( self ):
        sys = System()
        sys.createUser( "admin", "dragon", timezone.now(), True, "here", None, "email" )
        sys.createShareZone( sys.allUsers[0], 10 )
        sys.createUser( "John", "dragon", timezone.now(), True, "here", sys.allShareZones[0], "email" )
        sys.allShareZones[0].approveUser( sys.allUsers[1] )

    def test_state_invalid( self ):
        stateUser = User( name = "John" )
        stateUser.giveState( "NY")
        self.assertEqual( state_invalid( "NY"), False)
        self.assertEqual( state_invalid ("TT"), True)

