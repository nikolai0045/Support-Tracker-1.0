from django.shortcuts import render, redirect, render_to_response, get_object_or_404
from django.db import models
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import UserProfile, Person, SupportRelationship, ContactRelationship, ThankYou, Letter, Call, Meeting, VoiceMail, Reminder, Note, Message, FollowUp, Referral
from .forms import AddContactForm, AddThankYouForm, AddLetterForm, RegisterGiftForm, RegisterCallForm, RegisterMeetingForm, RegisterVoiceMailForm, RecordMeetingModalForm, AddReminder, RecordCallModalForm, RecordFollowUpModalForm, UpdateReminderModalForm, RecordMessageModalForm, ScheduleMessageModalForm, ScheduleCallModalForm, ScheduleThankYouModalForm, RecordThankYouModalForm, ScheduleFollowUpModalForm, UpdateStageForm, LoginForm, AddReferralForm, ChangePasswordForm
import datetime
from functools import partial, wraps
from django.contrib.auth.views import login as login_view
from django.contrib.auth.views import logout as logout_view
from collections import OrderedDict
from django.views.generic import View
from django.forms.formsets import formset_factory
from django_datatables_view.base_datatable_view import BaseDatatableView
import json

def processStageUpdate(rel,data,user):
	rel.stage = data['new_stage']
	rel.save()
	
	contact = rel.contact
	
	if data['new_stage'] == 'MESSAGE':
		if data['date'] != None and data['date'] != '':
			new_message = Message(
			staff_person = user.userprofile,
			contact = contact,
			date_to_send = data['date'],
			method = data['method'],
			note = data['note'],
			sent = False,
			)
		else:
			new_message = Message(
			staff_person = user.userprofile,
			contact = contact,
			sent = False,
			)
			
		new_message.save()
	elif data['new_stage'] == 'CALL': 
		if data['date'] != None and data['date'] != '':
			new_call = Call(
			staff_person = user.userprofile,
			contact = contact,
			date = data['date'],
			time = data['time'],
			note = data['note'],
			completed = False,
			)
		else:
			new_call = Call(
			staff_person = user.userprofile,
			contact = contact,
			completed = False,
			)
			
		new_call.save()
	elif data['new_stage'] == 'MEET':
		if data['date'] != None and data['date'] != '':
			new_meeting = Meeting(
			staff_person = user.userprofile,
			contact = contact,
			date = data['date'],
			time = data['time'],
			location = data['location'],
			note = data['note'],
			completed = False,
			)
		else:
			new_meeting = Meeting(
			staff_person = user.userprofile,
			contact = contact,
			completed = False,
			)
			
		new_meeting.save()
	elif data['new_stage'] == 'THANK':
		if data['date'] != None and data['date'] != '':
			new_thank_you = ThankYou(
			staff_person = user.userprofile,
			contact = contact,
			date = data['date'],
			sent = False,
			note = data['note'],
			)
		else:
			new_thank_you = ThankYou(
			staff_person = user.userprofile,
			contact = contact,
			sent = False,
			)
			
		new_thank_you.save()
	elif data['new_stage'] == 'FOLLOW_UP':
		if data['date'] != None and data['date'] != '':
			new_follow_up = FollowUp(
			staff_person = user.userprofile,
			contact = contact,
			date = data['date'],
			time = data['time'],
			method = data['method'],
			note = data['note'],
			completed = False,
			)
		else:
			new_follow_up = FollowUp(
			staff_person = user.userprofile,
			contact = contact,
			completed = False,
			)
			
		new_follow_up.save()

def processActiveTabScript(activeTableName):

	response = "<script>$(document).ready(function() {$('#urgent').attr('class','tab-pane fade');$('#meetings').attr('class','tab-pane fade');$('#calls').attr('class','tab-pane fade');$('#thankYous').attr('class','tab-pane fade');$('#follow_ups').attr('class','tab-pane fade');$('#messages').attr('class','tab-pane fade');$('#reminders').attr('class','tab-pane fade');$('#" + activeTableName + "').addClass('in active'););</script>"
	return response
	
class HomeView(View):
	template = 'supporttracker/home.html'
	@method_decorator(login_required)
	def get(self,request):

		user = request.user
		
		all_meetings = Meeting.objects.filter(staff_person=user.userprofile)
		all_calls = Call.objects.filter(staff_person=user.userprofile)
		all_follow_ups = FollowUp.objects.filter(staff_person=user.userprofile)
		all_reminders = Reminder.objects.filter(staff_person=user.userprofile)
		all_messages = Message.objects.filter(staff_person=user.userprofile)
		all_thank_yous = ThankYou.objects.filter(staff_person=user.userprofile)
		
		urgent_meetings = all_meetings.filter(date__lte=datetime.date.today()).filter(completed=False)
		urgent_calls = all_calls.filter(date__lte=datetime.date.today()).filter(completed=False)
		urgent_follow_ups = all_follow_ups.filter(date__lte=datetime.date.today()).filter(completed=False)
		urgent_reminders = all_reminders.filter(remind_date__lte=datetime.date.today()).filter(completed=False)
		urgent_messages = all_messages.filter(date_to_send__lte=datetime.date.today()).filter(sent=False)
		urgent_thank_yous = all_thank_yous.filter(date__lte=datetime.date.today()).filter(sent=False)
		
		meetings = all_meetings.filter(date__gte=datetime.date.today()).filter(completed=False)
		calls = all_calls.filter(completed=False)
		follow_up_rels = all_follow_ups.filter(completed=False)
		reminders = all_reminders.filter(remind_date__gte=datetime.date.today()).filter(completed=False)
		messages = all_messages.filter(sent=False)
		thank_yous = all_thank_yous.filter(sent=False)

		# meetings = Meeting.objects.filter(staff_person=user.userprofile).filter(date__gte=datetime.date.today()).filter(completed=False)
		# calls = Call.objects.filter(staff_person=user.userprofile).filter(completed=False)
		# follow_up_rels = FollowUp.objects.filter(staff_person=user.userprofile).filter(completed=False)
		# reminders = Reminder.objects.filter(staff_person=user.userprofile).filter(remind_date__gte=datetime.date.today()).filter(completed=False)
		# messages = Message.objects.filter(staff_person=user.userprofile).filter(sent=False)
		# thank_yous = ThankYou.objects.filter(staff_person=user.userprofile).filter(sent=False)
			
		context = {
		'urgentClasses':'tab-pane fade in active',
		'meetingClasses':'tab-pane fade',
		'callClasses':'tab-pane fade',
		'followUpClasses':'tab-pane fade',
		'reminderClasses':'tab-pane fade',
		'messageClasses':'tab-pane fade',
		'thankYouClasses':'tab-pane fade',
		'meetings':meetings,
		'calls':calls,
		'follow_ups':follow_up_rels,
		'reminders':reminders,
		'messages':messages,
		'thank_yous':thank_yous,
		'urgent_meetings':urgent_meetings,
		'urgent_calls':urgent_calls,
		'urgent_follow_ups':urgent_follow_ups,
		'urgent_reminders':urgent_reminders,
		'urgent_messages':urgent_messages,
		'urgent_thank_yous':urgent_thank_yous,
		}

		return render(request,self.template,context)
		
class LoginView(View):
	template = 'registration/login.html'
	
	def get(self,request,*args,**kwargs):
		form = LoginForm()
		context = {
			'form':form
		}
		if request.user.is_authenticated():
			return redirect('/home/')
		else:
			return render(request,self.template,context)
	
	def post(self,request,*args,**kwargs):
		form = LoginForm(request.POST)
		context = {
			'form':form
		}
		if form.is_valid():
			user = form.login(request)
			if user:
				login(request, user)
				return redirect('/home/')
				
		return render(request,self.template,context)

class ContactListView(View):
	template = 'supporttracker/contact_list.html'
	@method_decorator(login_required)
	def get(self,request,**kwargs):
	
		contact_rels = request.user.userprofile.contactrelationship_set.all().order_by('contact__last_name','contact__first_name')
	
		context = {
			'rels':contact_rels
		}
		
		return render(request,self.template,context)

def get_support_numbers(userProfile):
	support_rels = userProfile.supportrelationship_set.all()
	total_monthly_support = 0
	total_annual_support = 0
	total_quarterly_support = 0
	total_semi_annual_support = 0
	total_one_time_support = 0
	for rel in support_rels:
		if rel.frequency == 'Monthly':
			total_monthly_support += rel.amount
		elif rel.frequency == 'Quarterly':
			total_quarterly_support += rel.amount
		elif rel.frequency == 'Annually':
			total_annual_support += rel.amount
		elif rel.frequency == 'Semi-annually':
			total_semi_annual_support += rel.amount
		elif rel.frequency == 'One-time':
			total_one_time_support += rel.amount
	
	total_on_monthly_basis = total_monthly_support + (total_quarterly_support/3 ) + (total_annual_support/12) + (total_semi_annual_support/6)
	total_on_yearly_basis = (total_monthly_support*12) + (total_quarterly_support*4) + (total_semi_annual_support*2) + (total_annual_support)

	pct_of_total = "%.2f" % round((float(total_on_yearly_basis)/float(userProfile.yearly_support_goal))*100,2)
	
	return {
		'pct':pct_of_total,
		'total_month':total_on_monthly_basis,
		'total_year':total_on_yearly_basis,
	}
	
