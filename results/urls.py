from django.urls import path
from . import views

app_name = 'results'

urlpatterns = [
    # Vistas públicas para resultados
    path('', views.results_list, name='results_list'),
    path('event/<slug:event_slug>/', views.event_results, name='event_results'),
    path('race/<int:race_id>/', views.race_results, name='race_results'),
    
    # Vistas de jueces (protegidas)
    path('judge/', views.judge_dashboard, name='dashboard'),
    path('judge/races/', views.race_list, name='race_list'),
    path('judge/race/<int:race_id>/participants/', views.participant_list, name='participant_list'),
    path('judge/registration/<int:registration_id>/result/', views.record_result, name='record_result'),
    path('judge/penalty/<int:penalty_id>/delete/', views.delete_penalty, name='delete_penalty'),
    path('judge/time-record/<int:time_record_id>/delete/', views.delete_time_record, name='delete_time_record'),
    path('judge/registration/<int:registration_id>/annotation/', views.add_annotation, name='add_annotation'),
]