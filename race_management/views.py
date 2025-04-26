from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from events.models import Race
from registrations.models import Registration
from results.models import Result
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
            result, created = Result.objects.get_or_create(
                registration=registration,
                defaults={
                    'status': 'draft',
                    'recorded_by': request.user
                }
            )
            
            if not created:
                result.status = 'draft'
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
            result, created = Result.objects.get_or_create(
                registration=registration,
                defaults={
                    'status': 'pending', 
                    'recorded_by': request.user,
                    'recorded_at': timezone.now()
                }
            )
            
            result.status = 'pending'
            
            # Calculate time difference in seconds from race start
            if race.actual_start_time:
                now = timezone.now()
                time_diff = (now - race.actual_start_time).total_seconds()
                result.official_time_seconds = int(time_diff)
            
            result.save()
            
        except Registration.DoesNotExist:
            # Handle error - bib not found
            pass
        
        return redirect('race_management:dashboard')
    
    return render(request, 'race_management/finish_participant.html', {'race': race})
