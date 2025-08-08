from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.

User = settings.AUTH_USER_MODEL

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    class Meta:
        db_table = 'user'

class Event(models.Model):
    title = models.CharField(max_length=200, blank=False)
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField(blank=False)
    location = models.CharField(max_length=255, blank=False)
    created_by = models.ForeignKey(User, blank=False, on_delete=models.CASCADE, related_name='created_events')
    
    def __str__(self):
        return f"Event: {self.title} - Created by {self.created_by.username}. This Event will be on {self.date.strftime('%Y-%m-%d')} at {self.date.strftime('%H:%M')}"
    
    class Meta:
        db_table = 'event'
        ordering = ['-date']

class Attendee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendees')
    confirmed = models.BooleanField(default=False)    
    
    def __str__(self):
        return f"user: {self.user.username} attending event: {self.event.title}"
    
    class Meta:
        db_table = 'attendee'
        unique_together = ('user', 'event')  # Ensure a user can only register for an event once