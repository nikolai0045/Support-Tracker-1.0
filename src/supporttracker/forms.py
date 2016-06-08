from django import forms
from .models import Person, STATE_CHOICES, STAGE_OPTIONS, FREQ_OPTIONS, ContactRelationship, Call, FollowUp, ThankYou, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import authenticate, login
from localflavor.us.forms import USPhoneNumberField
from bootstrap3_datetime.widgets import DateTimePicker
import datetime
from collections import OrderedDict
from djangoformsetjs.utils import formset_media_js
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, HTML, ButtonHolder
from crispy_forms.bootstrap import FormActions




def get_contact_list(user):

	profile = user.userprofile
	#get list of all contact relationships	
	contact_relationships = profile.contactrelationship_set.all()
		
	#define mutable iterable to contain contacts
	contacts = []
		
	#cycle through all relationships
	for rel in contact_relationships:
		
		#build display name for choices tuple
		if rel.contact.spouse_name != '' and rel.contact.spouse_name != None:
			display_name = rel.contact.first_name + ' and ' + rel.contact.spouse_name + ' ' + rel.contact.last_name
		else:
			display_name = rel.contact.first_name + ' ' + rel.contact.last_name
			
		#add contact into contact list
		contact_to_add = (rel.contact.pk, display_name)
		contacts.append(contact_to_add)
		
	#convert list of contacts to a tuple
	#contacts = tuple(contacts)
	
	return contacts

def get_supporter_list(user):

	#get list of all support relationships	
	support_relationships = user.userprofile.supportrelationship_set.all()
	
	#define mutable iterable to contain supporters
	supporters = []
	
	#cycle through all relationships
	for rel in support_relationships:
	
		#build display name for choices tuple
		if rel.supporter.spouse_name != '' and rel.supporter.spouse_name != None:
			display_name = rel.supporter.first_name + ' and ' + rel.supporter.spouse_name + ' ' + rel.supporter.last_name
		else:
			display_name = rel.supporter.first_name + ' ' + rel.supporter.last_name
		
		#add supporter into supporter list
		supporter_to_add = (rel.supporter, display_name)
		supporter += supporter_to_add
	
	#convert list of supporters to a tuple
	supporters = tuple(supporters)

	return supporters

class LoginForm(forms.Form):
	username = forms.CharField(max_length=255, required=True)
	password = forms.CharField(widget=forms.PasswordInput, required=True)
	
	def __init__(self,*args,**kwargs):
		super (LoginForm,self).__init__(*args,**kwargs)
		self.helper = FormHelper()
		self.helper.layout = Layout(
			Div(
				'username',
				'password'
			),
			FormActions(
				Submit('submit', 'Login', css_class='btn btn-default', style="margin-top:15px")
			)
		)
		
	def clean(self):
		print "cleaning"
		username = self.cleaned_data.get('username')
		password = self.cleaned_data.get('password')
		user = authenticate(username=username, password=password)
		if not user or not user.is_active:
			raise forms.ValidationError("Sorry, that login was invalid. Please try again.")
		return self.cleaned_data
	
	def login(self, request):
		username = self.cleaned_data.get('username')
		password = self.cleaned_data.get('password')
		user = authenticate(username=username, password=password)
		return user

class ChangePasswordForm(PasswordChangeForm):

	def __init__(self,*args,**kwargs):
		for arg in kwargs:
			print arg
		super (ChangePasswordForm,self).__init__(*args,**kwargs)
		
		self.helper = FormHelper(self)
		self.helper.form_id = 'change_password_form'
		self.helper.layout = Layout(
			Div(
				'old_password',
				'new_password1',
				'new_password2',
				css_class = ('form-group')
			),
			FormActions(
				Submit('submit', 'Change Password', css_class='btn btn-default')
			)
		)
		
		

