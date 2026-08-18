from datetime import date, time, timedelta
from django.test import TestCase
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from .models import Service, SpecialHours, Booking
from .availability import get_available_slots, is_table_free, predict_duration, is_table_free_for_party, find_best_single_table
from tables.models import Table

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

class TurnaroundBufferTests(TestCase):
    def setUp(self):
        self.table = Table.objects.create(name='Test Table', min_covers=2, max_covers=4)
        self.target_date = timezone.localtime().date() + timedelta(days=1)
        Booking.objects.create(
            guest_name='Existing Guest',
            guest_email='existing@example.com',
            guest_phone='07700900000',
            date=self.target_date,
            time=time(18, 30),
            party_size=2,
            predicted_duration_minutes=75,  # ends 19:45
            buffer_minutes=15,              # free again at 20:00
            table_content_type=ContentType.objects.get_for_model(Table),
            table_object_id=self.table.id,
        )

    def test_table_busy_before_buffer_clears(self):
        self.assertFalse(is_table_free(self.table, self.target_date, time(19, 59), 90))

    def test_table_free_exactly_at_buffer_clear(self):
        self.assertTrue(is_table_free(self.table, self.target_date, time(20, 0), 90))

    def test_table_free_on_different_date(self):
        other_date = self.target_date + timedelta(days=1)
        self.assertTrue(is_table_free(self.table, other_date, time(18, 30), 90))

    def test_table_free_when_no_bookings(self):
        empty_table = Table.objects.create(name='Empty Table', min_covers=2, max_covers=4)
        self.assertTrue(is_table_free(empty_table, self.target_date, time(19, 0), 90))

class DurationPredictionTests(TestCase):
    def test_small_party_lunch(self):
        self.assertEqual(predict_duration(2, time(12, 30)), 75)

    def test_small_party_dinner(self):
        self.assertEqual(predict_duration(2, time(19, 0)), 90)

    def test_large_party_lunch(self):
        self.assertEqual(predict_duration(8, time(13, 0)), 120)

    def test_large_party_dinner(self):
        self.assertEqual(predict_duration(8, time(20, 0)), 150)
    
    def test_lunch_dinner_boundary(self):
        self.assertEqual(predict_duration(2, time(15, 59)), 75)
        self.assertEqual(predict_duration(2, time(16, 0)), 90)

class IsTableFreeForPartyTests(TestCase):
    def setUp(self):
        self.table = Table.objects.create(name='Duration Test Table', min_covers=2, max_covers=8)
        self.target_date = timezone.localtime().date() + timedelta(days=1)

    def test_free_table_with_predicted_duration(self):
        self.assertTrue(is_table_free_for_party(self.table, self.target_date, time(19, 0), 4))

    def test_busy_table_blocks_large_party_prediction(self):
        Booking.objects.create(
            guest_name='Blocker',
            guest_email='blocker@example.com',
            guest_phone='07700900001',
            date=self.target_date,
            time=time(19, 0),
            party_size=8,
            predicted_duration_minutes=150,
            buffer_minutes=15,
            table_content_type=ContentType.objects.get_for_model(Table),
            table_object_id=self.table.id,
        )
        # A new 4-top booking at 20:00 would overlap the 8-top's 150+15 min occupancy (frees at 21:45)
        self.assertFalse(is_table_free_for_party(self.table, self.target_date, time(20, 0), 4))

class TightFitAssignmentTests(TestCase):
    def setUp(self):
        self.small_a = Table.objects.create(name='Small A', min_covers=2, max_covers=4)
        self.small_b = Table.objects.create(name='Small B', min_covers=2, max_covers=4)
        self.large = Table.objects.create(name='Large', min_covers=4, max_covers=6)
        self.target_date = timezone.localtime().date() + timedelta(days=1)

    def test_smallest_fitting_table_chosen(self):
        result = find_best_single_table(self.target_date, time(19, 0), 3)
        self.assertEqual(result, self.small_a)  # first by max_covers then id

    def test_larger_party_skips_small_tables(self):
        result = find_best_single_table(self.target_date, time(19, 0), 5)
        self.assertEqual(result, self.large)

    def test_falls_back_to_next_candidate_when_first_is_busy(self):
        Booking.objects.create(
            guest_name='Occupying', guest_email='occ@example.com', guest_phone='07700900002',
            date=self.target_date, time=time(19, 0), party_size=3,
            predicted_duration_minutes=90, buffer_minutes=15,
            table_content_type=ContentType.objects.get_for_model(Table),
            table_object_id=self.small_a.id,
        )
        result = find_best_single_table(self.target_date, time(19, 0), 3)
        self.assertEqual(result, self.small_b)

    def test_no_fitting_table_returns_none(self):
        result = find_best_single_table(self.target_date, time(19, 0), 20)
        self.assertIsNone(result)