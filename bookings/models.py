from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
import uuid
from datetime import datetime, timedelta
from django.utils import timezone

class Service(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    name = models.CharField(max_length=100) # e.g, "Lunch", "Dinner"
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    last_booking_time = models.TimeField(
        help_text="Latest time a booking can be made for this service"
    )
    slot_interval_minutes = models.PositiveIntegerField(
        default=30,
        help_text="Interval between available booking slots, e.g. 15 or 20 minutes"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.name} ({self.get_day_of_week_display()})"
    
class SpecialHours(models.Model):
    """ Overrides normal service hours for a specific date - closures, holidays, private functions. """
    date = models.DateField(unique=True)
    is_closed = models.BooleanField(default=True)
    custom_start_time = models.TimeField(null=True, blank=True)
    custom_end_time = models.TimeField(null=True, blank=True)
    reason = models.CharField(max_length=255, blank=True) # e.g, "Christmas Day", "Private Function"

    class Meta:
        ordering = ['date']
        verbose_name_plural = 'Special hours'

    def __str__(self):
        status = "Closed" if self.is_closed else "Custom Hours"
        return f"{self.date} - {status}"

class Booking(models.Model):
    CANCELLATION_CUTOFF_HOURS = 2    

    STATUS_CHOICES = [
        ('awaiting_payment', 'Awaiting Payment'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
        ('completed', 'Completed'),
    ]

    # Guest details
    guest_name = models.CharField(max_length=150)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=30)

    # Booking details
    date = models.DateField()
    time = models.TimeField()
    party_size = models.PositiveIntegerField()
    special_requests = models.TextField(blank=True)
    seating_preference = models.CharField(max_length=20, blank=True)

    # Assignment - either a Table or a TableCombination, never both
    table_content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    table_object_id = models.PositiveIntegerField(null=True, blank=True)
    assigned_table = GenericForeignKey('table_content_type', 'table_object_id')

    # Timing
    predicted_duration_minutes = models.PositiveIntegerField(default=90)
    buffer_minutes = models.PositiveIntegerField(default=15)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    confirmation_email_status = models.CharField(max_length=225, blank=True)
    reminder_email_status = models.CharField(max_length=225, blank=True)

    # Deposits - parties of 6+, wired up properly in Sprint 6
    deposit_required = models.BooleanField(default=False)
    deposit_paid = models.BooleanField(default=False)
    deposit_amount = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    manage_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    @property
    def is_editable(self):
        booking_dt = timezone.make_aware(datetime.combine(self.date, self.time))
        return booking_dt - timezone.localtime() > timedelta(hours=self.CANCELLATION_CUTOFF_HOURS)
    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        return f"{self.guest_name} - {self.date} {self.time} ({self.party_size})"