class SupporterListView(View):
	template = 'supporttracker/supporter_list.html'
	@method_decorator(login_required)
	def get(self,request,**kwargs):
	
		support_rels = request.user.userprofile.supportrelationship_set.all().order_by('supporter__last_name','supporter__first_name')
		support_numbers = get_support_numbers(request.user.userprofile)
		
		context = {
			'rels':support_rels,
			'pct':support_numbers['pct'],
			'total_month':support_numbers['total_month'],
			'total_year':support_numbers['total_year'],
		}
		
		return render(request,self.template,context)
		
class DeleteSupporterView(View):
	template = 'supporttracker/supporter_list_table.html'
	
	@method_decorator(login_required)
	def get(self,request,**kwargs):
		rel_id = self.kwargs.pop('rel_id',False)
		rel = SupportRelationship.objects.get(pk=rel_id)
		rel.delete()
		
		support_rels = request.user.userprofile.supportrelationship_set.all().order_by('supporter__last_name','supporter__first_name')
		support_numbers = get_support_numbers(request.user.userprofile)
		
		context = {
			'rels':support_rels,
			'pct':support_numbers['pct'],
			'total_month':support_numbers['total_month'],
			'total_year':support_numbers['total_year'],
		}
				
		return render(request,self.template,context)

		
class ContactInfoModalView(View):
	template = 'supporttracker/contactInfoModal.html'
	@method_decorator(login_required)
	def get(self,request,**kwargs):
		contact_id = self.kwargs.pop('contact_id')
		contact = Person.objects.get(pk=contact_id)
		contact_rel = ContactRelationship.objects.get(staff_person=request.user.userprofile,contact=contact)
		
		context = {
			'contact':contact,
			'contact_rel':contact_rel,
		}
		return render(request,self.template,context)
		
class ContactProfileView(View):
	template = 'supporttracker/contactProfile.html'
	@method_decorator(login_required)
	def get(self,request,**kwargs):
		rel_id = self.kwargs.pop('contact_rel_id',None)
		rel = ContactRelationship.objects.get(pk=rel_id)
		
		meetings = Meeting.objects.filter(staff_person=request.user.userprofile,contact=rel.contact).filter(completed=True).order_by('date','time')
		calls = Call.objects.filter(staff_person=request.user.userprofile,contact=rel.contact).filter(completed=True).order_by('date','time')
		messages = Message.objects.filter(staff_person=request.user.userprofile,contact=rel.contact).filter(sent=True).order_by('date_to_send')
		follow_ups = FollowUp.objects.filter(staff_person=request.user.userprofile,contact=rel.contact).filter(completed=True).order_by('date','time')
		thank_yous = ThankYou.objects.filter(staff_person=request.user.userprofile,contact=rel.contact).filter(sent=True).order_by('date')
		reminders = Reminder.objects.filter(staff_person=request.user.userprofile,contact=rel.contact).filter(completed=True).order_by('remind_date')
		
		gifts = SupportRelationship.objects.filter(staff_person=request.user.userprofile,supporter=rel.contact)

		
		context = {
			'rel':rel,
			'meetings':meetings,
			'calls':calls,
			'messages':messages,
			'follow_ups':follow_ups,
			'thank_yous':thank_yous,
			'reminders':reminders,
			'gifts':gifts,
		}
		
		return render(request,self.template,context)
		
class UserSettingsView(View):
	template = 'supporttracker/user_settings.html'
	
	@method_decorator(login_required)
	def get(self,request,*args,**kwargs):
		form = ChangePasswordForm(user=request.user)
		context = {
			'form':form
		}
		return render(request,self.template,context)
		
	@method_decorator(login_required)
	def post(self,request,*args,**kwargs):
		form = ChangePasswordForm(request.user,request.POST)
		if form.is_valid():
			form.save()
			return redirect('/settings/')
		context = {
			'form':form
		}
		return render(request,self.template,context)

class ChangePasswordAJAX(View):
	template = 'supporttracker/change_password.html'
	
	@method_decorator(login_required)
	def post(self,request,*args,**kwargs):
		form = ChangePasswordForm(request.user,request.POST)
		if form.is_valid():
			form.save()
			update_session_auth_hash(request, form.user)
			return render(request,self.template)
		context = {
			'form':form,
			'fail':True,
		}
		return render(request,self.template,context)
class UserProfileView(View):
	template = 'supporttracker/user_profile.html'
	@method_decorator(login_required)
	def get(self,request,**kwargs):
		user = request.user
		userProfile = user.userprofile
		
		num_contacts = ContactRelationship.objects.filter(staff_person=userProfile).count()
		num_supporters = SupportRelationship.objects.filter(staff_person=userProfile).count()
		num_calls = Call.objects.filter(staff_person=userProfile).count()
		num_meetings = Meeting.objects.filter(staff_person=userProfile).count()
		num_thank_yous = ThankYou.objects.filter(staff_person=userProfile).count()
		num_voice_mails = VoiceMail.objects.filter(staff_person=userProfile).count()
		num_referrals = Referral.objects.filter(staff_person=userProfile).count()
		num_messages = Message.objects.filter(staff_person=userProfile).count()
		num_follow_ups = FollowUp.objects.filter(staff_person=userProfile).count()
		
		support_nums = get_support_numbers(userProfile)
		
		context = {
			'user':user,
			'userProfile':userProfile,
			'numContacts':num_contacts,
			'numSupporters':num_supporters,
			'numCalls':num_calls,
			'numMeetings':num_meetings,
			'numThankYous':num_thank_yous,
			'numVoiceMails':num_voice_mails,
			'numReferrals':num_referrals,
			'numMessages':num_messages,
			'numFollowUps':num_follow_ups,
			'pct':support_nums['pct'],
		}
		
		return render(request,self.template,context)

def contacts_list_view(request):

	contact_relationships = request.user.userprofile.contactrelationship_set.all().order_by('contact__last_name','contact__first_name')
	
	context = {
		'rels' : contact_relationships
	}
	
	return render(request,'supporttracker/contact_list.html',context)

		
def get_table_class_context(active):
	context = {
		'urgent':'tab-pane fade',
		'meetings':'tab-pane fade',
		'calls':'tab-pane fade',
		'followUps':'tab-pane fade',
		'reminders':'tab-pane fade',
		'messages':'tab-pane fade',
		'thankYous':'tab-pane fade',
	}
	
	context[active] = 'tab-pane fade in active'
	return context
	
def all_tables_update(request,classContext=False):

	if not classContext:
		urgentClasses = 'tab-pane fade in active'
		meetingClasses = 'tab-pane fade'
		callClasses = 'tab-pane fade'
		followUpClasses = 'tab-pane fade'
		reminderClases = 'tab-pane fade'
		messageClasses = 'tab-pane fade'
		thankYouClasses = 'tab-pane fade'
	else:
		urgentClasses = classContext['urgent']
		meetingClasses = classContext['meetings']
		callClasses = classContext['calls']
		followUpClasses = classContext['followUps']
		reminderClasses = classContext['reminders']
		messageClasses = classContext['messages']
		thankYouClasses = classContext['thankYous']
		
	template='supporttracker/tabTable.html'
	user = request.user

	all_meetings = Meeting.objects.filter(staff_person=user.userprofile)
	all_calls = Call.objects.filter(staff_person=user.userprofile)
	all_follow_ups = FollowUp.objects.filter(staff_person=user.userprofile)
	all_reminders = Reminder.objects.filter(staff_person=user.userprofile)
	all_messages = Message.objects.filter(staff_person=user.userprofile)
	all_thank_yous = ThankYou.objects.filter(staff_person=user.userprofile)
	
	urgent_meetings = all_meetings.filter(date__lte=datetime.date.today()).filter(completed=False)
	urgent_calls = all_calls.filter(date__lte=datetime.date.today()).filter(completed=False)
	urgent_follow_ups = all_follow_ups.filter(date__lte=datetime.date.today()).filter(completed=False)
	urgent_reminders = all_reminders.filter(remind_date__lte=datetime.date.today()).filter(completed=False)
	urgent_messages = all_messages.filter(date_to_send__lte=datetime.date.today()).filter(sent=False)
	urgent_thank_yous = all_thank_yous.filter(date__lte=datetime.date.today()).filter(sent=False)
	
	meetings = all_meetings.filter(date__gte=datetime.date.today()).filter(completed=False)
	calls = all_calls.filter(completed=False)
	follow_up_rels = all_follow_ups.filter(completed=False)
	reminders = all_reminders.filter(remind_date__gte=datetime.date.today()).filter(completed=False)
	messages = all_messages.filter(sent=False)
	thank_yous = all_thank_yous.filter(sent=False)
		
	context = {
	'urgentClasses':urgentClasses,
	'meetingClasses':meetingClasses,
	'callClasses':callClasses,
	'followUpClasses':followUpClasses,
	'reminderClasses':reminderClasses,
	'messageClasses':messageClasses,
	'thankYouClasses':thankYouClasses,
	'meetings':meetings,
	'calls':calls,
	'follow_ups':follow_up_rels,
	'reminders':reminders,
	'messages':messages,
	'thank_yous':thank_yous,
	'urgent_meetings':urgent_meetings,
	'urgent_calls':urgent_calls,
	'urgent_follow_ups':urgent_follow_ups,
	'urgent_reminders':urgent_reminders,
	'urgent_messages':urgent_messages,
	'urgent_thank_yous':urgent_thank_yous,
	}

	return render(request,template,context)
	
