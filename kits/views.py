from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from registrations.models import Registration
from django.utils import timezone

@login_required
def kit_dashboard(request):
    # Simple placeholder view
    # In a real implementation, would filter by appropriate event/race
    pending_kits = Registration.objects.filter(payment_status='paid', kit_delivered=False)
    return render(request, 'kits/dashboard.html', {'registrations': pending_kits})

@login_required
def deliver_kit(request, registration_id):
    # Simple placeholder view
    registration = get_object_or_404(Registration, id=registration_id)
    
    if request.method == 'POST':
        registration.kit_delivered = True
        registration.kit_delivery_time = timezone.now()
        registration.save()
        
        return redirect('kits:dashboard')
    
    return render(request, 'kits/deliver.html', {'registration': registration})
