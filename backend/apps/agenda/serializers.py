# ============================================================================
# CORRECTION : backend/apps/agenda/serializers.py
# À copier dans votre fichier backend/apps/agenda/serializers.py
# ============================================================================

from rest_framework import serializers
from .models import Event
from apps.dossiers.serializers import DossierListSerializer
from apps.users.serializers import UserMinimalSerializer
from apps.dossiers.models import Dossier

class EventSerializer(serializers.ModelSerializer):
    """
    Serializer complet pour les événements de l'agenda
    Gère la création, modification et lecture des événements
    """
    created_by = UserMinimalSerializer(read_only=True)
    
    # Pour la lecture : informations complètes du dossier
    dossier_info = DossierListSerializer(source='dossier', read_only=True)
    
    # Pour l'écriture : UUID du dossier
    dossier = serializers.PrimaryKeyRelatedField(
        queryset=Dossier.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    
    # Propriété calculée depuis le modèle
    color = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = [
            'id', 
            'title', 
            'type', 
            'start_date', 
            'start_time', 
            'all_day',
            'end_date', 
            'end_time', 
            'location', 
            'description',
            'dossier',        # Write-only (UUID)
            'dossier_info',   # Read-only (objet complet)
            'priority',       # AJOUTÉ
            'reminder',       # AJOUTÉ
            'created_by', 
            'created_at', 
            'updated_at', 
            'color'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at', 'color']

    def create(self, validated_data):
        """
        Injection automatique de l'utilisateur connecté
        """
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate(self, data):
        """
        Validations métier
        """
        # Si pas toute la journée, les horaires sont obligatoires
        if not data.get('all_day', False):
            if not data.get('start_time'):
                raise serializers.ValidationError({
                    'start_time': 'L\'heure de début est obligatoire pour un événement non journée entière'
                })
            if not data.get('end_time'):
                raise serializers.ValidationError({
                    'end_time': 'L\'heure de fin est obligatoire pour un événement non journée entière'
                })
                
            # Vérifier que end_time > start_time
            if data['end_time'] <= data['start_time']:
                raise serializers.ValidationError({
                    'end_time': 'L\'heure de fin doit être après l\'heure de début'
                })
        
        return data