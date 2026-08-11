from django.contrib import admin
from .models import Service, SpecialHours

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'day_of_week', 'start_time', 'end_time', 'last_booking_time', 'slot_interval_minutes', 'is_active')
    list_filter = ('day_of_week', 'is_active')
    ordering = ('day_of_week', 'start_time')

@admin.register(SpecialHours)
class SpecialHoursAdmin(admin.ModelAdmin):
    list_display = ('date', 'is_closed', 'custom_start_time', 'custom_end_time', 'reason')
    list_filter = ('is_closed',)
    ordering = ('date',)