class RecordGiftView(View):
	template = 'supporttracker/register_gift.html'
	@method_decorator(login_required)
	def get_logic(self,request,**kwargs):
	
		donor_id = self.kwargs.pop('donor_id',False)
		
		if donor_id:
			donor = Person.objects.get(pk=donor_id)
			form = RegisterGiftForm(user=request.user,donor=donor)
		else:
			donor = False
			form = RegisterGiftForm(user=request.user)
			
		form.order_fields(['supporter','amount','frequency','start_date','note'])
		
		context = {
			'form':form,
			'donor':donor,
		}
		
		return context
		
	@method_decorator(login_required)	 
	def post_logic(self,request,**kwargs):
	
		donor_id = self.kwargs.pop('donor_id',False)
		
		if donor_id:
			donor = Person.objects.get(pk=donor_id)
			form = RegisterGiftForm(request.POST,user=request.user,donor=donor)
		else:
			donor = False
			form = RegisterGiftForm(request.POST,user=request.user)
			
		if form.is_valid():
			gift_data = form.cleaned_data
			
			donor_id = gift_data['supporter']
			donor = Person.objects.get(pk=donor_id)
			
			new_support_rel = SupportRelationship(
			staff_person=request.user.userprofile,
			supporter = donor,
			amount = gift_data['amount'],
			frequency = gift_data['frequency'],
			start_date = gift_data['start_date'],
			note = gift_data['note'],
			)
			
			new_support_rel.save()
			
			return ['redirect', donor]
		print form.errors
		
		context = {
			'form':form,
			'donor':donor,
		}
		
		return ['context',context]
	
	@method_decorator(login_required)
	def get(self,request,**kwargs):
		context = self.get_logic(request,**kwargs)
		return render(request,self.template,context)
		
	@method_decorator(login_required)
	def post(self,request,**kwargs):
		post_logic_return = self.post_logic(request,**kwargs)
		if post_logic_return[0] == 'redirect':
			
			if request.POST.get('submit') == 'another':
				return redirect('/record_gift/')
			
			donor = post_logic_return[1]
			rel = ContactRelationship.objects.get(staff_person=request.user.userprofile,contact=donor)
			return redirect('/' + str(rel.pk) + '/contact_profile/')
	
		if post_logic_return[0] == 'context':
			context = post_logic_return[1]
			return render(request,self.template,context)

class scheduleCallModalView(View):
	template = 'supporttracker/scheduleMessageModal.html'
	heading = "Schedule Call"
	
	def get_logic(self,request,**kwargs):
		
		form = ScheduleCallModalForm(user=request.user)
		
		form.order_fields(['contact','date','time','note'])
		
		context = {
			'form':form,
			'heading':self.heading
		}
		
		return context
		
	def post_logic(self,request,**kwargs):
		
		form = ScheduleCallModalForm(request.POST,user=request.user)
		
		if form.is_valid():
		
			call_data = form.cleaned_data
		
			contact_id = call_data['contact']
			contact = Person.objects.get(pk=contact_id)
			
			new_call = Call(
				staff_person = request.user.userprofile,
				contact = contact,
				answered = True,
				left_message = False,
				date = call_data['date'],
				time = call_data['time'],
				note = call_data['note'],
				completed = False,
			)
			
			new_call.save()
			
			return ['redirect',call_table_update(request)]
			
		context = {
			'form':form,
			'heading':self.heading
		}
		
		return ['context',context]
	
	@method_decorator(login_required)
	def get(self,request,**kwargs):
	
		context = self.get_logic(request,**kwargs)
		return render(request,self.template,context)
		
	@method_decorator(login_required)
	def post(self,request,**kwargs):
		
		post_logic_return = self.post_logic(request,**kwargs)
		if post_logic_return[0] == 'redirect':
			return post_logic_return[1]
		if post_logic_return[0] == 'context':
			context = post_logic_return[1]
			return render(request,self.template,context)
			
		return render(request,self.template,context)

class recordCallModalView(View):
	template = 'supporttracker/callFormModal.html'
	
	def get_logic(self,request,**kwargs):
	
		call_id = self.kwargs.pop('call_id',False)
		modifer = self.kwargs.pop('modifier',False)
		
		if call_id:
			
			call = Call.objects.get(pk=call_id)
			contact = call.contact
			contact_rel = ContactRelationship.objects.get(contact=contact,staff_person=request.user.userprofile)

			callForm = RecordCallModalForm(user=request.user,call_id=call_id,initial={'stage':contact_rel.stage})
			
			stageForm = UpdateStageForm(user=request.user,contact=contact)
			
			callForm.order_fields(['answered','left_message','date','time','stage','note','voice_mail_note','call_id'])
			
		else:
		
			callForm = RecordCallModalForm(user=request.user)
		
			callForm.order_fields(['contact','answered', 'left_message', 'date', 'time','stage','note','voice_mail_note'])
			
			stageForm = UpdateStageForm(user=request.user)
		
		context = {
			'form':callForm,
			'stageForm':stageForm
		}
				
		return context
		
	def post_logic(self,request,**kwargs):
		
		modifer = self.kwargs.pop('modifier',False)
		call_id = request.POST.get('call_id',False)
		
		if call_id:
		
			call_id = request.POST.get('call_id')
			call = Call.objects.get(pk=call_id)
			
			contact = call.contact
			contact_rel = ContactRelationship.objects.get(staff_person=request.user.userprofile,contact=contact)
			
			callForm = RecordCallModalForm(request.POST,user=request.user,call_id=call_id)
			
			stageForm = UpdateStageForm(request.POST,user=request.user,contact = contact)
			
		else:
		
			call = Call()
			contact_id = request.POST.get('contact')
			contact = Person.objects.get(pk=contact_id)
			contact_rel = ContactRelationship.objects.get(staff_person=request.user.userprofile,contact=contact)
			
			callForm = RecordCallModalForm(request.POST,user=request.user)
			
			stageForm = UpdateStageForm(user=request.user)
			
		
		if callForm.is_valid():
		
			call_data = callForm.cleaned_data

			call.staff_person = request.user.userprofile
			call.contact = contact
			call.answered = call_data['answered_hidden']
			call.left_message = call_data['left_message_hidden']
			call.date = call_data['date']
			call.time = call_data['time']
			call.completed = True

			call.save()
			
			if call_data['left_message_hidden']:
			
				new_voice_mail = VoiceMail(
				staff_person=request.user.userprofile,
				call = call,
				contact=contact,
				date_left=call_data['time_called'],
				note=call_data['voice_mail_note'],
				)
				
				new_voice_mail.save()
				
			if stageForm.is_valid():
				stage_data = stageForm.cleaned_data
				processStageUpdate(contact_rel,stage_data,request.user)
				
				if not modifier:
					classContext = get_table_class_context('calls')
					response = all_tables_update(request,classContext=classContext)
					return ['redirect',response]
				if modifier:
					classContext = get_table_class_context('urgent')
					response = all_tables_update(request,classContext=classContext)
					return ['redirect',response]
					
		context = {
			'form':callForm,
			'contact':contact,
			'stageForm':stageForm,
		}
		
		return ['context',context]
	
	@method_decorator(login_required)
	def post(self,request,**kwargs):
	
		post_logic_return = self.post_logic(request,**kwargs)
		if post_logic_return[0] == 'redirect':
			return post_logic_return[1]
		if post_logic_return[0] == 'context':
			context = post_logic_return[1]
			return render(request,self.template,context)
		
		return render(request,self.template,context)
		
	@method_decorator(login_required)
	def get(self,request,**kwargs):
	
		context = self.get_logic(request,**kwargs)
		return render(request,self.template,context)
		

