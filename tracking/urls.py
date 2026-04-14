from django.urls import path

from . import views

urlpatterns = [
    path('', views.track_search, name='track_search'),
    path('<str:pnr>/', views.track_booking, name='track_booking'),
]
