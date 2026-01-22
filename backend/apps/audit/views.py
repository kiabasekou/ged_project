# backend/apps/audit/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from .models import AuditLog
from .serializers import AuditLogSerializer

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lecture seule des logs d'audit.
    Réservé exclusivement aux administrateurs.
    """
    queryset = AuditLog.objects.all().select_related('user')
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminUser]

    # Optionnel : filtrage par date, utilisateur, action, etc.
    filterset_fields = ['action_type', 'user', 'timestamp']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']