from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from registrations.models import Registration
from django.utils import timezone

@login_required
def checkin_dashboard(request):
    # Simple placeholder view
    # In a real implementation, would filter by appropriate event/race
    eligible_registrations = Registration.objects.filter(
        payment_status='paid',
        kit_delivered=True,
        vet_check_status='approved',
        checked_in=False
    )
    return render(request, 'checkin/dashboard.html', {'registrations': eligible_registrations})

@login_required
def activate_participant(request, registration_id):
    # Simple placeholder view
    registration = get_object_or_404(Registration, id=registration_id)
    
    if request.method == 'POST':
        if registration.kit_delivered and registration.vet_check_status == 'approved':
            registration.checked_in = True
            registration.checkin_time = timezone.now()
            registration.save()
        
        return redirect('checkin:dashboard')
    
    return render(request, 'checkin/activate.html', {'registration': registration})
