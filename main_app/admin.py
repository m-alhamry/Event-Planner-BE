from django.contrib import admin
from .models import CustomUser, UserProfile, Event, Attendee

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(UserProfile)
admin.site.register(Event)
admin.site.register(Attendee)
