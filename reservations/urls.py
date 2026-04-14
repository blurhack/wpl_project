from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('flight/<int:flight_id>/', views.flight_detail, name='flight_detail'),
    path('agent/', views.agent_booking, name='agent_booking'),
    path('track/', views.track_search, name='track_search'),
    path('track/<str:pnr>/', views.track_booking, name='track_booking'),
    path('chatbot/', views.chatbot, name='chatbot'),
]
