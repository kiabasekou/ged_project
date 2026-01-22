# backend/config/admin.py

from django.contrib import admin
from django.contrib.auth import get_user_model

admin.site.site_header = "Administration GED By SO Consulting"
admin.site.site_title = "GED Cabinet"
admin.site.index_title = "Bienvenue dans l’administration sécurisée"

# Optionnel : logo custom
# admin.site.site_url = '/'