# backend/apps/agenda/views.py

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Event
from .serializers import EventSerializer
from apps.audit.utils import log_action

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Event.objects.select_related('dossier', 'created_by')

    def perform_create(self, serializer):
        event = serializer.save()
        log_action(
            user=self.request.user,
            obj=event,
            action='CREATE',
            description=f"Création événement : {event.title}",
            request=self.request
        )

    def perform_update(self, serializer):
        event = serializer.save()
        log_action(
            user=self.request.user,
            obj=event,
            action='UPDATE',
            description=f"Modification événement : {event.title}",
            request=self.request
        )

    def perform_destroy(self, instance):
        log_action(
            user=self.request.user,
            obj=instance,
            action='DELETE',
            description=f"Suppression événement : {instance.title}",
            request=self.request
        )
        instance.delete()

    @action(detail=False, methods=['get'])
    def calendar(self, request):
        """Endpoint optimisé pour FullCalendar"""
        start = request.query_params.get('start')
        end = request.query_params.get('end')

        qs = self.get_queryset()
        if start:
            qs = qs.filter(start_date__gte=start)
        if end:
            qs = qs.filter(start_date__lte=end)

        events = qs.values(
            'id', 'title', 'type', 'start_date', 'start_time', 'all_day',
            'location', 'description', 'dossier_id'
        )

        formatted_events = []
        for e in events:
            start_str = str(e['start_date'])
            if e['start_time'] and not e['all_day']:
                start_str += f"T{e['start_time']}"

            formatted_events.append({
                'id': e['id'],
                'title': e['title'],
                'start': start_str,
                'allDay': e['all_day'],
                'backgroundColor': Event.objects.get(id=e['id']).color,
                'extendedProps': {
                    'type': e['type'],
                    'location': e['location'],
                    'description': e['description'],
                    'dossier': e['dossier_id']
                }
            })

        return Response(formatted_events)