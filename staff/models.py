from django.contrib.auth.models import User
from django.db import models

class StaffProfile(models.Model):
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('staff', 'Staff'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"
    
    @property
    def is_manager(self):
        return self.role == 'manager'

