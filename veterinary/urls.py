from django.urls import path
from . import views

app_name = 'veterinary'

urlpatterns = [
    # Add your URL patterns here
    path('', views.veterinary_dashboard, name='dashboard'),
    path('approval/<int:registration_id>/', views.veterinary_approval, name='approval'),
]