class recordMeetingModalView(View):
	template = 'supporttracker/meetingFormModal.html'
	
	def get_logic(self,request,meeting_id=None,modifier=None,**kwargs):
		if meeting_id:
			meeting_id = self.kwargs['meeting_id']
		
		referralFormSet = formset_factory(AddReferralForm)
		referral_formset = referralFormSet()
		
		if meeting_id:
			meeting = Meeting.objects.get(pk=meeting_id)
			contact_id = meeting.contact.pk
			reminderFormSet = formset_factory(wraps(AddReminder)(partial(AddReminder,user=request.user,hide_contact=True,initial={'contact':contact_id})))
			contact_rel = ContactRelationship.objects.get(staff_person=request.user.userprofile,contact=meeting.contact)
			initial_stage = contact_rel.stage
			meetingForm = RecordMeetingModalForm(user=request.user,contact=contact_id,initial={'contact_id':contact_id,'stage':initial_stage,'meeting_id':meeting_id})
			meetingForm.order_fields(['meeting_id','contact_id','stage','note'])
			stageForm = UpdateStageForm(user=request.user,contact=meeting.contact)

		else:
			reminderFormSet = formset_factory(wraps(AddReminder)(partial(AddReminder,user=request.user,hide_contact=True)))
			meetingForm = RecordMeetingModalForm(user=request.user)
			meetingForm.order_fields(['meeting_id','contact_id','location','date','time','stage','note'])
			stageForm = UpdateStageForm(user=request.user)

		reminder_formset = reminderFormSet()

		context = {
			'form':meetingForm,
			'stageForm':stageForm,
			'referral_formset':referral_formset,
			'reminder_formset':reminder_formset,
		}
		
		return context
		
	def post_logic(self,request,**kwargs):
	
		modifier = self.kwargs.pop('modifier',False)
		contact_id = request.POST['contact_id']
		contact = get_object_or_404(Person.objects,pk=contact_id)
		
		meetingForm = RecordMeetingModalForm(request.POST,user=request.user,contact=contact_id)
		
		stageForm = UpdateStageForm(request.POST,user=request.user,contact=contact)
		
		referralFormSet = formset_factory(AddContactForm)
		referral_formset = referralFormSet(request.POST)
		
		reminderFormSet = formset_factory(wraps(AddReminder)(partial(AddReminder,user=request.user,hide_contact=True)))
		reminder_formset = reminderFormSet(request.POST)		
		
		contact_rel = ContactRelationship.objects.get(staff_person=request.user.userprofile,contact=contact)

		if meetingForm.is_valid():
			meeting_data = meetingForm.cleaned_data
			
			if meeting_data['meeting_id']:
			
				meeting_to_update = Meeting.objects.get(pk=meeting_data['meeting_id'])
				meeting_to_update.note=meeting_data['meeting_note']
				meeting_to_update.completed=True
				meeting_to_update.save()
				
			else:
				
				new_meeting = Meeting(
					staff_person=request.user.userprofile,
					contact=contact,
					date=meeting_data['date'],
					time=meeting_data['time'],
					location=meeting_data['location'],
					note=meeting_data['meeting_note'],
					completed=True,
				)
			
			if stageForm.is_valid():
				stage_data = stageForm.cleaned_data
				processStageUpdate(contact_rel,stage_data,request.user)
				
				if reminder_formset.is_valid():
					rem_data = reminder_formset.cleaned_data
					print rem_data
					for rem in rem_data:
						if rem.has_key('remind_date'):
							new_reminder = Reminder(
								staff_person=request.user.userprofile,
								contact=contact,
								remind_date=rem['remind_date'],
								date_added=datetime.date.today,
								note=rem['note']
							)
							new_reminder.save()
				
				if referral_formset.is_valid():
					ref_data = referral_formset.cleaned_data
					for ref in ref_data:
						if ref.has_key('first_name') and ref.has_key('last_name'):
							new_contact = Person(
								title=ref['title'],
								first_name=ref['first_name'],
								last_name=ref['last_name'],
								spouse_name=ref['spouse_name'],
								phone_number=ref['phone_number'],
								email_address=ref['email_address'],
								street_address=ref['street_address'],
								city=ref['city'],
								state=ref['state'],
								zip=ref['zip'],
							)
							new_contact.save()
							
							new_contact_rel = ContactRelationship(
								staff_person=request.user.userprofile,
								contact=new_contact,
								referred_by=contact_id,
								referral_note=ref['note'],
								date_added=datetime.date.today,
								stage=ref['stage']
							)
							new_contact_rel.save()
							
							new_referral = Referral(
								staff_person=request.user.userprofile,
								referring_contact=contact,
								referred_contact=new_contact,
								date_referred=meeting_to_update.date,
								note=ref['note']
							)
							new_referral.save()
							
							processStageUpdate(new_contact_rel,ref['stage_data'],request.user)
				
				if not modifier:
					classContext = get_table_class_context('meetings')
					response = all_tables_update(request,classContext=classContext)
					return ['redirect',response]
				if modifier:
					classContext = get_table_class_context('urgent')
					response = all_tables_update(request,classContext=classContext)
					return ['redirect',response]
		
		context = {
			'form':meetingForm,
			'stageForm':stageForm,
			'referral_formset':referral_formset,
			'reminder_formset':reminder_formset,
			'contact':contact
		}
		
		return ['context',context]
	
	@method_decorator(login_required)
	def get(self,request,**kwargs):
	
		context = self.get_logic(request,**kwargs)
		return render(request,self.template,context)
	
	@method_decorator(login_required)
	def post(self,request,**kwargs):
		contact_id = request.POST['contact_id']
		post_logic_return = self.post_logic(request,**kwargs)
		if post_logic_return[0] == 'redirect':
			return post_logic_return[1]
		if post_logic_return[0] == 'context':
			context = post_logic_return[1]
			return render(request,self.template,context)
		
		return render(request,self.template,context)

class scheduleFollowUpModalView(View):
	template="supporttracker/followUpModalForm.html"
	heading='Schedule a new follow up'
	
	def post_logic(self,request,**kwargs):
		user = request.user
		form = ScheduleFollowUpModalForm(request.POST,user=user)
		
		if form.is_valid():
			data = form.cleaned_data
			contact = Person.objects.get(pk=data['contact'])
			
			new_follow_up = FollowUp(
			staff_person=user.userprofile,
			contact = contact,
			date = data['date'],
			time = data['time'],
			method = data['method'],
			note = data['note'],
			completed = False,
			)
			
			new_follow_up.save()
			
			return ['redirect',follow_up_table_update(request)]
			
		context = {
			'form':form,
			'heading':self.heading,
		}
		
		return ['context',context]
		
	def get_logic(self,request,**kwargs):
	
		user = request.user
		form = ScheduleFollowUpModalForm(user=user)
		
		form.order_fields(['contact','method','date','time','note'])
		
		context = {
			'form':form,
			'heading':self.heading,
		}
		
		return context
		
	@method_decorator(login_required)
	def post(self,request,**kwargs):
	
		post_logic_return = self.post_logic(request,**kwargs)
		
		if post_logic_return[0] == 'redirect':
			return post_logic_return[1]
			
		if post_logic_return[0] == 'context':
			context = post_logic_return[1]
			return render(request,self.template,context)
	
	@method_decorator(login_required)
	def get(self,request,**kwargs):
	
		context = self.get_logic(request,**kwargs)
		return render(request,self.template,context)

class recordFollowUpModalView(View):
	template = "supporttracker/followUpModalForm.html"
	heading = "Record a Follow Up"
	
	def post_logic(self,request,**kwargs):
		modifier = self.kwargs.pop('modifier',False)
		fup_id = self.kwargs.pop('fup_id',False)
		name = ''
		
		if fup_id:
			print fup_id
			form = RecordFollowUpModalForm(request.POST,fup_id=fup_id,user=request.user)
			fup = FollowUp.objects.get(pk=fup_id)
			contact = fup.contact
			stageForm = UpdateStageForm(request.POST,user=request.user,contact=contact)
			if form.is_valid():
				data = form.cleaned_data
				fup = FollowUp.objects.get(pk=fup_id)
				contact = fup.contact
				contact_rel = ContactRelationship.objects.get(contact=contact,staff_person=request.user.userprofile)
				
				fup.completed=True
				if data['note'] != '' and data['note'] != None:
					fup.note = data['note']
				fup.save()
				
				if stageForm.is_valid():
					stage_data = stageForm.cleaned_data
					processStageUpdate(contact_rel,stage_data,request.user)
				
				
					name = " with "
					fup = FollowUp.objects.get(pk=fup_id)
					name += fup.contact.first_name
					if fup.contact.spouse_name != None and fup.contact.spouse_name != '':
						name += ' and '
						name += fup.contact.spouse_name
					name += ' '
					name += fup.contact.last_name
					if not modifier:
						classContext = get_table_class_context('followUps')
						response = all_tables_update(request,classContext=classContext)
						return ['redirect',response]
					if modifier:
						classContext = get_table_class_context('urgent')
						response = all_tables_update(request,classContext=classContext)
						return ['redirect',response]
			
		else:
			form = RecordFollowUpModalForm(request.POST,user=request.user)
			stageForm = UpdateStageForm(user=request.user)
			if form.is_valid():
				data = form.cleaned_data
				contact = Person.objects.get(pk=data['contact'])
				
				fup = FollowUp(
				staff_person=request.user.userprofile,
				contact = contact,
				date = data['date'],
				time = data['time'],
				method = data['method'],
				note = data['note'],
				completed=True,
				)
				
				fup.save()
				
				if stageForm.is_valid():
					contact_rel = ContactRelationship.get(staff_person=request.user.userprofile,contact=contact)
					stage_data = stageForm.cleaned_data
					processStageUpdate(contact_rel,stage_data,request.user)
					
					if not modifier:
						return ['redirect',all_tables_update(request)+processActiveTabScript('follow_ups')]
					if modifier:
						return ['redirect',all_tables_update(request)+processActiveTabScript('urgent')]
			
		context = {
			'form':form,
			'stageForm':stageForm,
			'heading':self.heading,
			'name':name,
		}
		
		return ['context',context]
				
	def get_logic(self,request,**kwargs):
	
		fup_id = self.kwargs.pop('fup_id',False)
		user = request.user
		name = ''
		
		if fup_id:
			fup = FollowUp.objects.get(pk=fup_id)
			contact = fup.contact
			stageForm = UpdateStageForm(user=request.user,contact=contact)
			form = RecordFollowUpModalForm(fup_id=fup_id,user=user)
			form.order_fields(['fup_id','contact','stage','date','time','method','note'])
			fup = FollowUp.objects.get(pk=fup_id)
			name += " with "
			name += fup.contact.first_name
			if fup.contact.spouse_name != None and fup.contact.spouse_name != '':
				name += ' and '
				name += fup.contact.spouse_name
			name += ' '
			name += fup.contact.last_name

		else:
			form = RecordFollowUpModalForm(user=user)
			stageForm = UpdateStageForm(user=user)
			form.order_fields(['contact','stage','date','time','method','note'])
		
		context = {
			'form':form,
			'stageForm':stageForm,
			'heading':self.heading,
			'name':name
		}
		
		return context
		
	@method_decorator(login_required)
	def post(self,request,**kwargs):
		contact_id = request.POST['contact']
		post_logic_return = self.post_logic(request,contact_id=contact_id,**kwargs)
		
		if post_logic_return[0] == 'redirect':
			return post_logic_return[1]
			
		if post_logic_return[0] == 'context':
			context = post_logic_return[1]
			return render(request,self.template,context)
	
	@method_decorator(login_required)
	def get(self,request,**kwargs):
		
		context = self.get_logic(request,**kwargs)
		return render(request,self.template,context)

