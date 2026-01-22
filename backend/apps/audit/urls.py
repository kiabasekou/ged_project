# backend/apps/audit/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import IsAdminUser
from .views import AuditLogViewSet  # À créer avec permission admin only

router = DefaultRouter()
router.register(r'', AuditLogViewSet, basename='auditlog')

# On surcharge les permissions globales pour forcer l'accès admin uniquement
urlpatterns = [
    path('', include(router.urls)),
]

# Note : dans la vue AuditLogViewSet, ajoute :
# permission_classes = [IsAdminUser]  # ou une permission custom plus fine