class UpdateStageForm(forms.Form):

	def clean(self):
		cleaned_data = super(UpdateStageForm,self).clean()
				
		if cleaned_data['stage'] == 'MESSAGE':
			cleaned_data['date'] = cleaned_data['message_date']
			cleaned_data['method'] = cleaned_data['message_method']
			cleaned_data['note'] = cleaned_data['message_note']
		elif cleaned_data['stage'] == 'CALL':
			cleaned_data['date'] = cleaned_data['call_date']
			cleaned_data['time'] = cleaned_data['call_time']
			cleaned_data['note'] = cleaned_data['call_note']
		elif cleaned_data['stage'] == 'MEET':
			cleaned_data['date'] = cleaned_data['meeting_date']
			cleaned_data['time'] = cleaned_data['meeting_time']
			cleaned_data['location'] = cleaned_data['meeting_location']
			cleaned_data['note'] = cleaned_data['meeting_note']
		elif cleaned_data['stage'] == 'THANK':
			cleaned_data['date'] = cleaned_data['thank_you_date']
			cleaned_data['note'] = cleaned_data['thank_you_note']
		elif cleaned_data['stage'] == 'FOLLOW_UP':
			cleaned_data['date'] = cleaned_data['follow_up_date']
			cleaned_data['time'] = cleaned_data['follow_up_time']
			cleaned_data['note'] = cleaned_data['follow_up_note']
			cleaned_data['method'] = cleaned_data['follow_up_method']
			
		cleaned_data['new_stage'] = cleaned_data['stage']
		return cleaned_data

  
	def __init__(self,*args,**kwargs):
		self.user = kwargs.pop('user',User)
		self.contact = kwargs.pop('contact',False)

		super (UpdateStageForm,self).__init__(*args,**kwargs)

		self.fields['stage'] = forms.TypedChoiceField(
			choices=STAGE_OPTIONS,
			required=True,
			label = 'What\'s next?',
		)

		self.fields['stage'].widget.attrs = {'class':'stageSelect'}

		if self.contact:
			contact_rel = ContactRelationship.objects.get(contact=self.contact,staff_person=self.user.userprofile)
			print contact_rel
			self.fields['stage'].initial = contact_rel.stage

		self.fields['message_date'] = forms.DateField(
			input_formats=['%m/%d/%y'],
			required = False,
			widget=DateTimePicker(
			attrs={'class':'form-control','id':'message_date'},
			options={
			'format':'MM/DD/YY',
			'pickTime':False,
			},
			),
		)


		self.fields['message_method'] = forms.CharField(
			max_length = 30,
			required = False,
		)

		self.fields['message_method'].widget.attrs = {'id':'message_method'}

		self.fields['message_note'] = forms.CharField(
			max_length=200,
			required = False,
			widget = forms.Textarea,
		)

		self.fields['message_note'].widget.attrs = {'id':'message_note'}

		self.fields['call_date'] = forms.DateField(
			input_formats=['%m/%d/%y'],
			required = False,
			widget = DateTimePicker(
			attrs = {'id':'call_date'},
			options = {
			'format':'MM/DD/YY',
			'pickTime':False,
			}
			)
		)

		self.fields['call_time'] = forms.TimeField(
			input_formats=['%I:%M %p'],
			required = False,
			widget = DateTimePicker(
			options = {
			'format':'HH mm a',
			'pickDate':False,
			'pickSeconds':False,
			}
			)
		)
		self.fields['call_note'] = forms.CharField(
			max_length=200,
			widget = forms.Textarea,
			required = False,
		)

		self.fields['call_note'].widget.attrs = {'id':'call_note'}

		self.fields['meeting_date'] = forms.DateField(
			input_formats=['%m/%d/%y'],
			required = False,
			widget = DateTimePicker(
			attrs = {'id':'meeting_date'},
			options = {
			'format':'MM/DD/YY',
			'pickTime':False,
			}
			)
		)

		self.fields['meeting_time'] = forms.TimeField(
			input_formats=['%I:%M %p'],
			required = False,
			widget=DateTimePicker(
			attrs={'class':'form-control','id':'meeting_time'},
			options={
			'format':'HH:mm a',
			'pickDate':False,
			'pickSeconds':False,
			},
			),
		)

		self.fields['meeting_location'] = forms.CharField(
			max_length = 100,
			required = False,
		)

		self.fields['meeting_location'].widget.attrs = {'id':'meeting_location'}

		self.fields['meeting_note'] = forms.CharField(
			max_length = 200,
			required = False,
			widget = forms.Textarea,
		)

		self.fields['meeting_note'].widget.attrs = {'id':'meeting_note'}

		self.fields['thank_you_date'] = forms.DateField(
			input_formats=['%m/%d/%y'],
			required = False,
			widget = DateTimePicker(
			attrs = {'id':'thank_you_date'},
			options = {
			'format':'MM/DD/YY',
			'pickTime':False,
			}
			)
		)

		self.fields['thank_you_note'] = forms.CharField(
			max_length = 200,
			required = False,
			widget = forms.Textarea,
		)

		self.fields['thank_you_note'].widget.attrs = {'id':'thank_you_note'}

		self.fields['follow_up_date'] = forms.DateField(
			input_formats=['%m/%d/%y'],
			required = False,
			widget = DateTimePicker(
			attrs = {'id':'follow_up_date'},
			options = {
			'format':'MM/DD/YY',
			'pickTime':False,
			}
			)
		)

		self.fields['follow_up_time'] = forms.TimeField(
			input_formats=['%I:%M %p'],
			required = False,
			widget=DateTimePicker(
			attrs={'class':'form-control','id':'follow_up_time'},
			options={
			'format':'HH:mm a',
			'pickDate':False,
			'pickSeconds':False,
			},
			),
		)

		self.fields['follow_up_method'] = forms.CharField(
			max_length = 30,
			required = False,
		)

		self.fields['follow_up_note'] = forms.CharField(
			max_length = 200,
			required = False,
			widget = forms.Textarea,
		)
				
		
		