class scheduleThankYouModalView(View):
	template='supporttracker/followUpModalForm.html'
	heading='Schedule a thank you note'
	
	def post_logic(self,request,**kwargs):
	
		user = self.kwargs.pop('user',User)
		form = ScheduleThankYouModalForm(request.POST, user=user)
		if form.is_valid():
			data = form.cleaned_data
			contact_id = data['contact']
			contact = Person.objects.get(pk=contact_id)
			
			new_ty = ThankYou(
			staff_person = user.userprofile,
			contact = contact,
			date = data['date'],
			sent = False,
			note = data['note']
			)
			
			new_ty.save()
			
			return ['redirect',thank_you_table_update(request)]
		
		context = {
			'form':form,
			'heading':self.heading,
		}
		
		return ['context',context]
			
	def get_logic(self,request,**kwargs):
	
		user = self.kwargs.pop('user',User)
		form = ScheduleThankYouModalForm(user=request.user)
		
		context = {
			'form':form,
			'heading':self.heading,
		}
		
		return context
		
	@method_decorator(login_required)
	def post(self,request,**kwargs):
		
		post_logic_return = self.post_logic(request,**kwargs)
		
		if post_logic_return[0] == 'redirect':
			return post_logic_return[1]
		if post_logic_return[0] == 'context':
			context = post_logic_return[1]
			return render(request,self.template,context)
		
	@method_decorator(login_required)
	def get(self,request,**kwargs):
		
		context = self.get_logic(request,**kwargs)
		return render(request,self.template,context)

class recordThankYouModalView(View):
	template='supporttracker/followUpModalForm.html'
	heading='Record Thank You Note'
	
	def post_logic(self,request,**kwargs):
		modifier = self.kwargs.pop('modifier',False)
		ty_id = self.kwargs.pop('ty_id',False)
		if ty_id:
			ty = ThankYou.objects.get(pk=ty_id)
			form = RecordThankYouModalForm(request.POST,user=request.user,ty_id=ty_id)
			stageForm = UpdateStageForm(request.POST,user=request.user,contact=ty.contact)
			print form.is_valid()
			if form.is_valid():
				print 'form is valid'
				data = form.cleaned_data
				ty.sent = True
				ty.note = data['note']
				ty.date = data['date']
				ty.save()
				
				contact = ty.contact
				
				contact_rel = ContactRelationship.objects.get(staff_person=request.user.userprofile,contact=contact)
				if stageForm.is_valid():
					stage_data = stageForm.cleaned_data
					processStageUpdate(contact_rel,stage_data,request.user)
				
					if not modifier:
						classContext = get_table_class_context('thankYous')
						response = all_tables_update(request,classContext=classContext)
						return ['redirect',response]
					if modifier:
						classContext = get_table_class_context('urgent')
						response = all_tables_update(request,classContext=classContext)
						return ['redirect',response]
			
		else:
			form = RecordThankYouModalForm(request.POST,user=request.user)
			stageForm = UpdateStageForm(request.POST,user=request.user)
			if form.is_valid():
				data = form.cleaned_data
				contact = data['contact']
				ty = ThankYou(
				note = data['note'],
				date = data['date'],
				contact = contact,
				staff_person = request.user.userprofile,
				sent = False,				
				)
				
				ty.save()
				
				if stageForm.is_valid():
					contact_rel = ContactRelationship.objects.get(staff_person=request.user,contact=contact)
					stage_data = stageForm.cleaned_data
					processStageUpdate(contact_rel,stage_data,request.user)
				
					return ['redirect',all_tables_update(request)+processActiveTabScript('thankYous')]
				
		context = {
			'form':form,
			'stageForm':stageForm,
			'heading':self.heading,
		}
		
		return ['context',context]
					
	def get_logic(self,request,**kwargs):
	
		ty_id = self.kwargs.pop('ty_id',False)
		if ty_id:
			form = RecordThankYouModalForm(user=request.user,ty_id=ty_id)
			form.order_fields(['date','note','stage','contact'])
			ty = ThankYou.objects.get(pk=ty_id)
			stageForm = UpdateStageForm(user=request.user,contact=ty.contact)
			
		else:
			form = RecordThankYouModalForm(user=request.user)
			stageForm = UpdateStageForm(user=request.user)
			
		context = {
			'form':form,
			'stageForm':stageForm,
			'heading':self.heading,
		}
		
		return context
		
	@method_decorator(login_required)
	def post(self,request,**kwargs):
	
		post_logic_return = self.post_logic(request,**kwargs)
		
		if post_logic_return[0] == 'redirect':
			return post_logic_return[1]
		if post_logic_return[0] == 'context':
			context = post_logic_return[1]
			return render(request,self.template,context)
		
	@method_decorator(login_required)
	def get(self,request,**kwargs):
	
		context = self.get_logic(request,**kwargs)
		return render(request,self.template,context)
		
		
class scheduleReminderModalView(View):
	template='supporttracker/scheduleReminderModal.html'
	
	def post_logic(self,request,**kwargs):
		
		form = AddReminder(request.POST,user=request.user)
		
		if form.is_valid():
			data = form.cleaned_data
			
			new_reminder = Reminder(
			staff_person=request.user.userprofile,
			contact = Person.objects.get(pk=data['contact']),
			remind_date = data['remind_date'],
			date_added = datetime.date.today(),
			note = data['note'],
			completed = False,
			)
			
			new_reminder.save()
			
			return ['redirect',reminder_table_update(request)]
			
		context = {
			'form': form
		}
		
		return ['context',context]
		
	def get_logic(self,request,**kwargs):
	
		user = request.user
		form = AddReminder(user=user)
		form.order_fields(['contact','note','remind_date'])
		
		context = {
			'form':form
		}
		
		return context
		
	@method_decorator(login_required)
	def post(self,request,**kwargs):
	
		post_logic_return = self.post_logic(request,**kwargs)
		
		if post_logic_return[0] == 'redirect':
			return post_logic_return[1]
			
		if post_logic_return[0] == 'context':
			context = post_logic_return[1]
			return render(request,self.template,context)
		
	@method_decorator(login_required)
	def get(self,request,**kwargs):
	
		context = self.get_logic(request,**kwargs)
		return render(request,self.template,context)

class updateReminderModalView(View):
	template='supporttracker/reminderUpdateModalForm.html'
	
	def post_logic(self,request,**kwargs):
		contact_id = request.POST['contact']
		reminder_id = request.POST['reminder_id']
		reminder = Reminder.objects.get(pk=reminder_id)
		contact = Person.objects.get(pk=contact_id)
		
		contact_rel = ContactRelationship.objects.get(staff_person=request.user.userprofile,contact=contact)
		
		form = UpdateReminderModalForm(request.POST,contact_id=contact_id,user=request.user)
		stageForm = UpdateStageForm(request.POST,user=request.user,contact=contact)
		
		if form.is_valid():
			data = form.cleaned_data
			
			if stageForm.is_valid():
				stageData = stageForm.cleaned_data
				processStageUpdate(contact_rel,stageData,request.user)
				
				reminder.completed = True
				reminder.save()

				if not modifier:
					classContext = get_table_class_context('reminders')
					response = all_tables_update(request,classContext=classContext)
					return ['redirect',response]
				if modifier:
					classContext = get_table_class_context('urgent')
					response = all_tables_update(request,classContext=classContext)
					return ['redirect',response]
			
		context = {
			'form':form,
			'stageForm':stageForm,
		}
		
		return ['context',context]
		
	def get_logic(self,request,**kwargs):
		reminder_id = self.kwargs['reminder_id']
		reminder = Reminder.objects.get(pk=reminder_id)
		contact_id = reminder.contact.pk
		contact = Person.objects.get(pk=contact_id)
		user = request.user
		form = UpdateReminderModalForm(reminder_id=reminder_id,contact_id=contact_id,user=user)
		stageForm = UpdateStageForm(user=request.user,contact=contact)
		
		context = {
			'form':form,
			'stageForm':stageForm,
		}
		
		return context
		
	@method_decorator(login_required)
	def post(self,request,**kwargs):
		contact_id = request.POST['contact']
		post_logic_return = self.post_logic(request,contact_id=contact_id,**kwargs)
		
		if post_logic_return[0] == 'redirect':
			return post_logic_return[1]
			
		if post_logic_return[0] == 'context':
			context = post_logic_return[1]
			return render(request,self.template,context)
		
	@method_decorator(login_required)
	def get(self,request,**kwargs):
		
		context = self.get_logic(request,**kwargs)
		return render(request,self.template,context)

