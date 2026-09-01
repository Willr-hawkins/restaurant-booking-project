from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse

def send_booking_confirmation(booking):
    manage_url = f"{settings.SITE_URL}{reverse('booking_manage', args=[booking.manage_token])}"
    subject = f"Your table at Yūgen — {booking.date} at {booking.time.strftime('%-I:%M %p')}"
    html_content = render_to_string('bookings/emails/confirmation.html', {'booking': booking, 'manage_url': manage_url})

    message = Mail(
        from_email=settings.FROM_EMAIL,
        to_emails=booking.guest_email,
        subject=subject,
        html_content=html_content,
    )

    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        booking.confirmation_email_status = f"Sent (status {response.status_code})"
    except Exception as e:
        booking.confirmation_email_status = f"Failed: {e}"
    
    booking.save(update_fields=['confirmation_email_status'])

def send_booking_reminder(booking):
    subject = f"Reminder: your table at Yūgen tonight at {booking.time.strftime('%-I:%M %p')}"
    html_content = render_to_string('bookings/emails/reminder.html', {'booking': booking})

    message = Mail(
        from_email=settings.FROM_EMAIL,
        to_emails=booking.guest_email,
        subject=subject,
        html_content=html_content,
    )

    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        booking.reminder_email_status = f"Sent (status {response.status_code})"
    except Exception as e:
        booking.reminder_email_status = f"Failed: {e}"

    booking.save(update_fields=['reminder_email_status'])