class RecordMeetingModalForm(forms.Form):
	
	def __init__(self,*args,**kwargs):
		self.user = kwargs.pop('user',User)
		self.contact = kwargs.pop('contact',False)
		
		super (RecordMeetingModalForm, self).__init__(*args,**kwargs)

		if self.contact:
		
			self.fields['contact_id'] = forms.IntegerField(
				widget=forms.HiddenInput(),
				initial=self.contact
			)
			
		else:
		
			self.fields['contact_id'] = forms.TypedChoiceField(
				choices = get_contact_list(self.user),
				label = 'Contact',
			)
				
			self.fields['date'] = forms.DateField(
			input_formats=['%m/%d/%y'],
			initial = datetime.date.today,
			widget=DateTimePicker(
			attrs={'class':'form-control'},
			options={
			'format':'MM/DD/YY',
			'pickTime':False,
			},
			),
			)
			
			self.fields['time'] = forms.TimeField(
			input_formats=['%I:%M %p'],
			widget=DateTimePicker(
			attrs={'class':'form-control'},
			options={
			'format':'HH:mm a',
			'pickDate':False,
			'pickSeconds':False,
			},
			),
			)
			
			self.fields['location'] = forms.CharField(
			max_length=255,
			required=False
			)

	meeting_id = forms.IntegerField(
		widget=forms.HiddenInput(),
		required=False,
		initial=None,
	)	
	
	meeting_note = forms.CharField(max_length=500,required=False,widget=forms.Textarea)
	
	stage = forms.CharField(
		required=False,
		widget = forms.HiddenInput(),
		)
		
class ScheduleFollowUpModalForm(forms.Form):

	def __init__(self,*args,**kwargs):
	
		self.user = kwargs.pop('user',User)
		
		super (ScheduleFollowUpModalForm,self).__init__(*args,**kwargs)
		
		self.fields['contact'] = forms.TypedChoiceField(
		choices = get_contact_list(self.user)
		)
	
	date = forms.DateField(
	input_formats=['%m/%d/%y'],
	required = False,
	initial = datetime.date.today(),
	label="Date of follow up",
	widget=DateTimePicker(
		options = {
		'format':'MM/DD/YY',
		'pickTime':False,
		}
	)
	)
	
	time = forms.TimeField(
	input_formats=['%I:%M %p'],
	required = False,
	initial = datetime.time(),
	label = 'Time of follow up',
	widget = DateTimePicker(
		options={
		'format': 'hh:mm a',
		'pickDate':False,
		'pickSeconds':False,
		}
	)
	)
	
	method = forms.CharField(
	required = False,
	max_length = 50,
	label = 'Method of contact',
	)
	
	note = forms.CharField(
	required = False,
	max_length = 250,
	label = 'Note about this follow up',
	widget = forms.Textarea
	)
	
