# backend/apps/audit/utils.py

from .models import AuditLog
from django.contrib.contenttypes.models import ContentType


def log_action(
    user,
    obj,
    action: str,
    changes: dict | None = None,
    description: str = "",
    request=None
):
    """
    Fonction utilitaire centralisée pour créer un log d'audit.
    Utilisée dans tous les ViewSets pour tracer les actions sensibles.

    Args:
        user: L'utilisateur Django ayant effectué l'action (ou None pour système)
        obj: L'objet concerné (Dossier, Document, Client, User, etc.)
        action: Une des valeurs de AuditLog.Action (ex: 'CREATE', 'VIEW', 'DOWNLOAD')
        changes: Dict des modifications (pour UPDATE) → {'champ': ['ancien', 'nouveau']}
        description: Commentaire libre (ex: "Téléchargement justifié par envoi au client")
        request: Objet HttpRequest pour récupérer IP, user-agent, URL, session
    """
    ip_address = None
    user_agent = ""
    request_path = ""
    session_key = None # Par défaut à None pour le NULL en DB

    if request:
        # Récupération de l'IP (gestion des proxys éventuels)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        request_path = request.path[:500]
        
        # Récupération sécurisée de la session
        session = getattr(request, 'session', None)
        if session:
            session_key = session.session_key

    return AuditLog.objects.create(
        user=user,
        content_type=ContentType.objects.get_for_model(obj),
        object_id=obj.id,
        object_repr=str(obj)[:255],
        action_type=action,
        changes=changes if changes else None,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent,
        request_path=request_path,
        session_key=session_key,
    )