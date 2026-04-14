from django.contrib import admin

from .models import Agent


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('employee_code', 'name', 'desk', 'email', 'phone', 'active')
    list_filter = ('active', 'desk')
    search_fields = ('employee_code', 'name', 'email', 'phone')
