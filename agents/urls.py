from django.urls import path

from . import views

urlpatterns = [
    path('', views.agent_booking, name='agent_booking'),
]
