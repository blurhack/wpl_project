from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('control-tower/', views.control_tower, name='control_tower'),
    path('flight/<int:flight_id>/', views.flight_detail, name='flight_detail'),
]
