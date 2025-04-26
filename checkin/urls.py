from django.urls import path
from . import views

app_name = 'checkin'

urlpatterns = [
    # Add your URL patterns here
    path('', views.checkin_dashboard, name='dashboard'),
    path('activate/<int:registration_id>/', views.activate_participant, name='activate'),
]