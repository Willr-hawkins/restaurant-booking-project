import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

DEPOSIT_AMOUNT_PENCE = 1000 # £10 flat deposit

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

def create_deposit_checkout_session(booking, success_url, cancel_url):
    session = stripe.checkout.Session.create(
        mode='payment',
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'gbp',
                'product_data': {'name': f'Deposit — Yūgen booking for {booking.guest_name}'},
                'unit_amount': DEPOSIT_AMOUNT_PENCE,
            },
            'quantity': 1,
        }],
        payment_intent_data={'metadata': {'booking_id': booking.id}},
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session