"""
Utilitaires et fonctions helpers pour l'application GED Cabinet.
"""
import hashlib
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Union
from django.utils import timezone


def generate_reference_code(prefix: str, year: Optional[int] = None, counter: Optional[int] = None) -> str:
    """
    Génère un code de référence pour un dossier.
    
    Format : PREFIX/YYYY/NNNN
    Exemple : CAB/2024/0001
    
    Args:
        prefix: Préfixe (ex: "CAB", "CONT", "PROC")
        year: Année (défaut: année courante)
        counter: Numéro séquentiel (défaut: calculé automatiquement)
    
    Returns:
        Code de référence formaté
    """
    if year is None:
        year = timezone.now().year
    
    if counter is None:
        # En production, counter devrait être récupéré depuis la DB
        counter = 1
    
    return f"{prefix.upper()}/{year}/{counter:04d}"


def generate_secure_token(length: int = 32) -> str:
    """
    Génère un token cryptographiquement sécurisé.
    
    Args:
        length: Longueur du token (défaut: 32)
    
    Returns:
        Token aléatoire sécurisé
    """
    return secrets.token_urlsafe(length)


def generate_password(length: int = 12) -> str:
    """
    Génère un mot de passe aléatoire sécurisé.
    
    Args:
        length: Longueur du mot de passe (défaut: 12)
    
    Returns:
        Mot de passe avec majuscules, minuscules, chiffres et symboles
    """
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(characters) for _ in range(length))
    
    # S'assurer qu'il contient au moins un de chaque type
    if not any(c.isupper() for c in password):
        password = password[:-1] + secrets.choice(string.ascii_uppercase)
    if not any(c.isdigit() for c in password):
        password = password[:-1] + secrets.choice(string.digits)
    if not any(c in "!@#$%^&*" for c in password):
        password = password[:-1] + secrets.choice("!@#$%^&*")
    
    return password


def calculate_file_hash(file_obj, algorithm: str = 'sha256') -> str:
    """
    Calcule le hash d'un fichier.
    
    Args:
        file_obj: Objet fichier Django
        algorithm: Algorithme de hachage (sha256, sha512, md5)
    
    Returns:
        Hash hexadécimal du fichier
    """
    hash_obj = hashlib.new(algorithm)
    
    file_obj.seek(0)
    for chunk in file_obj.chunks():
        hash_obj.update(chunk)
    file_obj.seek(0)
    
    return hash_obj.hexdigest()


def format_file_size(size_bytes: int) -> str:
    """
    Formate une taille de fichier en format lisible.
    
    Args:
        size_bytes: Taille en octets
    
    Returns:
        Taille formatée (ex: "2.5 MB")
    """
    if size_bytes == 0:
        return "0 o"
    
    units = ['o', 'Ko', 'Mo', 'Go', 'To']
    size = float(size_bytes)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.1f} {units[unit_index]}"


def calculate_retention_date(years: int, from_date: Optional[datetime] = None) -> datetime:
    """
    Calcule la date de fin de rétention RGPD.
    
    Args:
        years: Nombre d'années de rétention
        from_date: Date de départ (défaut: maintenant)
    
    Returns:
        Date de fin de rétention
    """
    if from_date is None:
        from_date = timezone.now()
    
    return from_date + timedelta(days=365 * years)


def anonymize_string(value: str, visible_chars: int = 3) -> str:
    """
    Anonymise une chaîne en ne gardant que les premiers caractères visibles.
    
    Args:
        value: Chaîne à anonymiser
        visible_chars: Nombre de caractères visibles (défaut: 3)
    
    Returns:
        Chaîne anonymisée (ex: "123*******")
    """
    if not value or len(value) <= visible_chars:
        return "*" * len(value)
    
    return value[:visible_chars] + "*" * (len(value) - visible_chars)


def get_client_ip(request) -> Optional[str]:
    """
    Extrait l'adresse IP réelle du client (gestion proxy).
    
    Args:
        request: Objet Request Django
    
    Returns:
        Adresse IP du client
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    
    if x_forwarded_for:
        # Prendre la première IP (client réel)
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    return ip


def sanitize_filename(filename: str) -> str:
    """
    Nettoie un nom de fichier pour éviter les problèmes de sécurité.
    
    Args:
        filename: Nom de fichier original
    
    Returns:
        Nom de fichier sécurisé
    """
    import re
    from pathlib import Path
    
    # Garder seulement l'extension
    path = Path(filename)
    name = path.stem
    ext = path.suffix
    
    # Retirer les caractères dangereux
    name = re.sub(r'[^\w\s\-]', '', name)
    name = re.sub(r'[\s]+', '_', name)
    
    # Limiter la longueur
    if len(name) > 100:
        name = name[:100]
    
    return f"{name}{ext}"


def is_document_expired(retention_until: datetime) -> bool:
    """
    Vérifie si un document a dépassé sa période de rétention.
    
    Args:
        retention_until: Date limite de rétention
    
    Returns:
        True si le document est expiré
    """
    if not retention_until:
        return False
    
    return timezone.now().date() > retention_until


def mask_sensitive_data(data: dict, fields: list) -> dict:
    """
    Masque les champs sensibles dans un dictionnaire.
    
    Args:
        data: Dictionnaire de données
        fields: Liste des champs à masquer
    
    Returns:
        Dictionnaire avec champs masqués
    """
    masked_data = data.copy()
    
    for field in fields:
        if field in masked_data:
            masked_data[field] = "***MASKED***"
    
    return masked_data


def validate_gabon_business_hours(dt: datetime) -> bool:
    """
    Vérifie si une datetime est dans les heures ouvrables au Gabon.
    Lundi-Vendredi, 8h-17h (UTC+1)
    
    Args:
        dt: Datetime à vérifier
    
    Returns:
        True si dans les heures ouvrables
    """
    # Gabon est UTC+1
    local_dt = dt.astimezone(timezone.get_fixed_timezone(60))
    
    # Vérifier jour de semaine (0=Lundi, 6=Dimanche)
    if local_dt.weekday() >= 5:  # Samedi ou Dimanche
        return False
    
    # Vérifier heures (8h-17h)
    if local_dt.hour < 8 or local_dt.hour >= 17:
        return False
    
    return True


def generate_audit_context(request) -> dict:
    """
    Génère le contexte pour l'audit trail.
    
    Args:
        request: Objet Request Django
    
    Returns:
        Dictionnaire avec contexte d'audit
    """
    return {
        'ip_address': get_client_ip(request),
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'request_path': request.path,
        'request_method': request.method,
        'session_key': request.session.session_key if hasattr(request, 'session') else None,
    }


class FileNameGenerator:
    """Générateur de noms de fichiers sécurisés et uniques"""
    
    @staticmethod
    def generate(original_name: str, add_timestamp: bool = True) -> str:
        """
        Génère un nom de fichier unique.
        
        Args:
            original_name: Nom original du fichier
            add_timestamp: Ajouter un timestamp au nom
        
        Returns:
            Nom de fichier unique et sécurisé
        """
        from pathlib import Path
        import uuid
        
        path = Path(original_name)
        ext = path.suffix
        
        # Nom de base : UUID
        base_name = str(uuid.uuid4())
        
        if add_timestamp:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_name = f"{timestamp}_{base_name}"
        
        return f"{base_name}{ext}"