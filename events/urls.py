from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('<slug:slug>/', views.event_detail, name='event_detail'),
    path('<slug:slug>/races/', views.race_list, name='race_list'),
    path('<slug:slug>/races/<int:race_id>/', views.race_detail, name='race_detail'),
    path('<slug:slug>/register/', views.event_register, name='event_register'),
]