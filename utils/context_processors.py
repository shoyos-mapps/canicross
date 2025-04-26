"""
Context processors for the canicross_project.
"""
from django.conf import settings

def session_timeout(request):
    """
    Adds session timeout minutes to the context.
    """
    # Get session timeout from settings (default 30)
    timeout_minutes = getattr(settings, 'SESSION_TIMEOUT_MINUTES', 30)
    return {
        'session_timeout_minutes': timeout_minutes
    }