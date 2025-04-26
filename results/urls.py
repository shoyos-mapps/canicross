from django.urls import path
from . import views

app_name = 'results'

urlpatterns = [
    # Add your URL patterns here
    path('', views.results_list, name='results_list'),
    path('event/<slug:event_slug>/', views.event_results, name='event_results'),
    path('race/<int:race_id>/', views.race_results, name='race_results'),
]