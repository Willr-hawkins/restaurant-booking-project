from django.urls import path
from . import views

urlpatterns = [
    path('', views.booking_widget, name='booking_widget'),
    path('slots/', views.booking_slots, name='booking_slots'),
    path('details/', views.booking_details, name='booking_details'),
    path('confirm/', views.booking_confirm, name='booking_confirm'),
    path('manage/<uuid:token>/', views.booking_manage, name='booking_manage'),
    path('manage/<uuid:token>/cancel/', views.booking_cancel, name='booking_cancel'),
    path('manage/<uuid:token>/modify/', views.booking_modify, name='booking_modify'),
    path('phone/', views.phone_booking_create, name='phone_booking_create'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('payment-success/<uuid:token>/', views.booking_payment_success, name='booking_payment_success'),
]