from django.urls import path
from . import views

# NOTA: Este módulo se incluye en dos rutas diferentes:
# 1. /events/ con namespace 'events'
# 2. / (raíz) con namespace 'events_home'
# Por esta razón, cualquier plantilla que use {% url %} debe especificar
# el namespace completo, por ejemplo: {% url 'events:event_list' %} o {% url 'events_home:event_list' %}

app_name = 'events'

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('<slug:slug>/', views.event_detail, name='event_detail'),
    path('<slug:slug>/races/', views.race_list, name='race_list'),
    path('<slug:slug>/races/<int:race_id>/', views.race_detail, name='race_detail'),
    path('<slug:slug>/register/', views.event_register, name='event_register'),
]