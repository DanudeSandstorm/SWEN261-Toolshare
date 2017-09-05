from django.test import TestCase
from share_app.models import Member
import datetime

class MemberTestCase(TestCase):
	def setUp(self):
		Member.objects.create(
			username="CD12",
			password="password",
			first_name="Charles",
			last_name="Darwin",
			email="cd12@gmail.com",
			gender="M",
			dob="02/12/1809",
			zip="14623",
			address="Utah",
			rating=2.5,
			type=0,
			zone="Canada"
		)
	
	def test_username(self):
		member = Member.objects.get(username="CD12")
		self.assertEqual(member.password, "password")
		self.assertEqual(member.first_name, "Charles")
		self.assertEqual(member.last_name, "Darwin")
		self.assertEqual(member.email, "wrongemail@gmail.com")		#should throw error
		self.assertEqual(member.gender, "M")
		self.assertEqual(member.dob, "02/12/1809")
		self.assertEqual(member.zip, "14623")
		self.assertEqual(member.address, "Utah")
		self.assertEqual(member.rating, 2.5)
		self.assertEqual(member.type, 0)
		self.assertEqual(member.zone, "Canada")
		
		
	