class RecordFollowUpModalForm(forms.Form):

	def __init__(self,*args,**kwargs):
		
		self.user = kwargs.pop('user',User)
		self.fup_id = kwargs.pop('fup_id',False)
		
		if self.fup_id:
			self.contact = FollowUp.objects.get(pk=self.fup_id).contact
			self.contact_rel = ContactRelationship.objects.get(contact=self.contact,staff_person=self.user.userprofile)
			
		super (RecordFollowUpModalForm,self).__init__(*args,**kwargs)
		
		self.fields['stage'] = forms.TypedChoiceField(
		choices=STAGE_OPTIONS,
		required=True,
		label='What\'s next?',
		)
		
		self.fields['contact'] = forms.TypedChoiceField(
		choices=get_contact_list(self.user),
		)
		
		self.fields['date'] = forms.DateField(
		input_formats=['%m/%d/%y'],
		required=False,
		initial=datetime.date.today(),
		label='Date of follow up',
		widget=DateTimePicker(
			options={
			'format':'MM/DD/YY',
			'pickTime':False,
			},
		),)
		
		self.fields['time'] = forms.TimeField(
		label = 'Time of follow up',
		required = False,
		initial = datetime.time(),
		input_formats = ['%I:%M %p'],
		widget=DateTimePicker(
		options={
		"format":"hh:mm a",
		"pickSeconds":False,
		'pickDate':False,
		},
		),
		)
		
		self.fields['method'] = forms.CharField(
		max_length = 50,
		required = False,
		)
		
		
		if self.fup_id:
		
			self.fields['fup_id'] = forms.IntegerField(
			initial = self.fup_id,
			widget = forms.HiddenInput(),
			)
			
			self.fields['contact'].required = False
			self.fields['contact'].widget=forms.HiddenInput()
			self.fields['date'].disabled=True
			self.fields['time'].disabled=True
			self.fields['stage'].initial = self.contact_rel.stage
		
	note = forms.CharField(
	widget = forms.Textarea,
	required = False,
	)
		
class UpdateReminderModalForm(forms.Form):
	
	def __init__(self,*args,**kwargs):
		
		self.user = kwargs.pop('user',User)
		self.contact_id = kwargs.pop('contact_id',None)
		self.reminder_id = kwargs.pop('reminder_id',None)
		contact = Person.objects.get(pk=self.contact_id)
		contact_rel = ContactRelationship.objects.get(contact=contact,staff_person=self.user.userprofile)
		super (UpdateReminderModalForm,self).__init__(*args,**kwargs)
		
		self.fields['stage'] = forms.TypedChoiceField(
		choices=STAGE_OPTIONS,
		label="What's next?",
		initial = contact_rel.stage,
		)
		
		self.fields['reminder_id'] = forms.IntegerField(
		initial=self.reminder_id,
		widget=forms.HiddenInput(),
		)
		
		self.fields['contact'] = forms.TypedChoiceField(
		choices=get_contact_list(self.user),
		initial=self.contact_id,
		widget=forms.HiddenInput(),
		)
		
class RecordMessageModalForm(forms.Form):
	
	def __init__(self,*args,**kwargs):
	
		self.user = kwargs.pop('user',User)
		self.contact_id = kwargs.pop('contact_id',False)
		self.message_id = kwargs.pop('message_id',False)
		
		if self.contact_id:
			contact = Person.objects.get(pk=self.contact_id)
			contact_rel = ContactRelationship.objects.get(contact=contact,staff_person=self.user.userprofile)
		
		super(RecordMessageModalForm,self).__init__(*args,**kwargs)
		
		self.fields['stage'] = forms.TypedChoiceField(
		choices=STAGE_OPTIONS,
		label='What\'s next?',
		)
		
		if self.message_id:
		
			self.fields['message_id'] = forms.IntegerField(
			initial = self.message_id,
			widget = forms.HiddenInput(),
			)
		
		if self.contact_id:

			self.fields['contact'] = forms.TypedChoiceField(
			choices = get_contact_list(self.user),
			initial = self.contact_id,
			widget = forms.HiddenInput(),
			)
			
			self.fields['stage'].initial = contact_rel.stage
			
		else:
			
			self.fields['contact'] = forms.TypedChoiceField(
			choices = get_contact_list(self.user),
			required = True,
			)
			
			self.fields['method'] = forms.CharField(
			required = False,
			max_length = 100,
			)
			
			self.fields['note'] = forms.CharField(
			required = False,
			max_length = 250,
			widget = forms.Textarea,
			)
			
			self.fields['date_to_send'] = forms.DateField(
			required = True,
			widget=DateTimePicker(
				options={
				'format':'MM/DD/YY',
				'pickTime':False,
				},
			),
			initial=datetime.date.today(),
			label="Sent on",
			)
			
