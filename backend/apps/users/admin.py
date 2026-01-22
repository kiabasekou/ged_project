from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Correction list_display : on utilise les méthodes définies plus bas
    list_display = (
        'username', 
        'get_full_name', 
        'get_role_display', 
        'professional_id', 
        'is_active', 
        'is_staff'
    )
    
    # Correction list_filter : 'is_legal_professional' est une propriété, 
    # elle est retirée car on ne peut filtrer que sur des champs DB réels.
    list_filter = ('role', 'is_active', 'is_staff', 'groups')
    
    search_fields = ('username', 'first_name', 'last_name', 'email', 'professional_id')
    ordering = ('last_name', 'first_name')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Informations personnelles'), {
            'fields': ('first_name', 'last_name', 'email', 'phone_number')
        }),
        (_('Profession'), {
            'fields': ('role', 'professional_id', 'is_legal_professional')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Dates importantes'), {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
        (_('RGPD'), {
            'fields': ('has_accepted_privacy_policy', 'privacy_policy_accepted_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('is_legal_professional', 'date_joined', 'last_login', 'privacy_policy_accepted_at')
    filter_horizontal = ('groups', 'user_permissions',)

    # --- Méthodes calculées pour l'affichage dans la liste ---

    @admin.display(description=_("Nom complet"), ordering='last_name')
    def get_full_name(self, obj):
        return obj.get_full_name()

    @admin.display(description=_("Rôle"), ordering='role')
    def get_role_display(self, obj):
        # Utilise la méthode native de Django pour les choix (Choices)
        return obj.get_role_display()

    @admin.display(description=_("Pro."), boolean=True)
    def is_legal_pro(self, obj):
        # Si vous voulez quand même l'afficher sous forme d'icône check/cross
        return obj.is_legal_professional