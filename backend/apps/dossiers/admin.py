# backend/apps/dossiers/admin.py

from django.contrib import admin
from .models import Dossier

@admin.register(Dossier)
class DossierAdmin(admin.ModelAdmin):
    list_display = ('reference_code', 'title', 'client_name', 'responsible_name', 'category', 'status', 'critical_deadline', 'is_overdue')
    list_filter = ('status', 'category', 'responsible', 'opening_date')
    search_fields = ('reference_code', 'title', 'client__display_name', 'opponent')
    date_hierarchy = 'opening_date'
    ordering = ('-opening_date',)

    fieldsets = (
        (None, {'fields': ('reference_code', 'title', 'client', 'responsible')}),
        ('Détails', {'fields': ('category', 'status', 'opening_date', 'closing_date', 'critical_deadline')}),
        ('Contentieux', {'fields': ('opponent', 'jurisdiction')}),
        ('Collaborateurs', {'fields': ('assigned_users',)}),
        ('Notes', {'fields': ('description',)}),
    )

    filter_horizontal = ('assigned_users',)

    readonly_fields = ('reference_code',)

    def client_name(self, obj):
        return obj.client.display_name if obj.client else '-'
    client_name.short_description = "Client"

    def responsible_name(self, obj):
        return obj.responsible.get_full_name() if obj.responsible else '-'
    responsible_name.short_description = "Responsable"

    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = "En retard"