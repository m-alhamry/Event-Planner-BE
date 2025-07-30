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