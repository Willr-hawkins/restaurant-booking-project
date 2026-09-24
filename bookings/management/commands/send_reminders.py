from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from bookings.models import Booking
from bookings.emails import send_booking_reminder

class Command(BaseCommand):
    help = "Send reminder emails for bookings happening tomorrow"

    def handle(self, *args, **options):
        target_date = timezone.localtime().date() + timedelta(days=1)
        bookings = Booking.objects.filter(date=target_date, status='confirmed', reminder_email_status='')

        sent = 0
        failed = 0
        for booking in bookings:
            send_booking_reminder(booking)
            if booking.reminder_email_status.startswith('Sent'):
                sent += 1
            else:
                failed += 1

        self.stdout.write(self.style.SUCCESS(
            f"Reminders for {target_date}: {sent} sent, {failed} failed."
        ))