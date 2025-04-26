from django.db import models
from registrations.models import Registration

class RaceResult(models.Model):
    """
    Model representing race results for a participant.
    """
    registration = models.OneToOneField(Registration, related_name='result', on_delete=models.CASCADE)
    
    # Race times
    start_time = models.DateTimeField(null=True, blank=True)
    finish_time = models.DateTimeField(null=True, blank=True)
    base_time = models.DurationField(null=True, blank=True, help_text="Finish time - Start time")
    official_time = models.DurationField(null=True, blank=True, help_text="Base time + penalties")
    
    # Status
    STATUS_CHOICES = (
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('finished', 'Finished'),
        ('dnf', 'Did Not Finish'),
        ('dq', 'Disqualified'),
        ('dns', 'Did Not Start'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    
    # Rankings
    overall_rank = models.PositiveIntegerField(null=True, blank=True)
    modality_rank = models.PositiveIntegerField(null=True, blank=True)
    category_rank = models.PositiveIntegerField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.registration.participant} - {self.registration.race} - {self.official_time or 'No time'}"
    
    class Meta:
        ordering = ['official_time', 'status']
