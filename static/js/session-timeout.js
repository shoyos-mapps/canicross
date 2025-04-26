/**
 * Controlador de tiempo de inactividad de sesión
 * Cierra la sesión automáticamente después de un período de inactividad sin mostrar advertencia
 */
document.addEventListener('DOMContentLoaded', function() {
    // Obtener el tiempo de inactividad desde el meta tag
    const timeoutMinutes = parseInt(document.querySelector('meta[name="session-timeout-minutes"]').getAttribute('content'));
    
    // Convertir minutos a milisegundos
    const timeoutMilliseconds = timeoutMinutes * 60 * 1000;
    
    // Variables para el temporizador
    let timeoutId;
    let lastActivityTime = new Date().getTime();
    
    // Función para reiniciar el temporizador de inactividad
    function resetInactivityTimer() {
        // Actualizar el tiempo de la última actividad
        lastActivityTime = new Date().getTime();
        
        // Limpiar el temporizador existente
        clearTimeout(timeoutId);
        
        // Establecer un nuevo temporizador que cierra la sesión después del tiempo de inactividad
        timeoutId = setTimeout(logoutUser, timeoutMilliseconds);
    }
    
    // Función para cerrar sesión
    function logoutUser() {
        console.log("Sesión expirada por inactividad");
        window.location.href = '/accounts/logout/?next=/events/';
    }
    
    // Obtener el token CSRF
    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }
    
    // Eventos para reiniciar el temporizador cuando el usuario está activo
    document.addEventListener('mousemove', resetInactivityTimer);
    document.addEventListener('mousedown', resetInactivityTimer);
    document.addEventListener('keypress', resetInactivityTimer);
    document.addEventListener('touchmove', resetInactivityTimer);
    document.addEventListener('scroll', resetInactivityTimer);
    
    // Iniciar el temporizador cuando la página carga
    resetInactivityTimer();
    
    // Hacer ping al servidor periódicamente para mantener viva la sesión mientras haya actividad
    setInterval(function() {
        const currentTime = new Date().getTime();
        const elapsedTime = currentTime - lastActivityTime;
        
        // Si ha habido actividad reciente (menos de 1 minuto), mantener la sesión viva
        if (elapsedTime < 60000) {
            fetch('/accounts/extend-session/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'Content-Type': 'application/json'
                }
            }).catch(error => console.log('Error al extender la sesión:', error));
        }
    }, 5 * 60 * 1000); // Cada 5 minutos
});