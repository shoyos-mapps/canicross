from django.urls import path
from . import views

app_name = 'kits'

urlpatterns = [
    # Add your URL patterns here
    path('', views.kit_dashboard, name='dashboard'),
    path('deliver/<int:registration_id>/', views.deliver_kit, name='deliver'),
]