class ScheduleMessageModalForm(forms.Form):

	def __init__(self,*args,**kwargs):
	
		self.user = kwargs.pop('user',User)
		
		super(ScheduleMessageModalForm,self).__init__(*args,**kwargs)
		
		self.fields['contact'] = forms.TypedChoiceField(
		choices = get_contact_list(self.user),
		required = True,
		)
		
	date_to_send = forms.DateField(
		input_formats=['%m/%d/%y'],
		required=True,
		label='Send message on:',
		widget=DateTimePicker(
			options={
			'format':'MM/DD/YY',
			'pickTime':False,
			},
		),
	)
	
	method = forms.CharField(
		max_length = 100,
		required = False,
	)
	
	note = forms.CharField(
		max_length = 250,
		widget = forms.Textarea,
		required = False,
	)
	
class ScheduleCallModalForm(forms.Form):
	
	def __init__(self,*args,**kwargs):
	
		self.user = kwargs.pop('user',User)
		super (ScheduleCallModalForm,self).__init__(*args,**kwargs)
		
		self.fields['contact'] = forms.ChoiceField(
		choices = get_contact_list(self.user),
		required = True,
		)
	
	date = forms.DateField(
		input_formats=['%m/%d/%y'],
		required=False,
		label='Call on:',
		widget=DateTimePicker(
			options={
			'format':'MM/DD/YY',
			'pickTime':False,
			},
		),	
	)
	
	time = forms.TimeField(
		input_formats=['%I:%M %p'],
		required = False,
		widget=DateTimePicker(
		attrs={'class':'form-control'},
		options={
		'format':'hh:mm a',
		'pickDate':False,
		'pickSeconds':False,
		},
		),	
	)

	note = forms.CharField(
		max_length = 250,
		widget = forms.Textarea,
		required = False,
	)
class RecordCallModalForm(forms.Form):

	def __init__(self,*args,**kwargs):
	
		self.user = kwargs.pop('user',User)
		self.call_id = kwargs.pop('call_id',False)
		
		super (RecordCallModalForm, self).__init__(*args,**kwargs)
		
		self.fields['stage'] = forms.ChoiceField(
		choices=STAGE_OPTIONS,
		required=True,
		label = 'What\'s next?',
		)
		
		if self.call_id:
		
			call = Call.objects.get(pk=self.call_id)
			contact = call.contact
			contact_rel = ContactRelationship.objects.get(contact=contact,staff_person=self.user.userprofile)
			
			self.fields['call_id'] = forms.IntegerField(
			initial = self.call_id,
			required = True,
			widget = forms.HiddenInput(),
			)
			
			self.fields['stage'].inital = contact_rel.stage
			
		else:
		
			self.fields['contact'] = forms.TypedChoiceField(
			choices = get_contact_list(self.user),
			required = True,
			)
		
	answered_cb = forms.BooleanField(
	label='Answered',
	required=False,
	initial=True,
	)
	
	answered_cb.widget.attrs = {'id':'answered_cb'}
	
	left_message_cb = forms.BooleanField(
	label='Left message:',
	required=False,
	)
	
	left_message_cb.widget.attrs = {'id':'left_message_cb'}
	
	answered_hidden = forms.BooleanField(
	initial=True,
	required=False,
	widget=forms.HiddenInput(
	attrs = {'id':'answered_hidden'},
	),
	)
	
	left_message_hidden = forms.BooleanField(
	initial=False,
	required=False,
	widget=forms.HiddenInput(
	attrs = {'id':'left_message_hidden'},
	),
	)
		
	time = forms.TimeField(
	label = 'Time of call',
	required = False,
	input_formats = ['%I:%M %p'],
	widget=DateTimePicker(
	options={
	"format":"hh:mm a",
	"pickSeconds":False,
	'pickDate':False,
	},
	),
	)
	
	date = forms.DateField(
	label = 'Date called',
	initial = datetime.date.today,
	required = False,
	input_formats = ['%m-%d-%y'],
	widget = DateTimePicker(
	options = {
	'format':'MM-DD-YY',
	'pickTime':False,
	}
	)
	)
	
	note = forms.CharField(
	max_length=500,
	widget=forms.Textarea,
	required=False,
	)
	
	voice_mail_note = forms.CharField(
	max_length=500,
	widget=forms.Textarea,
	required=False
	)

