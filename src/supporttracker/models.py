from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from localflavor.us.models import PhoneNumberField
import datetime

STATE_CHOICES = (
('',''),
('AL','Alabama'),
('AK','Alaska'),
('AZ','Arizona'),
('AR','Arkansas'),
('CA','California'),
('CO','Colorado'),
('CT','Connecticut'),
('DE','Delaware'),
('FL','Florida'),
('GA','Georgia'),
('HI','Hawaii'),
('ID','Idaho'),
('IL','Illinois'),
('IN','Indiana'),
('IA','Iowa'),
('KS','Kansas'),
('KY','Kentucky'),
('LA','Louisiana'),
('ME','Maine'),
('MD','Maryland'),
('MA','Massachussets'),
('MI','Michigan'),
('MN','Minnesota'),
('MS','Mississippi'),
('MO','Missouri'),
('MT','Montana'),
('NE','Nebraska'),
('NV','Nevada'),
('NH','New Hampshire'),
('NJ','New Jersey'),
('NM','New Mexico'),
('NY','New York'),
('NC','North Carolina'),
('ND','North Dakota'),
('OH','Ohio'),
('OK','Oklahoma'),
('OR','Oregon'),
('PA','Pennsylvania'),
('RI','Rhode Island'),
('SC','South Carolina'),
('SD','South Dakota'),
('TN','Tennessee'),
('TX','Texas'),
('UT','Utah'),
('VT','Vermont'),
('WA','Washington'),
('WV','West Virginia'),
('WI','Wisconsin'),
('WY','Wyoming'),
)

STAGE_OPTIONS = (
('GET_INFO','Gather contact information'),
('MESSAGE','Need to send letter/message'),
('CALL','Need to call'),
('MEET','Meeting scheduled'),
('THANK','Send thank you'),
('FOLLOW_UP','Need to follow up'),
('STOP','Do not pursue further'),
('WAIT','Wait for a period of time'),
('MAINTAIN','Maintain'),
)

FREQ_OPTIONS = (
('Monthly','Monthly'),
('Quarterly','Quarterly'),
('Annually','Annually'),
('Semi-annually','Semi-annually'),
('One-time','One-time'),
)

class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	spouse_name = models.CharField(max_length=120,blank=True)
	street_address = models.CharField(max_length=120,null=True)
	city = models.CharField(max_length=120,null=True,blank=True)
	state = models.CharField(max_length=2,choices=STATE_CHOICES,null=True,blank=True)
	zip = models.charField(max_length=10,null=True,blank=True)
	
	def __str__(self):
		if self.spouse_name != '':
			return self.user.first_name + ' and ' + self.spouse_name + ' ' + self.user.last_name
		else:
			return self.user.first_name + ' ' + self.user.last_name

class StaffPerson(UserProfile):

	yearly_support_goal = models.IntegerField()

	def get_support_pct(self):
		rels = SupportRelationship.objects.filter(staff_person = self)
		total_raised = 0
		for rel in rels:
			total_raised += rel.amount
		pct = "%.f" % total_raised/self.yearly_support_goal
		return pct

class StaffAdmin(UserProfile):

	def __init__(self,*args,**kwargs):
		super (StaffAdmin,self).__init__(*args,**kwargs)


	
class Person(models.Model):
	title = models.CharField(max_length=20, blank=True)
	first_name = models.CharField(max_length=120)
	last_name = models.CharField(max_length=120)
	spouse_name = models.CharField(max_length=120, blank=True)
	phone_number = PhoneNumberField(null=True,blank=True)
	email_address = models.EmailField(blank=True)
	street_address = models.CharField(max_length=200, blank=True)
	city = models.CharField(max_length=100, blank=True)
	state = models.CharField(null=True,max_length=2, choices=STATE_CHOICES, blank=True)
	zip = models.CharField(max_length=10,blank=True)
	
	def __str__(self):
		if self.spouse_name != '' and self.spouse_name != None:
			return self.first_name + " and " + self.spouse_name + ' ' + self.last_name
		else:
			return self.first_name + ' ' + self.last_name
	
