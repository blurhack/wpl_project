from django.urls import include, path

urlpatterns = [
    path('', include('flights.urls')),
    path('agent/', include('agents.urls')),
    path('track/', include('tracking.urls')),
    path('chatbot/', include('chatbot.urls')),
]