class ScheduleThankYouModalForm(forms.Form):
	
	def __init__(self,*args,**kwargs):
		self.user = kwargs.pop('user',User)
		
		super (ScheduleThankYouModalForm,self).__init__(*args,**kwargs)
		
		self.fields['contact'] = forms.TypedChoiceField(
		choices = get_contact_list(self.user),
		required = True,
		)
		
		self.fields['date'] = forms.DateField(
		label = 'Date to send',
		initial = datetime.date.today,
		required = False,
		input_formats = ['%m-%d-%y'],
		widget = DateTimePicker(
		options = {
		'format':'MM-DD-YY',
		'pickTime':False,
		}
		),
		)
		
		self.fields['note'] = forms.CharField(
		label = 'Note',
		max_length = 200,
		required = False,
		widget = forms.Textarea,
		)

class RecordThankYouModalForm(forms.Form):

	def __init__(self,*args,**kwargs):
		self.user = kwargs.pop('user',User)
		self.ty_id = kwargs.pop('ty_id',False)
		
		super (RecordThankYouModalForm,self).__init__(*args,**kwargs)
		
		self.fields['contact'] = forms.TypedChoiceField(
		choices = get_contact_list(self.user),
		required = True,
		)
		
		self.fields['date'] = forms.DateField(
		label = 'Date sent',
		initial = datetime.date.today,
		required = False,
		input_formats = ['%m-%d-%y'],
		widget = DateTimePicker(
		options = {
		'format':'MM-DD-YY',
		'pickTime':False,
		}
		),
		)
		
		self.fields['stage'] = forms.TypedChoiceField(
		choices = STAGE_OPTIONS,
		required = True,
		)
		
		self.fields['note'] = forms.CharField(
		label = "Note",
		required = False,
		widget = forms.Textarea,
		max_length=200,
		)
		
		if self.ty_id:
			ty = ThankYou.objects.get(pk=self.ty_id)
			self.fields['contact'].required=False
			self.fields['contact'].widget = forms.HiddenInput()

class AddReminder(forms.Form):
	
	def __init__(self,*args,**kwargs):
		self.user = kwargs.pop('user',User)
		self.hide_contact = kwargs.pop('hide_contact',False)
		
		super (AddReminder, self).__init__(*args,**kwargs)


		self.fields['contact']=forms.TypedChoiceField(
			choices = get_contact_list(self.user),
			label = 'Contact',
			)
			
		if self.hide_contact:
			self.fields['contact'].widget=forms.HiddenInput()

	note = forms.CharField(
		max_length=500,
		required=False,
		label="Remind me to..."
	)
	
	remind_date = forms.DateField(
		required=True,
		widget=DateTimePicker(
			options={
			'format':'MM/DD/YY',
			'pickTime':False,
			},
		),
	)
	
class AddContactForm(forms.Form):

	def __init__(self,*args,**kwargs):
	
		stage_form = kwargs.pop('stage_form',False)
		super (AddContactForm,self).__init__(*args,**kwargs)
		if stage_form:
			self.fields['stage'].required=False,
			self.fields['stage'].widget = forms.HiddenInput()
	
	title = forms.CharField(
		max_length = 20,
		required=False,
		label='Title'
		)
								
	first_name = forms.CharField(
		max_length = 120,
		label='First Name'
		)
									
	last_name = forms.CharField(
		max_length = 120,
		label = 'Last Name'
		)
									
	spouse_name = forms.CharField(
		max_length = 120,
		required=False,
		label='Spouse\'s name'
		)
										
	phone_number = USPhoneNumberField(
		label="Phone Number",
		required=False,
	)
										
	email_address = forms.EmailField(
		required=False,
		label = 'Email Address'
		)
										
	street_address = forms.CharField(
		max_length=200,
		required=False,
		label = 'Street Address',
		)
										
	city = forms.CharField(
		max_length=100,
		required=False,
		label = 'City'
		)
		
	state = forms.ChoiceField(
		choices=STATE_CHOICES,
		required=False,
		label='State'
		)
		
	zip = forms.RegexField(
		required=False,
		regex='^\d{5}(?:[-\s]\d{4})?$',
		error_messages = {'invalid': 'Please enter a valid zip code (5 digit zip or zip+4 accepted).'},
		label='ZIP Code'
		)
		
	stage = forms.ChoiceField(
		choices=STAGE_OPTIONS,
		required=True,
		label = 'What to do next with this person:'
		)

