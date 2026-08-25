from django.urls import path
from . import views

urlpatterns = [
    path('', views.booking_widget, name='booking_widget'),
    path('slots/', views.booking_slots, name='booking_slots'),
    path('details/', views.booking_details, name='booking_details'),
    path('confirm/', views.booking_confirm, name='booking_confirm'),
]