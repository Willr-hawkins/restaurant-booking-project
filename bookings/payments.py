import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_deposit_payment_intent(booking, amount_pence):
    """
    Creates a Stripe PaymentIntent for a booking's deposit. amount_pence is the
    charge amount in the smallest currency unit (pence, not pounds) - Stripe's
    convention for avoiding floating-point rounding issues with money.
    """
    intent = stripe.PaymentIntent.create(
        amount=amount_pence,
        currency='gbp',
        metadata={'booking_id': booking.id},
    )
    return intent
