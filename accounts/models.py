from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom User model that extends the built-in Django User model.
    """
    USER_TYPE_CHOICES = (
        ('admin', 'Administrator'),
        ('staff', 'Staff/Volunteer'),
        ('judge', 'Judge'),
        ('veterinary', 'Veterinary'),
        ('participant', 'Participant'),
    )
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='participant'
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    def is_admin(self):
        return self.user_type == 'admin' or self.is_superuser
    
    def is_staff_member(self):
        return self.user_type == 'staff'
    
    def is_judge(self):
        return self.user_type == 'judge'
    
    def is_veterinary(self):
        return self.user_type == 'veterinary'
    
    def is_participant(self):
        return self.user_type == 'participant'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"
