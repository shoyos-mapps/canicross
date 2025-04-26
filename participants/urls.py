from django.urls import path
from . import views

app_name = 'participants'

urlpatterns = [
    path('', views.participant_list, name='participant_list'),
    path('profile/', views.participant_profile, name='profile'),
    path('dogs/', views.dog_list, name='dog_list'),
    path('dogs/add/', views.dog_add, name='dog_add'),
    path('dogs/<int:dog_id>/', views.dog_detail, name='dog_detail'),
    path('dogs/<int:dog_id>/edit/', views.dog_edit, name='dog_edit'),
]