class SupportRelationship(models.Model):
	staff_person = models.ForeignKey(UserProfile)
	supporter = models.ForeignKey(Person)
	amount = models.IntegerField()
	frequency = models.CharField(max_length=255,choices=FREQ_OPTIONS)
	start_date = models.DateField()
	note = models.TextField(blank=True)
	date_entered = models.DateField(auto_now_add = True)
	date_updated = models.DateField(auto_now = True, blank=True, null=True)
	
class ContactRelationship(models.Model):
	staff_person = models.ForeignKey(UserProfile)
	contact = models.ForeignKey(Person)
	referred_by = models.IntegerField(blank=True, null=True)
	referral_note = models.CharField(max_length=500,blank=True)
	date_added = models.DateField()
	stage = models.CharField(max_length=255,choices=STAGE_OPTIONS)
	
class Letter(models.Model):
	staff_person = models.ForeignKey(UserProfile)
	contact = models.ForeignKey(Person)
	date_mailed = models.DateField(null=True, blank=True)
	note = models.TextField(blank=True)
		
class Meeting(models.Model):
	staff_person = models.ForeignKey(UserProfile)
	contact = models.ForeignKey(Person)
	date = models.DateField(null=True, blank=True)
	time = models.TimeField(null=True, blank=True)
	location = models.CharField(max_length=255, blank=True)
	note = models.TextField(blank=True)
	completed = models.BooleanField(default=False)

class Reminder(models.Model):
	staff_person = models.ForeignKey(UserProfile)
	contact = models.ForeignKey(Person)
	remind_date = models.DateField(null=True, blank=True)
	date_added = models.DateField()
	note = models.TextField(blank=True)
	completed = models.BooleanField(default=False)
	
class ThankYou(models.Model):
	staff_person = models.ForeignKey(UserProfile)
	contact = models.ForeignKey(Person)
	date = models.DateField(null=True, blank=True)
	sent = models.BooleanField(default=False)
	note = models.TextField(blank=True)
	
class VoiceMail(models.Model):
	staff_person = models.ForeignKey(UserProfile)
	contact = models.ForeignKey(Person)
	date_left = models.DateTimeField(null=True, blank=True)
	note = models.TextField(blank=True)
	
class Call(models.Model):
	staff_person = models.ForeignKey(UserProfile)
	contact = models.ForeignKey(Person)
	answered = models.BooleanField(default=True)
	left_message = models.BooleanField(default=False)
	date = models.DateField(blank=True,null=True)
	time = models.TimeField(blank=True,null=True)
	note = models.TextField(blank=True)
	voice_mail = models.ForeignKey(VoiceMail, null=True)
	completed = models.BooleanField(default=False)
	
class Referral(models.Model):
	staff_person = models.ForeignKey(UserProfile)
	referring_contact = models.ForeignKey(Person, related_name='referrer')
	referred_contact = models.ForeignKey(Person, related_name='referred')
	date_referred = models.DateField(null=True, blank=True)
	note = models.TextField(blank=True)
	
class Note(models.Model):
	staff_person = models.ForeignKey(UserProfile)
	contact = models.ForeignKey(Person)
	date = models.DateField(null=True, blank=True)
	note = models.TextField(blank=True)
	
class Message(models.Model):
	staff_person = models.ForeignKey(UserProfile)
	contact = models.ForeignKey(Person)
	date_to_send = models.DateField(null=True, blank=True)
	date_entered = models.DateField(default=datetime.date.today)
	method = models.TextField(blank=True)
	note = models.TextField(blank=True)
	sent = models.BooleanField(default=False)
	
class FollowUp(models.Model):
	staff_person = models.ForeignKey(UserProfile)
	contact = models.ForeignKey(Person)
	date = models.DateField(blank=True, null=True)
	time = models.TimeField(blank=True, null=True)
	method = models.TextField(blank=True, null=True)
	note = models.TextField(blank=True, null=True)
	completed = models.BooleanField(default=False)