import uuid
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.agenda.models import Event
from apps.dossiers.models import Dossier
from apps.clients.models import Client # Importation du modèle Client
from datetime import date

User = get_user_model()

class EventModelTest(TestCase):
    def setUp(self):
        # 1. Création de l'utilisateur (avec matricule pro obligatoire)
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='AVOCAT',
            professional_id='TEST/2026/001'
        )
        
        # 2. Création d'un client réel (avec téléphone obligatoire pour le Gabon)
        self.client_obj = Client.objects.create(
            client_type='PHYSIQUE',
            first_name='Paul',
            last_name='Biyoghe',
            phone_primary='+24177000001',
            city='Libreville'
        )

        # 3. Création du dossier lié au vrai client
        self.dossier = Dossier.objects.create(
            title="Test Dossier",
            reference_code="GAB-2026-9999",
            client=self.client_obj, # On passe l'objet client créé ci-dessus
            responsible=self.user,
            category='CONTENTIEUX'
        )

    def test_event_creation(self):
        event = Event.objects.create(
            title="Audience Tribunal",
            type='AUDIENCE',
            start_date=date.today(),
            all_day=True,
            created_by=self.user,
            dossier=self.dossier
        )
        self.assertEqual(event.title, "Audience Tribunal")
        self.assertEqual(event.type, "AUDIENCE")

    def test_event_color_property(self):
        event = Event.objects.create(
            title="Test",
            type='CONGE',
            start_date=date.today(),
            created_by=self.user
        )
        self.assertEqual(event.color, '#616161')


class EventAPITest(APITestCase):
    def setUp(self):
        # Utilisateur pour l'API
        self.user = User.objects.create_user(
            username='apiuser',
            password='apipass123',
            role='AVOCAT',
            professional_id='API/2026/002'
        )
        self.client.force_authenticate(user=self.user)

        # Client pour l'API
        self.client_obj = Client.objects.create(
            client_type='MORALE',
            company_name='Test SARL',
            rccm='LBV/2026/B/0000',
            nif='2026000000',
            phone_primary='+24166000002'
        )

        # Dossier pour l'API
        self.dossier = Dossier.objects.create(
            title="API Dossier",
            reference_code="API-2026-0001",
            client=self.client_obj,
            responsible=self.user,
            category='IMMOBILIER'
        )

        self.event_data = {
            "title": "Rendez-vous client",
            "type": "RDV",
            "start_date": "2026-02-01",
            "all_day": True,
            "location": "Cabinet",
            "dossier": str(self.dossier.id)
        }

    def test_create_event(self):
        url = reverse('event-list')
        response = self.client.post(url, self.event_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_events(self):
        Event.objects.create(
            title="Test Event",
            type='FORMALITE',
            start_date=date.today(),
            created_by=self.user
        )
        url = reverse('event-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_calendar_endpoint(self):
        Event.objects.create(
            title="Audience test",
            type='AUDIENCE',
            start_date=date(2026, 1, 25),
            created_by=self.user
        )
        url = reverse('event-calendar')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)