class AddReferralForm(forms.Form):	

	def clean(self):
		cleaned_data = super(AddReferralForm,self).clean()
		
		cleaned_data['stage_data'] = {}
		cleaned_data['stage_data']['new_stage'] = cleaned_data['stage']
		title = cleaned_data('title')
		first_name = cleaned_data('first_name')
		last_name = cleaned_data('last_name')
		spouse_name = cleaned_data('spouse_name')
		phone_number = cleaned_data('phone_number')
		email_address = cleaned_data('email_address')
		street_address = cleaned_data('street_address')
		city = cleaned_data('city')
		state = cleaned_data('state')
		zip = cleaned_data('zip')
		note = cleaned_data('note')
		stage = cleaned_data('stage')
		
		if not first_name and not last_name and not stage:
			raise forms.ValidationError("Incomplete form")
			
		return cleaned_data
			
	def __init__(self,*args,**kwargs):
		self.user = kwargs.pop('user',User)
		self.contact = kwargs.pop('contact',False)

		super (AddReferralForm,self).__init__(*args,**kwargs)

		self.fields['stage'] = forms.TypedChoiceField(
			choices=STAGE_OPTIONS,
			required=True,
			label = 'What\'s next?',
		)

		self.fields['stage'].widget.attrs = {'class':'refStageSelect'}

		
	title = forms.CharField(
		max_length = 20,
		required=False,
		label='Title'
		)
								
	first_name = forms.CharField(
		max_length = 120,
		required=False,
		label='First Name'
		)
									
	last_name = forms.CharField(
		max_length = 120,
		required=False,
		label = 'Last Name'
		)
									
	spouse_name = forms.CharField(
		max_length = 120,
		required=False,
		label='Spouse\'s name'
		)
										
	phone_number = USPhoneNumberField(
		label="Phone Number",
		required=False,
	)
										
	email_address = forms.EmailField(
		required=False,
		label = 'Email Address'
		)
										
	street_address = forms.CharField(
		max_length=200,
		required=False,
		label = 'Street Address',
		)
										
	city = forms.CharField(
		max_length=100,
		required=False,
		label = 'City'
		)
		
	state = forms.ChoiceField(
		choices=STATE_CHOICES,
		required=False,
		label='State'
		)
		
	zip = forms.RegexField(
		required=False,
		regex='^\d{5}(?:[-\s]\d{4})?$',
		error_messages = {'invalid': 'Please enter a valid zip code (5 digit zip or zip+4 accepted).'},
		label='ZIP Code'
		)
		
	note = forms.CharField(
		max_length=500,
		required=False,
	)
		
class AddThankYouForm(forms.Form):

	def __init__(self,*args,**kwargs):
		self.user = kwargs.pop('user',User)
		super (AddThankYouForm, self).__init__(*args,**kwargs)
		
		new_fields = OrderedDict()
		
		self.fields['contact']=forms.TypedChoiceField(
			choices = get_contact_list(self.user),
			label = 'Mailed to:'
			)
					
	note = forms.CharField(
		max_length=500,
		widget=forms.Textarea,
		required=False
		)
	
	date_sent = forms.DateField(
		initial=datetime.date.today
		)
					
class AddLetterForm(forms.Form):

	def __init__(self,*args,**kwargs):
		self.user = kwargs.pop('user',User)
		super (AddLetterForm, self).__init__(*args,**kwargs)
		
		new_fields = OrderedDict()
		
		self.fields['contact']=forms.TypedChoiceField(
			choices = get_contact_list(self.user),
			label = 'Mailed to:',
			initial = '----Select a contact----',
			)
				
	note = forms.CharField(
		max_length=500,
		widget=forms.Textarea,
		required=False
		)
		
	date_sent = forms.DateField(
		initial=datetime.date.today,
		)
				
