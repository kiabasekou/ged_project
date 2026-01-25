"""
Utilitaires d'audit et middleware pour traçabilité automatique.
"""
from typing import Optional, Dict, Any
from django.utils.deprecation import MiddlewareMixin
from .models import AuditLog


def log_action(user, obj, action_type: str, description: str = "",
               changes: Optional[Dict] = None, request=None):
    """
    Fonction helper pour créer rapidement une entrée d'audit.
    
    Usage:
        from apps.audit.utils import log_action
        
        log_action(
            user=request.user,
            obj=document,
            action_type='CREATE',
            description='Upload du document contrat.pdf'
        )
    """
    return AuditLog.log_action(
        user=user,
        obj=obj,
        action_type=action_type,
        description=description,
        changes=changes,
        request=request
    )


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware pour audit automatique des requêtes importantes.
    """
    
    # Méthodes HTTP à auditer
    AUDITED_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
    
    # Chemins à exclure de l'audit
    EXCLUDED_PATHS = [
        '/admin/jsi18n/',
        '/static/',
        '/media/',
        '/__debug__/',
    ]
    
    def process_request(self, request):
        """Enregistre le début de la requête"""
        request._audit_start_time = __import__('time').time()
        return None
    
    def process_response(self, request, response):
        """
        Audit automatique des actions critiques.
        Ne log que les succès (codes 2xx et 3xx).
        """
        # Ignorer si chemin exclu
        if any(request.path.startswith(path) for path in self.EXCLUDED_PATHS):
            return response
        
        # Ignorer si méthode non-auditée
        if request.method not in self.AUDITED_METHODS:
            return response
        
        # Ignorer les échecs (déjà logués ailleurs)
        if response.status_code >= 400:
            return response
        
        # Ignorer si utilisateur non authentifié
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return response
        
        # Déterminer le type d'action selon la méthode HTTP
        action_map = {
            'POST': 'CREATE',
            'PUT': 'UPDATE',
            'PATCH': 'UPDATE',
            'DELETE': 'DELETE',
        }
        action_type = action_map.get(request.method, 'READ')
        
        # Calculer le temps de réponse
        duration = None
        if hasattr(request, '_audit_start_time'):
            duration = round((__import__('time').time() - request._audit_start_time) * 1000, 2)
        
        # Créer l'entrée d'audit générique (sans objet spécifique)
        try:
            from django.contrib.contenttypes.models import ContentType
            
            # Tentative d'extraction de l'objet concerné depuis la vue
            obj = getattr(request, '_audit_object', None)
            
            if obj:
                AuditLog.log_action(
                    user=request.user,
                    obj=obj,
                    action_type=action_type,
                    description=f"[AUTO] {request.method} {request.path}",
                    changes={'duration_ms': duration} if duration else None,
                    request=request
                )
        except Exception as e:
            # Ne jamais bloquer la requête à cause d'un échec d'audit
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Échec audit automatique: {str(e)}")
        
        return response


def audit_view(action_type: str = None):
    """
    Décorateur pour forcer l'audit d'une vue spécifique.
    
    Usage:
        from apps.audit.utils import audit_view
        
        @audit_view(action_type='DOWNLOAD')
        def download_document(request, pk):
            ...
    """
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            # Exécuter la vue
            response = view_func(request, *args, **kwargs)
            
            # Déterminer l'objet si possible
            obj = getattr(request, '_audit_object', None)
            
            if obj and request.user.is_authenticated:
                log_action(
                    user=request.user,
                    obj=obj,
                    action_type=action_type or 'READ',
                    description=f"{view_func.__name__} appelé",
                    request=request
                )
            
            return response
        
        return wrapped_view
    
    return decorator


class AuditableMixin:
    """
    Mixin pour ViewSets DRF avec audit automatique.
    
    Usage:
        class DocumentViewSet(AuditableMixin, viewsets.ModelViewSet):
            queryset = Document.objects.all()
            ...
    """
    
    def perform_create(self, serializer):
        """Override pour auditer les créations"""
        instance = serializer.save()
        
        log_action(
            user=self.request.user,
            obj=instance,
            action_type='CREATE',
            description=f"Création via API: {instance}",
            request=self.request
        )
        
        return instance
    
    def perform_update(self, serializer):
        """Override pour auditer les modifications"""
        # Récupérer les changements
        old_instance = self.get_object()
        old_data = {
            field: getattr(old_instance, field)
            for field in serializer.validated_data.keys()
        }
        
        instance = serializer.save()
        
        changes = {
            field: {
                'old': old_data.get(field),
                'new': getattr(instance, field)
            }
            for field in serializer.validated_data.keys()
            if old_data.get(field) != getattr(instance, field)
        }
        
        log_action(
            user=self.request.user,
            obj=instance,
            action_type='UPDATE',
            description=f"Modification via API: {instance}",
            changes=changes,
            request=self.request
        )
        
        return instance
    
    def perform_destroy(self, instance):
        """Override pour auditer les suppressions"""
        log_action(
            user=self.request.user,
            obj=instance,
            action_type='DELETE',
            description=f"Suppression via API: {instance}",
            request=self.request
        )
        
        instance.delete()