class recordMessageModalView(View):
	template='supporttracker/recordMessageModal.html'
	
	def post_logic(self,request,**kwargs):
		modifier = self.kwargs.pop('modifier')
		contact_id = request.POST['contact']
		
		if 'message_id' in request.POST:
			message_id = request.POST['message_id']
			message = Message.objects.get(pk=message_id)
		else:
			message_id = False
			
		contact = Person.objects.get(pk=contact_id)
		
		contact_rel = ContactRelationship.objects.get(staff_person=request.user.userprofile,contact=contact)
		
		if message_id:
			form = RecordMessageModalForm(request.POST,contact_id=contact_id,user=request.user)
			stageForm = UpdateStageForm(request.POST,user=request.user,contact=contact)
		else:
			form = RecordMessageModalForm(request.POST,user=request.user)
			stageForm = UpdateStageForm(request.POST,user=request.user)
		
		if form.is_valid():
			data = form.cleaned_data
			
			if message_id:
			
				message.sent = True
				message.save()
				
			else:
			
				new_message = Message(
				staff_person = request.user.userprofile,
				contact = contact,
				date_to_send = data['date_to_send'],
				date_entered = datetime.date.today(),
				method = data['method'],
				note = data['note'],
				sent = True,
				)
				
				new_message.save()
				
			if stageForm.is_valid():
				stage_data = stageForm.cleaned_data
				processStageUpdate(contact_rel,stage_data,request.user)
			
				if not modifier:
					classContext = get_table_class_context('messages')
					response = all_tables_update(request,classContext=classContext)
					return ['redirect',response]
				if modifier:
					classContext = get_table_class_context('urgent')
					response = all_tables_update(request,classContext=classContext)
					return ['redirect',response]
			
		context = {
			'form':form,
			'stageForm':stageForm,
		}
		
		return ['context',context]
		
	def get_logic(self,request,**kwargs):
		
		message_id = self.kwargs.pop('message_id',False)
		user = request.user
		
		if message_id:
		
			message = Message.objects.get(pk=message_id)
			contact_id = message.contact.pk
			form = RecordMessageModalForm(message_id=message_id,contact_id=contact_id,user=user)
			stageForm = UpdateStageForm(user=user,contact=message.contact)
			
		else:
		
			form = RecordMessageModalForm(user=user)
			stageForm = UpdateStageForm(user=user)
		
		context = {
			'form':form,
			'stageForm':stageForm,
		}
		
		return context
		
	@method_decorator(login_required)
	def post(self,request,**kwargs):
		post_logic_return = self.post_logic(request,**kwargs)
		
		if post_logic_return[0] == 'redirect':
			return post_logic_return[1]
			
		if post_logic_return[0] == 'context':
			context = post_logic_return[1]
			return render(request,self.template,context)
		
	@method_decorator(login_required)
	def get(self,request,**kwargs):
		
		context = self.get_logic(request,**kwargs)
		return render(request,self.template,context)

class scheduleMessageModalView(View):
	template = 'supporttracker/scheduleMessageModal.html'
	heading = "Schedule a Message"
	
	def get_logic(self,request,**kwargs):
		user = request.user
		
		form = ScheduleMessageModalForm(user=user)
		
		form.order_fields(['contact','method','date_to_send','note'])
		
		context = {
			'form':form,
			'heading':self.heading,
		}
		
		return context
		
	def post_logic(self,request,**kwargs):
	
		form = ScheduleMessageModalForm(request.POST,user=request.user)
		
		if form.is_valid():
			data = form.cleaned_data
			
			contact_id = data['contact']
			contact = Person.objects.get(pk=contact_id)
			
			new_message = Message(
			staff_person = request.user.userprofile,
			contact = contact,
			date_to_send = data['date_to_send'],
			date_entered = datetime.date.today(),
			method = data['method'],
			note = data['note'],
			sent = False,
			)
			
			new_message.save()
			
			return ['redirect',message_table_update(request)]
			
		context = {
			'form':form,
			'heading':self.heading,
		}
		
		return ['context',context]

		
	@method_decorator(login_required)
	def get(self,request,**kwargs):
		context=self.get_logic(request,**kwargs)
		return render(request,self.template,context)
		
	@method_decorator(login_required)
	def post(self,request,**kwargs):
		post_logic_return = self.post_logic(request,**kwargs)
		
		if post_logic_return[0] == 'redirect':
			return post_logic_return[1]
			
		if post_logic_return[0] == 'context':
			context = post_logic_return[1]
			return render(request,self.template,context)

class scheduleMeetingModalView(View):
	template='supporttracker/scheduleMeetingModal.html'
	
	def post_logic(self,request,**kwargs):
				
		form = RegisterMeetingForm(request.POST,user=request.user)
		user = request.user
		
		if form.is_valid():
			data = form.cleaned_data
			
			contact = Person.objects.get(pk=data['contact'])
			new_meeting = Meeting(
				staff_person=user.userprofile,
				contact=contact,
				date=data['date'],
				time=data['time'],
				location=data['location'],
				note=data['note'],
				completed=False,
			)
			
			new_meeting.save()
			
			print new_meeting
			print "####Meeting saved####"
			
			return ['redirect',meeting_table_update(request)]
			
		context = {
			'form':form
		}
		
		return ['context',context]
		
	def get_logic(self,request,**kwargs):
		user = request.user
		form = RegisterMeetingForm(user=user)
		
		form.order_fields(['contact','location','date','time','note'])
		context = {
			'form':form
		}
		
		return context
		
	@method_decorator(login_required)
	def post(self,request,**kwargs):
		post_logic_return = self.post_logic(request,**kwargs)
		
		if post_logic_return[0] == 'redirect':
			return post_logic_return[1]
			
		if post_logic_return[0] == 'context':
			context = post_logic_return[1]
			return render(request,self.template,context)
		
	@method_decorator(login_required)
	def get(self,request,**kwargs):
		
		context = self.get_logic(request,**kwargs)
		return render(request,self.template,context)

def meeting_table_update(request):

	template='supporttracker/meeting_table.html'
	user = request.user
	meetings = Meeting.objects.filter(staff_person=user.userprofile).filter(date__gte=datetime.date.today()).filter(completed=False)
	context = {'meetings':meetings}
	return render(request,template,context)
	
def call_table_update(request):

	template='supporttracker/call_table.html'
	user = request.user
	calls = Call.objects.filter(staff_person=user.userprofile).filter(completed=False)
	context = {'calls':calls}
	return render(request,template,context)
	
def follow_up_table_update(request):

	template='supporttracker/follow_up_table.html'
	user = request.user
	follow_ups = FollowUp.objects.filter(staff_person=user.userprofile).filter(completed=False)
	context = {'follow_ups':follow_ups}
	return render(request,template,context)
		
def reminder_table_update(request):

	template='supporttracker/reminder_table.html'
	user = request.user
	reminders = Reminder.objects.filter(staff_person=user.userprofile).filter(remind_date__gte=datetime.date.today()).filter(completed=False)
	context = {'reminders':reminders}
	return render(request,template,context)

def message_table_update(request):
	
	template = 'supporttracker/message_table.html'
	user = request.user
	messages = Message.objects.filter(staff_person=user.userprofile).filter(sent=False)
	context = {'messages':messages}
	return render(request,template,context)
	
def thank_you_table_update(request):

	template = 'supporttracker/thank_you_table.html'
	user = request.user
	thank_yous = ThankYou.objects.filter(staff_person=user.userprofile).filter(sent=False)
	context = {'thank_yous':thank_yous}
	return render(request,template,context)


def home(request):

	user = request.user
	
	meetings = Meeting.objects.filter(staff_person=user.userprofile).filter(date__gte=datetime.date.today())
	call_rels = ContactRelationship.objects.filter(staff_person=user.userprofile).filter(stage='CALL')
	follow_up_rels = ContactRelationship.objects.filter(staff_person=user.userprofile).filter(stage='FOLLOW_UP')
		
	context = {'meetings':meetings,'calls':call_rels,'follow_ups':follow_up_rels}

	return render(request,'supporttracker/home.html',context)
	
def user_profile_view(request):
	user = request.user
	
	user_first_name = user.first_name
	user_last_name = user.last_name
	user_username = user.username
	user_spouse_name = user.userprofile.spouse_name
	user_email = user.email
	user_address = user.userprofile.street_address
	user_city = user.userprofile.city
	user_state = user.userprofile.state
	user_zip = user.userprofile.zip
	
	context = {
	'f_name':user_first_name,
	'l_name':user_last_name,
	's_name':user_spouse_name,
	'email':user_email,
	'address':user_address,
	'city':user_city,
	'state':user_state,
	'zip':user_zip,	
	}
	
	return render(request,'supporttracker/user_profile.html',context)
	
