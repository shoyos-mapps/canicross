from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

router = DefaultRouter()
router.register(r'events', views.EventViewSet, basename='events')
router.register(r'races', views.RaceViewSet, basename='races')
router.register(r'participants', views.ParticipantViewSet, basename='participants')
router.register(r'annotations', views.AnnotationViewSet, basename='annotations')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
    
    # Custom endpoints
    path('races/<int:race_id>/participants/search/', views.search_participant, name='search-participant'),
    path('events/<int:event_id>/penalty_types/', views.list_penalty_types, name='penalty-types'),
    path('events/<int:event_id>/active_races/', views.list_active_races, name='active-races'),
]