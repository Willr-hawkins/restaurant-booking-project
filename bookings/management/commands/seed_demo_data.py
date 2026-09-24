import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from bookings.models import Booking, Guest, get_or_create_guest
from bookings.availability import find_best_table_or_combination, predict_duration
from bookings.models import Service


GUESTS = [
    ("Aiko Tanaka", "aiko.tanaka@example.com", "07700900101", False, ""),
    ("James Fletcher", "james.fletcher@example.com", "07700900102", False, ""),
    ("Priya Shah", "priya.shah@example.com", "07700900103", True, "Prefers window seating, celebrates anniversary here every year."),
    ("Tom Bracewell", "tom.bracewell@example.com", "07700900104", False, ""),
    ("Emily Carter", "emily.carter@example.com", "07700900105", False, "Vegetarian, always asks about the tasting menu."),
    ("Daniel Osei", "daniel.osei@example.com", "07700900106", False, ""),
    ("Sophie Nguyen", "sophie.nguyen@example.com", "07700900107", True, "Regular — books most Fridays."),
    ("Mark Ellison", "mark.ellison@example.com", "07700900108", False, "Has no-showed before, confirm by phone if possible."),
    ("Hana Yoshida", "hana.yoshida@example.com", "07700900109", False, ""),
    ("Chris Whitfield", "chris.whitfield@example.com", "07700900110", False, ""),
    ("Olivia Bennett", "olivia.bennett@example.com", "07700900111", False, ""),
    ("Ryo Matsumoto", "ryo.matsumoto@example.com", "07700900112", False, ""),
    ("Freya Sinclair", "freya.sinclair@example.com", "07700900113", False, ""),
    ("Noah Patel", "noah.patel@example.com", "07700900114", False, ""),
    ("Isla Robertson", "isla.robertson@example.com", "07700900115", False, ""),
]


class Command(BaseCommand):
    help = "Seed realistic demo bookings (past and future) using real Guests and the real assignment engine."

    def handle(self, *args, **options):
        random.seed(42)  # reproducible results each run

        guests = []
        for name, email, phone, is_vip, notes in GUESTS:
            guest = get_or_create_guest(name, email, phone)
            if is_vip or notes:
                guest.is_vip = is_vip
                guest.notes = notes
                guest.save(update_fields=['is_vip', 'notes'])
            guests.append(guest)

        today = timezone.localdate()
        created_count = 0

        # Past 14 days + next 14 days
        for offset in range(-14, 15):
            day = today + timedelta(days=offset)
            services = Service.objects.filter(day_of_week=day.weekday(), is_active=True)
            if not services.exists():
                continue

            # 2-5 bookings per open day
            for _ in range(random.randint(2, 5)):
                service = random.choice(list(services))
                guest = random.choice(guests)
                party_size = random.choice([2, 2, 2, 3, 4, 4, 6])

                # pick a random slot within the service window
                slot_minutes = random.randrange(0, 90, service.slot_interval_minutes)
                hour = service.start_time.hour
                minute = service.start_time.minute + slot_minutes
                hour += minute // 60
                minute = minute % 60
                if hour >= service.end_time.hour:
                    continue

                from datetime import time as dtime
                slot_time = dtime(hour, minute)

                assigned = find_best_table_or_combination(day, slot_time, party_size)
                if not assigned:
                    continue

                from django.contrib.contenttypes.models import ContentType
                content_type = ContentType.objects.get_for_model(assigned)
                duration = predict_duration(party_size, slot_time)

                if offset < 0:
                    status = random.choices(
                        ['completed', 'no_show', 'cancelled'], weights=[80, 12, 8]
                    )[0]
                else:
                    status = 'confirmed'

                deposit_required = party_size >= 6

                Booking.objects.create(
                    guest_name=guest.name,
                    guest_email=guest.email,
                    guest_phone=guest.phone,
                    guest=guest,
                    date=day,
                    time=slot_time,
                    party_size=party_size,
                    table_content_type=content_type,
                    table_object_id=assigned.id,
                    predicted_duration_minutes=duration,
                    buffer_minutes=15,
                    status=status,
                    deposit_required=deposit_required,
                    deposit_paid=deposit_required and status != 'cancelled',
                )
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(guests)} guests and {created_count} bookings across 29 days."
        ))