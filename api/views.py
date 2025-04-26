from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from events.models import Event, Race, PenaltyType
from participants.models import Participant
from registrations.models import Registration, ParticipantAnnotation
from django.shortcuts import get_object_or_404
from django.utils import timezone

class EventViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Event.objects.all()

class RaceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Race.objects.all()

class ParticipantViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Participant.objects.all()

class AnnotationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            return ParticipantAnnotation.objects.filter(status=status_filter)
        return ParticipantAnnotation.objects.all()

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_participant(request, race_id):
    bib_number = request.query_params.get('bib_number', None)
    if not bib_number:
        return Response({'error': 'Bib number is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    race = get_object_or_404(Race, id=race_id)
    
    try:
        registration = Registration.objects.get(race=race, bib_number=bib_number)
        data = {
            'participant': {
                'id': registration.participant.id,
                'name': f"{registration.participant.first_name} {registration.participant.last_name}",
                'id_document': registration.participant.id_document,
            },
            'dog': {
                'id': registration.dog.id,
                'name': registration.dog.name,
                'breed': registration.dog.breed,
                'microchip': registration.dog.microchip_number,
            },
            'registration': {
                'id': registration.id,
                'bib_number': registration.bib_number,
                'category': registration.race_category.category.name,
                'payment_status': registration.payment_status,
                'ai_vaccine_status': registration.ai_vaccine_status,
                'vet_check_status': registration.vet_check_status,
                'kit_delivered': registration.kit_delivered,
                'checked_in': registration.checked_in,
            }
        }
        return Response(data)
    except Registration.DoesNotExist:
        return Response({'error': 'Participant not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_penalty_types(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    penalty_types = PenaltyType.objects.all()
    
    data = [
        {
            'id': penalty.id,
            'name': penalty.name,
            'description': penalty.description,
            'time_penalty': str(penalty.time_penalty) if penalty.time_penalty else None,
            'is_disqualification': penalty.is_disqualification,
        }
        for penalty in penalty_types
    ]
    
    return Response(data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_active_races(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    today = timezone.now().date()
    
    active_races = Race.objects.filter(event=event, race_date=today)
    
    data = [
        {
            'id': race.id,
            'name': race.name,
            'modality': race.modality.name,
            'distance': float(race.distance),
            'time': race.race_time.strftime('%H:%M'),
            'start_type': race.get_start_type_display(),
        }
        for race in active_races
    ]
    
    return Response(data)
