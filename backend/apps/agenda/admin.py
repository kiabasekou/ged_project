# backend/apps/agenda/admin.py

from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'start_date', 'start_time', 'all_day', 'location', 'created_by')
    list_filter = ('type', 'start_date', 'all_day')
    search_fields = ('title', 'location', 'description')
    date_hierarchy = 'start_date'

    fieldsets = (
        (None, {'fields': ('title', 'type')}),
        ('Date et heure', {'fields': ('start_date', 'start_time', 'all_day', 'end_date', 'end_time')}),
        ('Lieu et lien', {'fields': ('location', 'dossier')}),
        ('Description', {'fields': ('description',)}),
    )