"""
Exceptions personnalisées pour GED Cabinet.
"""
from rest_framework.exceptions import APIException
from rest_framework import status


class GEDException(APIException):
    """Exception de base pour toute l'application GED"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Une erreur s'est produite"
    default_code = 'ged_error'


class DocumentIntegrityError(GEDException):
    """Levée quand l'intégrité d'un document est compromise"""
    status_code = status.HTTP_409_CONFLICT
    default_detail = "L'intégrité du document est compromise"
    default_code = 'document_integrity_error'


class DocumentVersionError(GEDException):
    """Erreur liée au versionnage de documents"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Erreur de versionnage du document"
    default_code = 'document_version_error'


class EncryptionError(GEDException):
    """Erreur lors du chiffrement/déchiffrement"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Erreur de chiffrement"
    default_code = 'encryption_error'


class RGPDViolationError(GEDException):
    """Levée lors d'une violation potentielle du RGPD"""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Action non autorisée (RGPD)"
    default_code = 'rgpd_violation'


class RetentionPeriodExpiredError(GEDException):
    """Document dont la période de rétention est expirée"""
    status_code = status.HTTP_410_GONE
    default_detail = "La période de rétention du document est expirée"
    default_code = 'retention_expired'


class PermissionDeniedError(GEDException):
    """Permission refusée pour cette action"""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Vous n'avez pas la permission d'effectuer cette action"
    default_code = 'permission_denied'


class DossierClosedError(GEDException):
    """Tentative de modification d'un dossier fermé/archivé"""
    status_code = status.HTTP_423_LOCKED
    default_detail = "Ce dossier est fermé et ne peut être modifié"
    default_code = 'dossier_closed'


class ValidationError(GEDException):
    """Erreur de validation métier"""
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Erreur de validation"
    default_code = 'validation_error'


class FileUploadError(GEDException):
    """Erreur lors de l'upload d'un fichier"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Erreur lors de l'upload du fichier"
    default_code = 'file_upload_error'


class FileSizeExceededError(FileUploadError):
    """Fichier trop volumineux"""
    default_detail = "Le fichier dépasse la taille maximale autorisée"
    default_code = 'file_size_exceeded'


class InvalidFileTypeError(FileUploadError):
    """Type de fichier non autorisé"""
    default_detail = "Ce type de fichier n'est pas autorisé"
    default_code = 'invalid_file_type'


class BackupError(GEDException):
    """Erreur lors d'un backup"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Erreur lors de la sauvegarde"
    default_code = 'backup_error'


class RestoreError(GEDException):
    """Erreur lors d'une restauration"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Erreur lors de la restauration"
    default_code = 'restore_error'


def custom_exception_handler(exc, context):
    """
    Handler d'exceptions personnalisé pour DRF.
    À configurer dans settings.py :
    REST_FRAMEWORK = {
        'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler'
    }
    """
    from rest_framework.views import exception_handler
    from rest_framework.response import Response
    
    # Appeler le handler par défaut de DRF
    response = exception_handler(exc, context)
    
    if response is not None:
        # Enrichir la réponse avec des informations supplémentaires
        custom_response_data = {
            'error': True,
            'status_code': response.status_code,
            'message': response.data.get('detail', str(exc)),
            'error_code': getattr(exc, 'default_code', 'error'),
        }
        
        # Ajouter les erreurs de validation si présentes
        if hasattr(response.data, 'items'):
            custom_response_data['validation_errors'] = {
                key: value for key, value in response.data.items() 
                if key != 'detail'
            }
        
        response.data = custom_response_data
    
    return response