class RegisterGiftForm(forms.Form):

	def __init__(self,*args,**kwargs):
		self.user = kwargs.pop('user',User)
		self.donor = kwargs.pop('donor',False)
		super (RegisterGiftForm, self).__init__(*args,**kwargs)

		self.fields['supporter'] = forms.TypedChoiceField(
			choices = get_contact_list(self.user),
			label = 'Donor'
			)
			
		if self.donor:
			self.fields['supporter'].widget = forms.HiddenInput()
			self.fields['supporter'].initial = self.donor.pk
				
	amount = forms.IntegerField(
		label = 'Gift amount'
		)
		
	frequency = forms.ChoiceField(
		choices = FREQ_OPTIONS,
		label = 'Giving schedule'
		)
		
	start_date = forms.DateField(
		required=True,
		label='Start date',
		widget=DateTimePicker(
			options={
			'format':'MM/DD/YY',
			'pickTime':False,
			},
		),
		)

	note = forms.CharField(
		max_length=500,
		widget=forms.Textarea,
		required=False
		)
	
class RegisterCallForm(forms.Form):

	def __init__(self,*args,**kwargs):
	
		self.user = kwargs.pop('user',User)
		super (RegisterCallForm, self).__init__(*args,**kwargs)
		
		self.fields['contact'] = forms.TypedChoiceField(
		choices = get_contact_list(self.user),
		label = 'Call with',
		widget = forms.widgets.Select(
		attrs={
		'class':'form-control',
		}),
		)
		
	answered = forms.TypedChoiceField(
	label='Answered:',
	coerce=lambda x: x == 'Yes',
	choices=((False, 'No'), (True, 'Yes')),
	widget=forms.widgets.RadioSelect(),
	required=True
	)
	answered.widget.attrs = {'class':'form-control'}
	
	left_message = forms.TypedChoiceField(
	label='Left a message:',
	coerce=lambda x: x == 'Yes',
	choices=((False, 'No'), (True, 'Yes')),
	widget=forms.widgets.RadioSelect(),
	)
	left_message.widget.attrs = {'class':'form-control'}
	
	time_called = forms.DateTimeField(
	label = 'Time of call',
	initial = datetime.datetime.now,
	required = False,
	widget=DateTimePicker(
	attrs={'class':"form-control"},
	options={
	"format":"YYYY-MM-DD HH:mm a",
	"pickSeconds":False
	},
	),
	)
	
	note = forms.CharField(
	max_length=500,
	widget=forms.Textarea,
	required=False,
	)
	
	voice_mail_note = forms.CharField(
	max_length=500,
	widget=forms.Textarea,
	required=False
	)
	
class RegisterMeetingForm(forms.Form):

	def __init__(self,*args,**kwargs):
		self.user = kwargs.pop('user',User)

		super (RegisterMeetingForm, self).__init__(*args,**kwargs)

		self.fields['contact'] = forms.TypedChoiceField(
		choices = get_contact_list(self.user),
		label = 'Meeting with:'
		)
				
	date = forms.DateField(
	input_formats=['%m/%d/%y'],
	initial = datetime.date.today,
	widget=DateTimePicker(
	attrs={'class':'form-control'},
	options={
	'format':'MM/DD/YY',
	'pickTime':False,
	},
	),
	)
	
	time = forms.TimeField(
	input_formats=['%I:%M %p'],
	widget=DateTimePicker(
	attrs={'class':'form-control'},
	options={
	'format':'HH:mm a',
	'pickDate':False,
	'pickSeconds':False,
	},
	),
	)
	
	location = forms.CharField(
	max_length=255,
	required=False
	)
	
	note = forms.CharField(
	max_length=500,
	widget=forms.Textarea,
	required=False
	)
	
class RegisterVoiceMailForm(forms.Form):

	def __init__(self,*args,**kwargs):
	
		self.user = kwargs.pop('user',User)

		super (RegisterVoiceMailForm, self).__init__(*args,**kwargs)

		self.fields['contact'] = forms.TypedChoiceField(
		choices = get_contact_list(self.user),
		label = 'Left for',
		)
				
	date = forms.DateTimeField(
	initial = datetime.date.today,
	)
	
	note = forms.CharField(
	max_length=500,
	widget=forms.Textarea,
	required=False
	)

	
	
 
	
	