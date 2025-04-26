from django.shortcuts import render, get_object_or_404
from events.models import Event, Race
from .models import RaceResult

def results_list(request):
    # Simple placeholder view
    events = Event.objects.filter(status__in=['in_progress', 'completed'])
    return render(request, 'results/results_list.html', {'events': events})

def event_results(request, event_slug):
    # Simple placeholder view
    event = get_object_or_404(Event, slug=event_slug)
    races = Race.objects.filter(event=event)
    return render(request, 'results/event_results.html', {'event': event, 'races': races})

def race_results(request, race_id):
    # Simple placeholder view
    race = get_object_or_404(Race, id=race_id)
    results = RaceResult.objects.filter(registration__race=race, status='finished').order_by('official_time')
    return render(request, 'results/race_results.html', {'race': race, 'results': results})
