from django.contrib import admin
from django.urls import include, path

admin.site.site_header = 'AeroMitra Airline Admin'
admin.site.site_title = 'AeroMitra Admin'
admin.site.index_title = 'Airline Operations Dashboard'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('accounts.urls')),
    path('', include('flights.urls')),
    path('agent/', include('agents.urls')),
    path('track/', include('tracking.urls')),
    path('chatbot/', include('chatbot.urls')),
]
