from django.contrib import admin

from .models import ChatMessage, FAQEntry


@admin.register(FAQEntry)
class FAQEntryAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'question', 'active')
    list_filter = ('active',)
    search_fields = ('keyword', 'question', 'answer')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'role', 'text', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('session_key', 'text')
