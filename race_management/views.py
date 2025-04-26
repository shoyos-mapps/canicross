from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from events.models import Race
from registrations.models import Registration
from results.models import RaceResult
from django.utils import timezone

@login_required
def race_dashboard(request):
    # Simple placeholder view
    active_races = Race.objects.filter(race_date=timezone.now().date())
    return render(request, 'race_management/dashboard.html', {'races': active_races})

@login_required
def start_race(request, race_id):
    # Simple placeholder view
    race = get_object_or_404(Race, id=race_id)
    
    if request.method == 'POST':
        race.actual_start_time = timezone.now()
        race.save()
        
        # Create result entries for all checked-in participants
        checked_in_registrations = Registration.objects.filter(
            race=race,
            checked_in=True
        )
        
        for registration in checked_in_registrations:
            # Create or update the result
            result, created = RaceResult.objects.get_or_create(
                registration=registration,
                defaults={
                    'start_time': race.actual_start_time,
                    'status': 'in_progress'
                }
            )
            
            if not created:
                result.start_time = race.actual_start_time
                result.status = 'in_progress'
                result.save()
        
        return redirect('race_management:dashboard')
    
    return render(request, 'race_management/start_race.html', {'race': race})

@login_required
def finish_participant(request, race_id):
    # Simple placeholder view
    race = get_object_or_404(Race, id=race_id)
    
    if request.method == 'POST':
        bib_number = request.POST.get('bib_number')
        
        try:
            registration = Registration.objects.get(race=race, bib_number=bib_number)
            result, created = RaceResult.objects.get_or_create(
                registration=registration,
                defaults={'status': 'finished'}
            )
            
            result.finish_time = timezone.now()
            result.status = 'finished'
            
            # Calculate time
            if race.actual_start_time and result.finish_time:
                result.base_time = result.finish_time - race.actual_start_time
                result.official_time = result.base_time  # Will be adjusted for penalties later
            
            result.save()
            
        except Registration.DoesNotExist:
            # Handle error - bib not found
            pass
        
        return redirect('race_management:dashboard')
    
    return render(request, 'race_management/finish_participant.html', {'race': race})
