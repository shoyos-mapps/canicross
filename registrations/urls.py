from django.urls import path
from . import views

app_name = 'registrations'

urlpatterns = [
    path('', views.registration_list, name='list'),
    path('form/', views.registration_form, name='registration_form'),
    path('confirmation/<int:registration_id>/', views.registration_confirmation, name='confirmation'),
    path('payment/update/<int:registration_id>/', views.update_payment_status, name='update_payment'),
    path('payment/bulk-update/', views.bulk_update_payment_status, name='bulk_update_payment'),
]