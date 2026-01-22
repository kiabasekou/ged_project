# backend/apps/clients/admin.py

from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'client_type', 'phone_primary', 'email', 'city', 'is_active', 'dossier_count')
    list_filter = ('client_type', 'city', 'neighborhood', 'is_active', 'consent_given')
    search_fields = ('first_name', 'last_name', 'company_name', 'nif', 'rccm', 'phone_primary', 'email')
    ordering = ('last_name', 'company_name')

    fieldsets = (
        (None, {'fields': ('client_type',)}),
        ('Personne physique', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'place_of_birth', 'ni_number', 'ni_type'),
            'classes': ('collapse',) if 'MORALE' in 'client_type' else ()
        }),
        ('Personne morale', {
            'fields': ('company_name', 'rccm', 'nif', 'representative_name', 'representative_role'),
            'classes': ('collapse',) if 'PHYSIQUE' in 'client_type' else ()
        }),
        ('Contact', {'fields': ('phone_primary', 'phone_secondary', 'email')}),
        ('Adresse', {'fields': ('address_line', 'neighborhood', 'city', 'country')}),
        ('RGPD & Suivi', {'fields': ('consent_given', 'consent_date', 'data_source', 'retention_period_years', 'notes', 'is_active')}),
    )

    readonly_fields = ('display_name', 'full_address')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(dossier_count=models.Count('dossiers'))

    def dossier_count(self, obj):
        return obj.dossier_count
    dossier_count.short_description = "Nb dossiers"
    dossier_count.admin_order_field = 'dossier_count'