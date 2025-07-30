from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=8, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    class Meta:
        db_table = 'user_profile'

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    
    def __str__(self):
        return f"Event: {self.title} - Created by {self.created_by.username} on {self.date.strftime('%Y-%m-%d')} at {self.time.strftime('%H:%M')}"
    
    class Meta:
        db_table = 'event'
        ordering = ['-date', '-time']

class Attendee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendees')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendances')
    confirmed = models.BooleanField(default=False)    
    
    def __str__(self):
        return f"{self.user.username} - {self.event.title}"
    
    class Meta:
        db_table = 'attendee'
        unique_together = ('user', 'event')  # Ensure a user can only register for an event once