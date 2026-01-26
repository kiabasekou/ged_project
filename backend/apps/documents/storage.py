"""
Système de stockage chiffré pour documents sensibles du cabinet.
Conforme aux exigences de confidentialité et RGPD.
"""
import os
import secrets
import hashlib
from pathlib import Path
from typing import Optional

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files.base import File, ContentFile
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptedFileStorage(FileSystemStorage):
    """
    Stockage chiffré AES-256 avec noms de fichiers aléatoires.
    Garantit la confidentialité même en cas d'accès physique au serveur.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cipher = self._get_cipher()
    
    def _get_cipher(self) -> Fernet:
        """Initialise le chiffrement AES-256 via Fernet"""
        encryption_key = getattr(settings, 'FILE_ENCRYPTION_KEY', None)
        
        if not encryption_key:
            raise ValueError(
                "FILE_ENCRYPTION_KEY manquante dans settings. "
                "Générez-la avec: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
            )
        
        # Validation et conversion de la clé
        try:
            # Si c'est une string, encoder en bytes
            if isinstance(encryption_key, str):
                key_bytes = encryption_key.encode('utf-8')
            else:
                key_bytes = encryption_key
            
            # Tentative de création du cipher pour valider la clé
            return Fernet(key_bytes)
            
        except Exception as e:
            raise ValueError(
                f"FILE_ENCRYPTION_KEY invalide: {str(e)}\n"
                "La clé doit être 32 bytes encodés en base64 URL-safe.\n"
                "Générez une clé valide avec:\n"
                "  python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"\n"
                "Puis ajoutez-la dans votre fichier .env:\n"
                "  FILE_ENCRYPTION_KEY=votre_clé_générée"
            )
    
    def _generate_secure_filename(self, original_name: str) -> str:
        """
        Génère un nom de fichier sécurisé et non-prévisible.
        Format: {hash_partiel}/{token_aléatoire}.enc
        """
        # Hash partiel du nom original (pour debugging uniquement)
        name_hash = hashlib.sha256(original_name.encode()).hexdigest()[:8]
        
        # Token cryptographiquement sécurisé
        random_token = secrets.token_urlsafe(32)
        
        # Structure: premier_niveau/second_niveau/fichier.enc
        # Permet distribution équilibrée (évite trop de fichiers dans un dossier)
        first_level = name_hash[:2]
        second_level = name_hash[2:4]
        
        return f"{first_level}/{second_level}/{random_token}.enc"
    
    def _save(self, name: str, content: File) -> str:
        """
        Sauvegarde le fichier après chiffrement.
        
        Args:
            name: Nom original du fichier
            content: Contenu du fichier
            
        Returns:
            Chemin du fichier chiffré sauvegardé
        """
        # Lecture du contenu
        content.seek(0)
        file_data = content.read()
        
        # Chiffrement AES-256
        encrypted_data = self.cipher.encrypt(file_data)
        
        # Génération du nom sécurisé
        secure_name = self._generate_secure_filename(name)
        
        # Création du répertoire si nécessaire
        full_path = self.path(secure_name)
        directory = os.path.dirname(full_path)
        os.makedirs(directory, exist_ok=True)
        
        # Sauvegarde du fichier chiffré
        encrypted_file = ContentFile(encrypted_data)
        return super()._save(secure_name, encrypted_file)
    
    def _open(self, name: str, mode: str = 'rb') -> File:
        """
        Ouvre et déchiffre un fichier.
        
        Args:
            name: Chemin du fichier chiffré
            mode: Mode d'ouverture (lecture binaire par défaut)
            
        Returns:
            Fichier déchiffré
        """
        # Lecture du fichier chiffré
        encrypted_file = super()._open(name, mode)
        encrypted_data = encrypted_file.read()
        encrypted_file.close()
        
        # Déchiffrement
        try:
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return ContentFile(decrypted_data)
        except Exception as e:
            raise ValueError(f"Échec du déchiffrement du fichier {name}: {str(e)}")
    
    def get_available_name(self, name: str, max_length: Optional[int] = None) -> str:
        """
        Surcharge pour éviter les collisions de noms.
        Les noms étant aléatoires, collision quasi-impossible.
        """
        return self._generate_secure_filename(name)
    
    def verify_integrity(self, name: str, expected_hash: str) -> bool:
        """
        Vérifie l'intégrité d'un fichier via son hash SHA-256.
        
        Args:
            name: Chemin du fichier
            expected_hash: Hash SHA-256 attendu
            
        Returns:
            True si l'intégrité est vérifiée
        """
        try:
            file_obj = self._open(name)
            file_data = file_obj.read()
            file_obj.close()
            
            actual_hash = hashlib.sha256(file_data).hexdigest()
            return actual_hash == expected_hash
            
        except Exception:
            return False


class AuditedFileStorage(EncryptedFileStorage):
    """
    Extension du stockage chiffré avec audit automatique des accès.
    Chaque lecture/écriture est tracée dans AuditLog.
    """
    
    def _log_access(self, action: str, file_path: str, user=None):
        """
        Enregistre un accès fichier dans l'audit trail.
        
        Args:
            action: Type d'action (READ, WRITE, DELETE)
            file_path: Chemin du fichier accédé
            user: Utilisateur effectuant l'action
        """
        from apps.audit.models import AuditLog
        from django.contrib.contenttypes.models import ContentType
        
        try:
            AuditLog.objects.create(
                user=user,
                action_type='FILE_ACCESS',
                description=f"{action} - {file_path}",
                changes={'action': action, 'path': file_path}
            )
        except Exception:
            # Ne pas bloquer les opérations si l'audit échoue
            pass
    
    def _save(self, name: str, content: File) -> str:
        """Sauvegarde avec log d'audit"""
        result = super()._save(name, content)
        self._log_access('WRITE', result)
        return result
    
    def _open(self, name: str, mode: str = 'rb') -> File:
        """Ouverture avec log d'audit"""
        self._log_access('READ', name)
        return super()._open(name, mode)
    
    def delete(self, name: str):
        """Suppression avec log d'audit"""
        self._log_access('DELETE', name)
        return super().delete(name)