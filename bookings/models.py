from django.db import models

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
