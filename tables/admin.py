from django.contrib import admin
from .models import Table, TableCombination

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_covers', 'max_covers', 'section', 'is_active')
    list_filter = ('section', 'is_active')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(TableCombination)
class TableCombinationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'min_covers', 'max_covers', 'is_active')
    filter_horizontal = ('tables',)
    list_filter = ('is_active',)