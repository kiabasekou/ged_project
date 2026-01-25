"""
Tests unitaires pour l'application Core.
"""
from django.test import TestCase
from django.utils import timezone
from apps.core.utils import (
    generate_reference_code,
    generate_secure_token,
    format_file_size,
    anonymize_string,
    sanitize_filename,
    calculate_retention_date,
)
from apps.core.validators import (
    validate_ni_gabon,
    validate_nif_gabon,
    validate_phone_gabon,
    validate_retention_period,
)
from django.core.exceptions import ValidationError


class UtilsTestCase(TestCase):
    """Tests pour les fonctions utilitaires"""
    
    def test_generate_reference_code(self):
        """Test génération code de référence"""
        code = generate_reference_code('CAB', 2024, 1)
        self.assertEqual(code, 'CAB/2024/0001')
        
        code = generate_reference_code('PROC', 2024, 999)
        self.assertEqual(code, 'PROC/2024/0999')
    
    def test_generate_secure_token(self):
        """Test génération token sécurisé"""
        token1 = generate_secure_token(32)
        token2 = generate_secure_token(32)
        
        # Les tokens doivent être différents
        self.assertNotEqual(token1, token2)
        
        # Longueur approximative (base64 encode)
        self.assertGreater(len(token1), 30)
    
    def test_format_file_size(self):
        """Test formatage taille fichier"""
        self.assertEqual(format_file_size(0), "0 o")
        self.assertEqual(format_file_size(500), "500.0 o")
        self.assertEqual(format_file_size(1024), "1.0 Ko")
        self.assertEqual(format_file_size(1024 * 1024), "1.0 Mo")
        self.assertEqual(format_file_size(1536 * 1024), "1.5 Mo")
    
    def test_anonymize_string(self):
        """Test anonymisation de chaîne"""
        self.assertEqual(anonymize_string("1234567890", 3), "123*******")
        self.assertEqual(anonymize_string("ABC", 3), "***")
        self.assertEqual(anonymize_string("", 3), "")
    
    def test_sanitize_filename(self):
        """Test nettoyage nom de fichier"""
        self.assertEqual(
            sanitize_filename("document <script>.pdf"),
            "document_script.pdf"
        )
        self.assertEqual(
            sanitize_filename("mon fichier  test.docx"),
            "mon_fichier_test.docx"
        )
    
    def test_calculate_retention_date(self):
        """Test calcul date de rétention"""
        from datetime import timedelta
        
        now = timezone.now()
        retention_date = calculate_retention_date(10, now)
        
        # Devrait être environ 10 ans dans le futur
        delta = retention_date - now
        self.assertGreater(delta.days, 3650)  # ~10 ans
        self.assertLess(delta.days, 3660)


class ValidatorsTestCase(TestCase):
    """Tests pour les validators"""
    
    def test_validate_ni_gabon_valid(self):
        """Test validation NI valide"""
        try:
            validate_ni_gabon("1234567890")
        except ValidationError:
            self.fail("NI valide rejeté")
    
    def test_validate_ni_gabon_invalid(self):
        """Test validation NI invalide"""
        with self.assertRaises(ValidationError):
            validate_ni_gabon("12345")  # Trop court
        
        with self.assertRaises(ValidationError):
            validate_ni_gabon("12345678901")  # Trop long
        
        with self.assertRaises(ValidationError):
            validate_ni_gabon("123456789A")  # Contient lettre
    
    def test_validate_nif_gabon_valid(self):
        """Test validation NIF valide"""
        try:
            validate_nif_gabon("123456789")  # 9 chiffres
            validate_nif_gabon("1234567890")  # 10 chiffres
        except ValidationError:
            self.fail("NIF valide rejeté")
    
    def test_validate_nif_gabon_invalid(self):
        """Test validation NIF invalide"""
        with self.assertRaises(ValidationError):
            validate_nif_gabon("12345")  # Trop court
        
        with self.assertRaises(ValidationError):
            validate_nif_gabon("12345678901")  # Trop long
    
    def test_validate_phone_gabon_valid(self):
        """Test validation téléphone valide"""
        try:
            validate_phone_gabon("+24177123456")
            validate_phone_gabon("077123456")
            validate_phone_gabon("0077123456")
        except ValidationError:
            self.fail("Numéro valide rejeté")
    
    def test_validate_phone_gabon_invalid(self):
        """Test validation téléphone invalide"""
        with self.assertRaises(ValidationError):
            validate_phone_gabon("123")  # Trop court
        
        with self.assertRaises(ValidationError):
            validate_phone_gabon("+33612345678")  # Mauvais indicatif
    
    def test_validate_retention_period_valid(self):
        """Test validation période de rétention valide"""
        try:
            validate_retention_period(1)
            validate_retention_period(10)
            validate_retention_period(99)
        except ValidationError:
            self.fail("Période valide rejetée")
    
    def test_validate_retention_period_invalid(self):
        """Test validation période de rétention invalide"""
        with self.assertRaises(ValidationError):
            validate_retention_period(0)  # Trop court
        
        with self.assertRaises(ValidationError):
            validate_retention_period(100)  # Trop long


