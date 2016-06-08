"""tracker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import patterns, url
from django.contrib import admin
import supporttracker.views as views
#from supporttracker.views import user_profile_view, supporters_list_view, supporter_profile_view, new_person, new_contact, new_thank_you, new_letter, new_gift, new_call, new_meeting, new_voice_mail
from django.contrib.auth.views import login as login_view
from django.contrib.auth.views import logout as logout_view

urlpatterns = [
	url(r'^$', views.HomeView.as_view()),
    url(r'^admin/', admin.site.urls),
	url(r'^home/', views.HomeView.as_view()),
	url(r'^login/$', views.LoginView.as_view()),
	url(r'^logout/$', logout_view),
	url(r'^profile/$', views.UserProfileView.as_view()),
	url(r'^settings/$', views.UserSettingsView.as_view()),
	url(r'^change_password/$',views.ChangePasswordAJAX.as_view()),
	url(r'^supporters/$', views.supporters_list_view),
	url(r'(?P<rel_id>[0-9]+)/delete_gift', views.DeleteSupporterView.as_view()),
	url(r'^(?P<supporter_id>[0-9]+)/support_profile/$', views.supporter_profile_view),
	url(r'^new_contact/$', views.new_contact),
	url(r'^new_thank_you/$', views.new_thank_you),
	url(r'^new_letter/$', views.new_letter),
	url(r'^record_gift/$',views.RecordGiftView.as_view()),
	url(r'(?P<donor_id>[0-9]+)/record_gift/$',views.RecordGiftView.as_view()),
	url(r'^new_gift/$', views.new_gift),
	url(r'^new_call/$', views.new_call),
	url(r'^edit_call/(?P<call_id>[0-9]+)/$', views.edit_call),
	url(r'^new_meeting/$', views.scheduleMeetingModalView.as_view()),
	url(r'^new_voice_mail/$', views.new_voice_mail),
	url(r'(?P<contact_id>[0-9]+)/edit_contact/$', views.edit_contact),
	url(r'(?P<voice_mail_id>[0-9]+)/edit_voice_mail/$',views.edit_voice_mail),
	url(r'(?P<modifier>[\w\-]+)/(?P<thank_you_id>[0-9]+)/edit_thank_you/$',views.recordThankYouModalView.as_view()),
	url(r'(?P<thank_you_id>[0-9]+)/edit_thank_you/$',views.edit_thank_you),
	url(r'(?P<ty_id>[0-9]+)/record_thank_you/$',views.recordThankYouModalView.as_view()),
	url(r'record_thank_you/$',views.recordThankYouModalView.as_view()),
	url(r'^schedule_thank_you/$',views.scheduleThankYouModalView.as_view()),
	url(r'(?P<letter_id>[0-9]+)/edit_letter/$',views.edit_letter),
	url(r'(?P<gift_id>[0-9]+)/edit_gift/$',views.edit_gift),
	url(r'(?P<call_id>[0-9]+)/edit_call/$',views.edit_call),
	url(r'(?P<modifier>[\w\-]+)/(?P<meeting_id>[0-9]+)/record_meeting/$',views.recordMeetingModalView.as_view()),
	url(r'(?P<meeting_id>[0-9]+)/edit_meeting/$',views.edit_meeting),
	url(r'(?P<meeting_id>[0-9]+)/record_meeting/$',views.recordMeetingModalView.as_view()),
	url(r'^record_meeting/$',views.recordMeetingModalView.as_view()),
	url(r'(?P<modifier>[\w\-]+)/(?P<call_id>[0-9]+)/record_call/$',views.recordCallModalView.as_view()),
	url(r'(?P<call_id>[0-9]+)/record_call/$',views.recordCallModalView.as_view()),
	url(r'^record_call/$',views.recordCallModalView.as_view()),
	url(r'^schedule_call/$',views.scheduleCallModalView.as_view()),
	url(r'(?P<modifier>[\w\-]+)/(?P<fup_id>[0-9]+)/record_follow_up/$',views.recordFollowUpModalView.as_view()),
	url(r'(?P<fup_id>[0-9]+)/record_follow_up/$',views.recordFollowUpModalView.as_view()),
	url(r'^record_follow_up/$',views.recordFollowUpModalView.as_view()),
	url(r'^schedule_follow_up/$',views.scheduleFollowUpModalView.as_view()),
	url(r'(?P<reminder_id>[0-9]+)/update_reminder/$',views.updateReminderModalView.as_view()),
	url(r'^new_reminder/$',views.scheduleReminderModalView.as_view()),
	url(r'(?P<modifier>[\w\-]+)/(?P<message_id>[0-9]+)/record_message/$',views.recordMessageModalView.as_view()),
	url(r'(?P<message_id>[0-9]+)/record_message/$',views.recordMessageModalView.as_view()),
	url(r'^record_message/$',views.recordMessageModalView.as_view()),
	url(r'^schedule_message/$',views.scheduleMessageModalView.as_view()),
	url(r'^contact_list/$',views.ContactListView.as_view()),
	url(r'^supporter_list/$',views.SupporterListView.as_view()),
	url(r'(?P<contact_id>[0-9]+)/contact_info/$',views.ContactInfoModalView.as_view()),
	url(r'(?P<contact_rel_id>[0-9]+)/contact_profile/$',views.ContactProfileView.as_view()),
]
