from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from registrations.models import Registration
from django.utils import timezone

@login_required
def veterinary_dashboard(request):
    # Simple placeholder view
    # In a real implementation, would filter by appropriate event/race
    pending_registrations = Registration.objects.filter(vet_check_status='pending')
    return render(request, 'veterinary/dashboard.html', {'registrations': pending_registrations})

@login_required
def veterinary_approval(request, registration_id):
    # Simple placeholder view
    registration = get_object_or_404(Registration, id=registration_id)
    
    if request.method == 'POST':
        approved = request.POST.get('approved') == 'yes'
        notes = request.POST.get('notes', '')
        
        registration.vet_check_status = 'approved' if approved else 'rejected'
        registration.vet_check_time = timezone.now()
        registration.vet_checker_details = notes
        registration.save()
        
        return redirect('veterinary:dashboard')
    
    return render(request, 'veterinary/approval.html', {'registration': registration})
