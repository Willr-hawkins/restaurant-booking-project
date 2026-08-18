from datetime import date, time, timedelta
from django.test import TestCase
from django.utils import timezone

from .models import Service, SpecialHours
from .availability import get_available_slots

class AvailabilityTests(TestCase):
    def setUp(self):
        # Tuesday dinner service
        self.service = Service.objects.create(
            name='Dinner',
            day_of_week=1,
            start_time=time(17, 30),
            end_time=time(21, 30),
            last_booking_time=time(20, 45),
            slot_interval_minutes=15,
            is_active=True,
        )

    def _next_weekday(self, weekday):
        today = timezone.localtime().date()
        days_ahead = (weekday - today.weekday()) % 7
        days_ahead = days_ahead or 7 # always get a future date, not today
        return today + timedelta(days=days_ahead)
    
    def test_slots_generated_within_service_window(self):
        target_date = self._next_weekday(1) # a future Tuesday
        slots = get_available_slots(target_date)
        self.assertIn(time(17, 30), slots)
        self.assertIn(time(20, 45), slots)
        self.assertNotIn(time(21, 0), slots)  # past last_booking_time

    def test_closed_day_returns_no_slots(self):
        target_date = self._next_weekday(2) #wednesday - no Service seeded
        slots = get_available_slots(target_date)
        self.assertEqual(slots, [])

    def test_special_hours_closure_overrides_service(self):
        target_date = self._next_weekday(1)
        SpecialHours.objects.create(date=target_date, is_closed=True, reason='Test Closure')
        slots = get_available_slots(target_date)
        self.assertEqual(slots, [])

    def test_special_hours_custom_override(self):
        target_date = self._next_weekday(1)
        SpecialHours.objects.create(
            date=target_date,
            is_closed=False,
            custom_start_time=time(12, 0),
            custom_end_time=time(15, 0),
            reason='Test custom hours',
        )
        slots = get_available_slots(target_date)
        self.assertIn(time(12, 0), slots)
        self.assertNotIn(time(17, 30), slots) # normal Tuesday dinner slots excluded