def supporters_list_view(request):
	user = request.user
	
	support_relationships = user.userprofile.supportrelationship_set.all()
	
	context = {
		'rels' : support_relationships
	}
	
	return render(request,'supporttracker/supporter_list.html',context)
	
class ContactsListView(BaseDatatableView):
	contact = ContactRelationship
	
	columns = ['last_name','first_name','phone_number','address','stage']

	max_display_length = 100
	
	@method_decorator(login_required)
	def render_column(self,row,column):
	
		if column == 'last_name':
			return '{0}'.format(row.contact__last_name)
		else:
			return super(ContactsListView,self).render_column(row,column)
			
		if column == 'first_name':
			pass
			
	
def supporter_profile_view(request,supporter_id):
	user = request.user
	
	try:
		supporter = Person.objects.get(pk=supporter_id)
	except Exception:
		supporter = None
		
	try:
		relationship = SupportRelationship.objects.get(supporter=supporter, staff_person=user.userprofile)
	except Exception:
		relationship = None
	
	context = {
	'rel':relationship
	}
	
	return render(request,'supporttracker/supporter_profile.html',context)
			
def new_contact(request):

	if not request.user.is_authenticated():
	
		return redirect(login_view)

	if request.method == "POST":
	
		form = AddContactForm(request.POST, stage_form=True)
		stageForm = UpdateStageForm(request.POST,user=request.user)
		
		if form.is_valid():
		
			title = form.cleaned_data['title']
			first_name = form.cleaned_data['first_name']
			last_name = form.cleaned_data['last_name']
			spouse_name = form.cleaned_data['spouse_name']
			phone_number = form.cleaned_data['phone_number']
			email_address = form.cleaned_data['email_address']
			street_address = form.cleaned_data['street_address']
			city = form.cleaned_data['city']
			state = form.cleaned_data['state']
			zip = form.cleaned_data['zip']
						
			new_person = Person(
				title=title,
				first_name=first_name,
				last_name=last_name,
				spouse_name=spouse_name,
				phone_number=phone_number,
				email_address=email_address,
				street_address=street_address,
				city=city,
				state=state,
				zip=zip,
				)
							
			new_person.save()
		
			staff_person = request.user.userprofile
			contact = new_person
			date_added = datetime.date.today()
			
			if stageForm.is_valid():
				stage = stageForm.cleaned_data['new_stage']
			else:
				return render(request,'supporttracker/add_contact.html',{'form':form,'stageForm':stageForm})
			
			new_rel = ContactRelationship(
				staff_person=staff_person,
				contact=contact,
				date_added=date_added,
				stage=stage,
				)
			
			new_rel.save()
			
			if stageForm.is_valid():
			
				processStageUpdate(new_rel,stageForm.cleaned_data,request.user)
	
			if request.POST.get('submit') == 'continue':
			
				return redirect('/profile')
				
			else:
				return redirect(new_contact)
		
	else:
		contactFormSet = formset_factory(AddContactForm)
		
		form = AddContactForm(stage_form=True)
		stageForm = UpdateStageForm(user=request.user)
	
	return render(request, 'supporttracker/add_contact.html', {'form':form,'stageForm':stageForm})
		
def new_thank_you(request):

	if not request.user.is_authenticated():
		return redirect(login_view)

	if request.method == "POST":
		
		form = AddThankYouForm(request.POST,user=request.user)
	
		if form.is_valid():
			contact_pk = form.cleaned_data['contact']
			contact = Person.objects.get(pk=contact_pk)
			date_sent = form.cleaned_data['date_sent']
			note = form.cleaned_data['note']
			staff_person = request.user.userprofile
					
			thank_you = ThankYou(
				staff_person = staff_person,
				contact = contact,
				date_sent = date_sent,
				note = note,
				)
				
			thank_you.save()
		
			if request.POST.get('submit') == 'continue':
				return redirect(user_profile_view)
			else:
				return redirect(new_thank_you)
		
	else:
		form = AddThankYouForm(user=request.user)
	
	form.order_fields(['contact','date_sent','note'])
	return render(request, 'supporttracker/add_thank_you.html', {'form':form})

def new_letter(request):

	if not request.user.is_authenticated():
		return redirect(login_view)

	if request.method == "POST":

		form = AddLetterForm(request.POST,user=request.user)
		
		if form.is_valid():
		
			contact_pk = form.cleaned_data['contact']
			contact = Person.objects.get(pk=contact_pk)
			date_mailed = form.cleaned_data['date_sent']
			note = form.cleaned_data['note']
			staff_person = request.user.userprofile
			
			letter = Letter(
				staff_person = staff_person,
				contact = contact,
				date_mailed = date_mailed,
				note = note,
				)
				
			letter.save()
			
			if request.POST.get('submit') == 'continue':
				return redirect(user_profile_view)
			else:
				return redirect(new_letter)

		
	else:
		form = AddLetterForm(user=request.user)
	
	form.order_fields(['contact','date_sent','note'])
	return render(request, 'supporttracker/add_letter.html',{'form':form})
		
def new_gift(request):

	if not request.user.is_authenticated():
		return redirect(login_view)

	if request.method == "POST":
	
		form = RegisterGiftForm(request.POST,user=request.user)
		
		if form.is_valid():
		
			supporter_pk = forms.cleaned_data['supporter']
			supporter = Person.objects.get(pk=supporter_pk)
			amount = forms.cleaned_data['amount']
			frequency = forms.cleaned_data['frequency']
			start_date = forms.cleaned_data['start_date']
			date_entered = datetime.date.today()
			
			staff_person = request.user.userprofile
			
			gift = SupportRelationship(
				staff_person=staff_person,
				supporter=supporter,
				amount=amount,
				frequency=frequency,
				start_date=start_date,
				date_entered=date_entered
				)
				
			gift.save()
			
			if request.POST.get('submit') == 'continue':
				return redirect(user_profile_view)
			else:
				return redirect(new_gift)

		
	else:
		form = RegisterGiftForm(user=request.user)
	
	form.order_fields(['supporter','amount','frequency','start_date','note'])
	return render(request, 'supporttracker/register_gift.html', {'form':form})
		
def new_call(request):

	if not request.user.is_authenticated():
		return redirect(login_view)
		
	if request.method == "POST":	
				
		form = RegisterCallForm(request.POST,user=request.user)
		form.order_fields(['contact', 'answered', 'left_message', 'time_called','note'])

			
		if form.is_valid():
		
			answered = form.cleaned_data['answered']
			left_message = form.cleaned_data['left_message']
			contact_pk = form.cleaned_data['contact']
			time_called = form.cleaned_data['time_called']
			note = form.cleaned_data['note']
			
			contact = Person.objects.get(pk=contact_pk)
			staff_person = request.user.userprofile
			
			call = Call(
				staff_person=staff_person,
				contact=contact,
				answered=answered,
				left_message=left_message,
				time=time_called,
				note=note,
				)
			
			call.save()
					
			if request.POST.get('submit') == 'continue':
				return redirect(user_profile_view)
			else:
				return redirect(new_call)
		
	else:
			
		form = RegisterCallForm(user=request.user,)
		
	form.order_fields(['contact', 'answered', 'left_message', 'time_called','note'])
	
	return render(request, 'supporttracker/register_call.html',{'form':form})
			
def new_meeting(request):

	if not request.user.is_authenticated():
		return redirect(login_view)

	if request.method == "POST":
	
		form = RegisterMeetingForm(request.POST,user=request.user)
		
		if form.is_valid():
		
			staff_person = request.user.userprofile
			contact_pk = form.cleaned_data['contact']
			contact = Person.objects.get(pk=contact_pk)
			date = form.cleaned_data['date']
			time = form.cleaned_data['time']
			location = form.cleaned_data['location']
			note = form.cleaned_data['note']
			
			meeting = Meeting(
				staff_person=staff_person,
				contact=contact,
				date=date,
				time=time,
				location=location,
				note=note,
				)
				
			meeting.save()
		
			if request.POST.get('submit') == 'continue':
				return redirect(user_profile_view)
			else:
				return redirect(new_meeting)
		
	else:
	
		form = RegisterMeetingForm(user=request.user)
	
	form.order_fields(['contact','date','time','location','note'])
	return render(request, 'supporttracker/add_meeting.html',{'form':form})
		
def new_voice_mail(request):

	if not request.user.is_authenticated():
		return redirect(login_view)

	if request.method == "POST":
	
		form = RegisterVoiceMailForm(request.POST,user=request.user)
		
		if form.is_valid():
	
			staff_person = request.user.userprofile
			contact_pk = form.cleaned_data['contact']
			contact = Person.objects.get(pk=contact_pk)
			date = form.cleaned_data['date']
			note = form.cleaned_data['note']
					
			voice_mail = VoiceMail(
				staff_person=staff_person,
				contact=contact,
				date_left=date,
				note=note
				)
				
			voice_mail.save()
			
			if request.POST.get('submit') == 'continue':
				return redirect(user_profile_view)
			else:
				return redirect(new_voice_mail)
		
	else:
		form = RegisterVoiceMailForm(user=request.user)

	form.order_fields(['contact','date','note'])	
	return render(request, 'supporttracker/new_voice_mail.html',{'form':form})
		
