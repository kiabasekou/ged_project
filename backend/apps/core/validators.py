"""
Validators personnalisés pour l'application GED Cabinet.
"""
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_ni_gabon(value):
    """
    Valide le format du Numéro d'Identification (NI) gabonais.
    Format attendu : XXXXXXXXXX (10 chiffres)
    """
    if not value:
        return
    
    pattern = r'^\d{10}$'
    if not re.match(pattern, value):
        raise ValidationError(
            _("Le NI doit contenir exactement 10 chiffres."),
            code='invalid_ni'
        )


def validate_nif_gabon(value):
    """
    Valide le format du Numéro d'Identification Fiscale (NIF) gabonais.
    Format attendu : XXXXXXXXX (9 chiffres) ou XXXXXXXXXX (10 chiffres)
    """
    if not value:
        return
    
    pattern = r'^\d{9,10}$'
    if not re.match(pattern, value):
        raise ValidationError(
            _("Le NIF doit contenir 9 ou 10 chiffres."),
            code='invalid_nif'
        )


def validate_rccm_gabon(value):
    """
    Valide le format du RCCM gabonais (Registre de Commerce et du Crédit Mobilier).
    Format : LBV/XXXX/X/X/XXXXX
    """
    if not value:
        return
    
    # Pattern flexible pour RCCM
    pattern = r'^[A-Z]{2,3}\/\d{4}\/[A-Z]\/[A-Z]\/\d{4,6}$'
    if not re.match(pattern, value.upper()):
        raise ValidationError(
            _("Format RCCM invalide. Exemple : LBV/2024/B/N/12345"),
            code='invalid_rccm'
        )


def validate_phone_gabon(value):
    """
    Valide le format du numéro de téléphone gabonais.
    Formats acceptés :
    - +241XXXXXXXXX (indicatif international)
    - 0XXXXXXXXX (format local avec 0)
    - XXXXXXXXX (format local sans 0)
    """
    if not value:
        return
    
    # Nettoyer le numéro (retirer espaces, tirets, etc.)
    cleaned = re.sub(r'[\s\-\(\)]', '', value)
    
    patterns = [
        r'^\+241\d{8,9}$',  # Format international
        r'^0\d{8,9}$',       # Format local avec 0
        r'^\d{8,9}$',        # Format local sans 0
    ]
    
    if not any(re.match(pattern, cleaned) for pattern in patterns):
        raise ValidationError(
            _("Numéro de téléphone invalide. Formats acceptés : +241XXXXXXXX, 0XXXXXXXX"),
            code='invalid_phone'
        )


def validate_file_size(file):
    """
    Valide la taille d'un fichier uploadé.
    Limite : 100 MB par défaut (configurable via settings)
    """
    from django.conf import settings
    
    max_size = getattr(settings, 'MAX_UPLOAD_SIZE_MB', 100) * 1024 * 1024
    
    if file.size > max_size:
        raise ValidationError(
            _(f"Le fichier est trop volumineux. Taille maximale : {max_size / (1024 * 1024):.0f} MB"),
            code='file_too_large'
        )


def validate_file_extension(value):
    """
    Valide l'extension du fichier uploadé.
    Extensions autorisées définies dans settings.ALLOWED_FILE_EXTENSIONS
    """
    from django.conf import settings
    import os
    
    ext = os.path.splitext(value.name)[1].lower()
    
    allowed_extensions = getattr(settings, 'ALLOWED_FILE_EXTENSIONS', [
        '.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt',
        '.txt', '.rtf', '.odt', '.ods', '.odp',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
        '.zip', '.rar', '.7z', '.msg', '.eml'
    ])
    
    if ext not in allowed_extensions:
        raise ValidationError(
            _(f"Extension de fichier non autorisée. Extensions acceptées : {', '.join(allowed_extensions)}"),
            code='invalid_file_extension'
        )


def validate_retention_period(value):
    """
    Valide la période de rétention (en années).
    Minimum 1 an, maximum 99 ans.
    """
    if value < 1:
        raise ValidationError(
            _("La période de rétention doit être d'au moins 1 an."),
            code='retention_too_short'
        )
    
    if value > 99:
        raise ValidationError(
            _("La période de rétention ne peut excéder 99 ans."),
            code='retention_too_long'
        )


def validate_professional_id(value):
    """
    Valide l'identifiant professionnel (avocat, notaire, etc.).
    Format libre mais requis non-vide pour les professionnels.
    """
    if not value or not value.strip():
        raise ValidationError(
            _("L'identifiant professionnel est requis."),
            code='professional_id_required'
        )
    
    if len(value) < 3:
        raise ValidationError(
            _("L'identifiant professionnel doit contenir au moins 3 caractères."),
            code='professional_id_too_short'
        )


def validate_reference_code(value):
    """
    Valide le code de référence d'un dossier.
    Format : XXXX/YYYY/NNNN
    Exemple : CAB/2024/0001
    """
    if not value:
        return
    
    pattern = r'^[A-Z]{2,5}\/\d{4}\/\d{4,6}$'
    if not re.match(pattern, value.upper()):
        raise ValidationError(
            _("Format de code de référence invalide. Exemple : CAB/2024/0001"),
            code='invalid_reference_code'
        )


def validate_email_domain(value):
    """
    Valide que l'email provient d'un domaine autorisé.
    Utile pour restreindre les inscriptions aux emails professionnels.
    """
    from django.conf import settings
    
    allowed_domains = getattr(settings, 'ALLOWED_EMAIL_DOMAINS', None)
    
    if allowed_domains:
        domain = value.split('@')[-1].lower()
        if domain not in allowed_domains:
            raise ValidationError(
                _(f"Seuls les emails des domaines suivants sont autorisés : {', '.join(allowed_domains)}"),
                code='invalid_email_domain'
            )


def validate_no_special_chars(value):
    """
    Valide qu'une chaîne ne contient pas de caractères spéciaux dangereux.
    Prévention d'injections.
    """
    if not value:
        return
    
    # Caractères interdits
    forbidden = ['<', '>', '"', "'", ';', '&', '|', '`', '$']
    
    for char in forbidden:
        if char in value:
            raise ValidationError(
                _(f"Caractères spéciaux interdits détectés : {char}"),
                code='forbidden_characters'
            )


def validate_future_date(value):
    """Valide qu'une date est dans le futur"""
    from django.utils import timezone
    
    if value <= timezone.now().date():
        raise ValidationError(
            _("La date doit être dans le futur."),
            code='date_not_future'
        )


def validate_past_date(value):
    """Valide qu'une date est dans le passé"""
    from django.utils import timezone
    
    if value >= timezone.now().date():
        raise ValidationError(
            _("La date doit être dans le passé."),
            code='date_not_past'
        )