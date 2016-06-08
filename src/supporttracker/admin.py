from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Person, UserProfile, SupportRelationship, ContactRelationship, Letter, Call, Meeting, ThankYou, VoiceMail, Referral, Reminder, Note, Message

class UserProfileInline(admin.StackedInline):
	model = UserProfile
	can_delete = False
	verbose_name_plural = 'User Profile'
	
class UserAdmin(BaseUserAdmin):
	inlines = (UserProfileInline,)
	
admin.site.unregister(User)
admin.site.register(User,UserAdmin)
admin.site.register(Person)
admin.site.register(SupportRelationship)
admin.site.register(ContactRelationship)
admin.site.register(Letter)
admin.site.register(Call)
admin.site.register(Meeting)
admin.site.register(ThankYou)
admin.site.register(VoiceMail)
admin.site.register(Referral)
admin.site.register(Reminder)
admin.site.register(Note)
admin.site.register(Message)

