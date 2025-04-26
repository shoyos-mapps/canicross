from django.urls import path
from . import views

app_name = 'race_management'

urlpatterns = [
    # Add your URL patterns here
    path('', views.race_dashboard, name='dashboard'),
    path('start/<int:race_id>/', views.start_race, name='start_race'),
    path('finish/<int:race_id>/', views.finish_participant, name='finish_participant'),
]