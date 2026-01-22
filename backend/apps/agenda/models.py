# backend/apps/agenda/models.py

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.dossiers.models import Dossier  # Optionnel : lien avec dossier

User = get_user_model()

class Event(models.Model):
    """
    Événement calendrier du cabinet : audience, RDV, formalité, congé...
    Indépendant ou lié à un dossier.
    """
    class EventType(models.TextChoices):
        AUDIENCE = 'AUDIENCE', _("Audience / Plaidoirie")
        RDV = 'RDV', _("Rendez-vous client")
        FORMALITE = 'FORMALITE', _("Formalité notariale")
        CONGE = 'CONGE', _("Congé / Absence")
        AUTRE = 'AUTRE', _("Autre événement")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=255, verbose_name=_("Titre"))
    type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        default=EventType.AUTRE,
        verbose_name=_("Type d'événement")
    )

    start_date = models.DateField(verbose_name=_("Date de début"))
    start_time = models.TimeField(null=True, blank=True, verbose_name=_("Heure de début"))
    all_day = models.BooleanField(default=True, verbose_name=_("Journée entière"))

    end_date = models.DateField(null=True, blank=True, verbose_name=_("Date de fin"))
    end_time = models.TimeField(null=True, blank=True, verbose_name=_("Heure de fin"))

    location = models.CharField(max_length=255, blank=True, verbose_name=_("Lieu"))
    description = models.TextField(blank=True, verbose_name=_("Description / Notes"))

    # Lien optionnel avec un dossier
    dossier = models.ForeignKey(
        'dossiers.Dossier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events',
        verbose_name=_("Dossier lié")
    )

    # Créé par
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_events',
        verbose_name=_("Créé par")
    )

    created_at = models.DateTimeField(default=timezone.now, verbose_name=_("Créé le"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

    class Meta:
        verbose_name = _("Événement calendrier")
        verbose_name_plural = _("Événements calendrier")
        ordering = ['-start_date', '-start_time']
        indexes = [
            models.Index(fields=['start_date']),
            models.Index(fields=['type']),
            models.Index(fields=['dossier']),
        ]

    def __str__(self):
        return f"{self.get_type_display()} : {self.title} ({self.start_date})"

    @property
    def is_overdue(self):
        """Pour compatibilité avec les dossiers en retard"""
        if not self.start_date:
            return False
        return timezone.now().date() > self.start_date

    @property
    def color(self):
        """Couleur pour FullCalendar"""
        colors = {
            self.EventType.AUDIENCE: '#D32F2F',
            self.EventType.RDV: '#1A237E',
            self.EventType.FORMALITE: '#FF8F00',
            self.EventType.CONGE: '#616161',
            self.EventType.AUTRE: '#1976D2',
        }
        return colors.get(self.type, '#1976D2')