def edit_contact(request,contact_id):

	if request.method == "POST":
	
		form = AddContactForm(request.POST)
		
		if form.is_valid():
			contact = Person.objects.get(pk=contact_id)
			rel = ContactRelationship.objects.get(staff_person=request.user.userprofile,contact=contact)
			
			contact.title = form.cleaned_data['title']
			contact.first_name = form.cleaned_data['first_name']
			contact.last_name = form.cleaned_data['last_name']
			contact.spouse_name = form.cleaned_data['spouse_name']
			contact.phone_number = form.cleaned_data['phone_number']
			contact.email_address = form.cleaned_data['email_address']
			contact.street_address = form.cleaned_data['street_address']
			contact.city = form.cleaned_data['city']
			contact.state = form.cleaned_data['state']
			contact.zip = form.cleaned_data['zip']
			
			contact.save()
			
			rel.stage = form.cleaned_data['stage']
			rel.save()
			
			
			
			if request.POST.get('submit') == 'continue':
			
				return redirect(contacts_list_view)
				
			else:
				return redirect(new_contact)
					
	else:
	
		contact = Person.objects.get(pk=contact_id)
		rel = ContactRelationship.objects.get(staff_person=request.user.userprofile,contact=contact)
		
		title = contact.title
		first_name = contact.first_name
		last_name = contact.last_name
		spouse_name = contact.spouse_name
		phone_number = contact.phone_number
		email_address = contact.email_address
		street_address = contact.street_address
		city = contact.city
		state = contact.state
		zip = contact.zip
		stage = rel.stage
		
		form = AddContactForm(initial={
		'title':title,
		'first_name':first_name,
		'last_name':last_name,
		'spouse_name':spouse_name,
		'phone_number':phone_number,
		'email_address':email_address,
		'street_address':street_address,
		'city':city,
		'stage':stage,
		'state':state,
		'zip':zip,
		})
	
	return render(request, 'supporttracker/add_contact.html',{'form':form})
		
def edit_thank_you(request,thank_you_id):

	if not request.user.is_authenticated():
		return redirect(login_view)
		
	thank_you = ThankYou.objects.get(pk=thank_you_id)

	if request.method == "POST":
	
		form = AddThankYouForm(request.POST,user=request.user)
		
		if form.is_valid():
				
			contact_pk = form.cleaned_data['contact']
			thank_you.contact = Person.objects.get(pk=contact_pk)
			thank_you.date_sent = form.cleaned_data['date_sent']
			thank_you.note = form.cleaned_data['note']
			thank_you.staff_person = request.user.userprofile
			
			thank_you.save()
			
			if request.POST.get('submit') == 'continue':
				return redirect(user_profile_view)
			else:
				return redirect(edit_thank_you)
	
	else:
		form = AddThankYouForm(intial={
		'contact':thank_you.contact.pk,
		'date_sent':thank_you.date_sent,
		'note':thank_you.note,
		},
		user=request.user,
		)
		
	form.order_fields(['contact','date_sent','note'])
	return render(request, 'supporttracker/add_thank_you.html',{'form':form})
		
def edit_letter(request,letter_id):
	
	if not request.user.is_authenticated():
		return redirect(login_view)
		
	letter = Letter.objects.get(pk=letter_id)
		
	if request.method == "POST":

		form = AddLetterForm(request.POST,user=request.user)
		
		if form.is_valid():
			
			letter = Letter.objects.get(pk=letter_id)
			
			contact_pk = form.cleaned_data['contact']
			letter.contact = Person.objects.get(pk=contact_pk)
			letter.date_mailed = form.cleaned_data['date_sent']
			letter.note = form.cleaned_date['note']
			letter.staff_person = request.user.userprofile
			
			letter.save()
			
			if request.POST.get('submit') == 'continue':
				return redirect(user_profile_view)
			else:
				return redirect(edit_letter)
				
	else:
		
		form = AddLetterForm(user=request.user)
		form.order_fields(['contact','date_sent','note'])
		form.initial = {
			'contact':letter.contact.pk,
			'note':letter.note,
			'date_sent':letter.date_mailed,	
		}
	
	form.order_fields(['contact','date_sent','note'])
	return render(request, 'supporttracker/add_letter.html',{'form':form})
		
def edit_gift(request,gift_id):

	if not request.user.is_authenticated():
		return redirect(login_view)
		
	rel = SupportRelationship.objects.get(pk=gift_id)

	if request.method == "POST":
		
		form = RegisterGiftForm(request.POST,user=request.user)
		
		if form.is_valid():
			
			supporter_pk = form.cleaned_data['supporter']
			rel.supporter = Person.objects.get(pk=supporter_pk)
			rel.amount = form.cleaned_data['amount']
			rel.frequency = form.cleaned_data['frequency']
			rel.start_date = form.cleaned_data['start_date']
			rel.note = form.cleaned_data['note']
			rel.date_updated = datetime.date.today
			rel.staff_person = request.user.userprofile
			
			rel.save()
			
			if request.POST.get('submit') == 'continue':
				return redirect(supporters_list_view)
			else:
				return redirect(edit_gift)
				
			
	else:
	
		form = RegisterGiftForm(
		initial={
			'supporter':rel.supporter.pk,
			'amount':rel.amount,
			'frequency':rel.frequency,
			'start_date':rel.start_date,
			'note':rel.note,
			},
		user=request.user
		)
		
	form.order_fields(['supporter','amount','frequency','start_date','note'])
	return render(request, 'supporttracker/register_gift.html',{'form':form})
		
def edit_call(request,call_id):

	if not request.user.is_authenticated():
		return redirect(login_view)
	
	if request.method == "POST":
	
		form = RegisterCallForm(request.POST,user=request.user)
		form.order_fields(['contact', 'answered', 'left_message', 'time_called','note'])

		if form.is_valid():
			call = Call.objects.get(pk=call_id)
			
			call.answered = form.cleaned_data['answered']
			call.left_message = form.cleaned_data['left_message']
			contact_pk = form.cleaned_data['contact']
			call.time_called = form.cleaned_data['time_called']
			call.note = form.cleaned_data['note']
			
			call.contact = Person.objects.get(pk=contact_pk)
			staff_person = request.user.userprofile
			
			call.save()
					
			if request.POST.get('submit') == 'continue':
				return redirect(user_profile_view)
			else:
				return redirect(new_call)
		
	else:
	
		call = Call.objects.get(pk=call_id)
		contact = call.contact
		answered = call.answered
		left_message = call.left_message
		time_called = call.time
		note = call.note
		
		form = RegisterCallForm(initial={
		'contact':contact.pk,
		'answered':answered,
		'left_message':left_message,
		'time_called':time_called,
		'note':note,
		},user=request.user)

		form.order_fields(['contact', 'answered', 'left_message', 'time_called','note'])
		
	return render(request, 'supporttracker/register_call.html',{'form':form})
		
def edit_meeting(request,meeting_id):

	if not request.user.is_authenticated():
		return redirect(login_view)
		
	meeting = Meeting.objects.get(pk=meeting_id)

	if request.method == "POST":
		
		form = RegisterMeetingForm(request.POST,user=request.user)
		
		if form.is_valid():
			
			contact_pk = form.cleaned_data['contact']
			meeting.contact = Person.objects.get(pk=contact_pk)
			meeting.date = form.cleaned_data['date']
			meeting.time = form.cleaned_data['time']
			meeting.location = form.cleaned_data['location']
			meeting.note = form.cleaned_data['note']
			meeting.staff_person = request.user.userprofile
			
			meeting.save()
			
			if request.POST.get('submit') == 'continue':
				return redirect(user_profile_view)
			else:
				return redirect(edit_meeting)
				
			
	else:
	
		form = RegisterMeetingForm(
		initial={
			'contact':meeting.contact.pk,
			'date':meeting.date,
			'time':meeting.time,
			'location':meeting.location,
			'note':meeting.note,
			},
		user=request.user
		)
		
	form.order_fields(['contact','date','time','location','note'])
	return render(request, 'supporttracker/add_meeting.html',{'form':form})
		
def edit_voice_mail(request,voice_mail_id):

	if not request.user.is_authenticated():
		return redirect(login_view)
		
	voice_mail = VoiceMail.objects.get(pk=voice_mail_id)

	if request.method == "POST":
		
		form = RegisterVoiceMailForm(request.POST,user=request.user)
		
		if form.is_valid():
			
			contact_pk = form.cleaned_data['contact']
			voice_mail.contact = Person.objects.get(pk=contact)
			voice_mail.date = form.cleaned_data['date']
			voice_mail.note = form.cleaned_data['note']
			voice_mail.staff_person = request.user.userprofile
			
			voice_mail.save()
			
			if request.POST.get('submit') == 'continue':
				return redirect(user_profile_view)
			else:
				return redirect(edit_voice_mail)
				
			
	else:
	
		form = RegisterVoiceMailForm(
		initial={
			'contact':rel.contact.pk,
			'date':rel.date,
			'note':rel.note,
			},
		user=request.user
		)
		
	form.order_fields(['contact','date','note'])
	return render(request, 'supporttracker/new_voice_mail.html',{'form':form})
