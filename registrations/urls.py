from django.urls import path
from . import views

app_name = 'registrations'

urlpatterns = [
    path('', views.registration_form, name='registration_form'),
    path('confirmation/<int:registration_id>/', views.registration_confirmation, name='confirmation'),
]