"""
Utilidades para enviar correos electrónicos en la aplicación Canicross.
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.urls import reverse
from utils.logger import get_logger, log_function_call, log_exception

logger = get_logger('emails')

@log_function_call(logger)
def send_registration_confirmation(registration):
    """
    Envía un correo electrónico de confirmación de inscripción al participante.
    
    Args:
        registration: La instancia de Registration para la que enviar la confirmación.
    
    Returns:
        bool: True si el correo se envió correctamente, False en caso contrario.
    """
    try:
        # Verificar que el participante tiene un correo electrónico
        if not registration.participant.user.email:
            logger.warning(f"No se puede enviar confirmación: el participante {registration.participant.id} no tiene email")
            return False
        
        # Preparar el contexto para la plantilla
        context = {
            'participant': registration.participant,
            'dog': registration.dog,
            'race': registration.race,
            'event': registration.race.event,
            'category': registration.race_category.category,
            'price': registration.race_category.price,
            'registration_date': registration.created_at,
            'registration_status': registration.get_registration_status_display(),
            'payment_status': registration.get_payment_status_display(),
        }
        
        # Construir el asunto del correo
        subject = f'Confirmación de inscripción - {registration.race.event.name}'
        
        # Renderizar el HTML desde la plantilla
        html_message = render_to_string('emails/registration_confirmation.html', context)
        
        # Versión de texto plano del mensaje
        plain_message = strip_tags(html_message)
        
        # Enviar el correo
        send_result = send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[registration.participant.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        if send_result:
            logger.info(f"Correo de confirmación enviado a {registration.participant.user.email} para la inscripción {registration.id}")
            return True
        else:
            logger.warning(f"Fallo al enviar correo de confirmación para la inscripción {registration.id}")
            return False
            
    except Exception as e:
        log_exception(logger, f"Error al enviar correo de confirmación para la inscripción {registration.id}")
        return False