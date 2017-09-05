from django.test import TestCase
import datetime

# Create your tests here.
from share_app.models import User

#tests for registration and login
def createUser(username, password, first_name, last_name, email, gender, dob, zip, address,
               rating, type, zone):
    return User.objects.create(username=username, password=password, first_name=first_name,
                               last_name=last_name, email=email, dob=dob, zip=zip,
                               address=address, rating=rating, type=type, zone=zone)
    
class testUserRegistration(TestCase):
    def test_index(self):
        resp = self.client.get('share_app/signup/')
        self.assertEqual(resp.status_code, 200)
        
    def test_empty_fields(self):
        resp = self.client.get('share_app/signup/')
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post("share_app/signup/", {'username': ''})
        self.assertFormError(resp, 'form', 'username', 'This field is required.')
        resp = self.client.post("share_app/signup/", {'password': ''})
        self.assertFormError(resp, 'form', 'password', 'This field is required.')
        resp = self.client.post("share_app/signup/", {'first_name': ''})
        self.assertFormError(resp, 'form', 'first_name', 'This field is required.')
        resp = self.client.post("share_app/signup/", {'last_name': ''})
        self.assertFormError(resp, 'form', 'last_name', 'This field is required.')
        resp = self.client.post("share_app/signup/", {'email': ''})
        self.assertFormError(resp, 'form', 'email', 'This field is required.')
        resp = self.client.post("share_app/signup/", {'gender': ''})
        self.assertFormError(resp, 'form', 'gender', 'This field is required.')
        resp = self.client.post("share_app/signup/", {'dob': ''})
        self.assertFormError(resp, 'form', 'dob', 'This field is required.')
        resp = self.client.post("share_app/signup/", {'zip': ''})
        self.assertFormError(resp, 'form', 'zip', 'This field is required.')
        resp = self.client.post("share_app/signup/", {'address': ''})
        self.assertFormError(resp, 'form', 'address', 'This field is required.')
        resp = self.client.post("share_app/signup/", {'rating': ''})
        self.assertFormError(resp, 'form', 'rating', 'This field is required.')
        resp = self.client.post("share_app/signup/", {'type': ''})
        self.assertFormError(resp, 'form', 'type', 'This field is required.')
        resp = self.client.post("share_app/signup/", {'zone': ''})
        self.assertFormError(resp, 'form', 'zone', 'This field is required.')

    def test_year_format(self):
        resp = self.client.post("share_app/signup/", {'year': ''})
        self.assertGreaterEqual(resp, 1000)
        self.assertLessEqual(resp, 9999)
        

#tests for tool sharing
def createTool(owner, name, description, pickupInformation, location, available, timesUsed):
    return ToolModel.objects.create(owner=owner, name=name, description=description, pickupInformation=pickupInformation,
                                    location=location, available=available, timesUsed=0)
    
class TestToolModel(TestCase):
    def test_index(self):
        resp = self.client.get('/share_app/addtool')
        self.assertEqual(resp.status_code, 200)
        
    def test_empty_fields(self):
        resp = self.client.get('/share_app/addtool')
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post("/share_app/addtool", {'name': ''})
        self.assertFormError(resp, 'form', 'name', 'This field is required.')
        resp = self.client.post("/share_app/addtool", {'description': ''})
        self.assertFormError(resp, 'form', 'description', 'This field is required.')
        resp = self.client.post("/share_app/addtool", {'pickupInformation': ''})
        self.assertFormError(resp, 'form', 'pickupInformation', 'This field is required.')
        
    def test_fields(self):
        resp = self.client.get('/share_app/addtool')
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post("share_app/addtool", {'name': 'Hammer'})
        self.assertEqual(resp, 'form', 'name', 'Hammer')
        resp = self.client.post("share_app/addtool", {'description': 'Hammer things'})
        self.assertEqual(resp, 'form', 'description', 'Hammer things')
        resp = self.client.post("share_app/addtool", {'pickupInformation': 'My house'})
        self.assertEqual(resp, 'form', 'pickupInformation', 'My house')

#test for creating shed
class TestCreateShed(TestCase):
    def test_index(self):
        resp = self.client.get('/share_app/addShed')
        self.assertEqual(resp.status_code, 200)