class BaseModelTestCase(TestCase):
    """Tests pour BaseModel"""
    
    def setUp(self):
        """Créer un modèle de test utilisant BaseModel"""
        from apps.core.models import BaseModel
        from django.db import models
        
        class TestModel(BaseModel):
            name = models.CharField(max_length=100)
            
            class Meta:
                app_label = 'core'
        
        self.TestModel = TestModel
    
    def test_base_model_has_uuid(self):
        """Test que BaseModel génère un UUID"""
        instance = self.TestModel(name="Test")
        self.assertIsNotNone(instance.id)
    
    def test_soft_delete(self):
        """Test du soft delete"""
        instance = self.TestModel.objects.create(name="Test")
        self.assertTrue(instance.is_active)
        
        instance.soft_delete()
        self.assertFalse(instance.is_active)
        
        # L'objet existe toujours en DB
        self.assertTrue(
            self.TestModel.objects.filter(id=instance.id).exists()
        )
    
    def test_restore(self):
        """Test de la restauration"""
        instance = self.TestModel.objects.create(name="Test")
        instance.soft_delete()
        self.assertFalse(instance.is_active)
        
        instance.restore()
        self.assertTrue(instance.is_active)


class ExceptionsTestCase(TestCase):
    """Tests pour les exceptions personnalisées"""
    
    def test_ged_exception_status_code(self):
        """Test que les exceptions ont le bon status code"""
        from apps.core.exceptions import (
            DocumentIntegrityError,
            PermissionDeniedError,
            FileSizeExceededError,
        )
        
        self.assertEqual(DocumentIntegrityError.status_code, 409)
        self.assertEqual(PermissionDeniedError.status_code, 403)
        self.assertEqual(FileSizeExceededError.status_code, 400)
    
    def test_exception_messages(self):
        """Test que les exceptions ont des messages clairs"""
        from apps.core.exceptions import DocumentVersionError
        
        exc = DocumentVersionError()
        self.assertIn('versionnage', exc.default_detail.lower())


class PermissionsTestCase(TestCase):
    """Tests pour les permissions personnalisées"""
    
    def setUp(self):
        """Créer des utilisateurs de test"""
        from apps.users.models import User
        
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        
        self.normal_user = User.objects.create_user(
            username='user',
            email='user@test.com',
            password='user123'
        )
    
    def test_superuser_has_all_permissions(self):
        """Test que le superuser a toutes les permissions"""
        from apps.core.permissions import IsOwnerOrReadOnly
        from unittest.mock import Mock
        
        permission = IsOwnerOrReadOnly()
        request = Mock()
        request.user = self.superuser
        request.method = 'POST'
        
        obj = Mock()
        obj.created_by = self.normal_user
        
        self.assertTrue(
            permission.has_object_permission(request, None, obj)
        )