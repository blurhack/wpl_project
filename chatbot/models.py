from django.db import models


class FAQEntry(models.Model):
    keyword = models.CharField(max_length=40, unique=True)
    question = models.CharField(max_length=160)
    answer = models.TextField()
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['keyword']
        verbose_name = 'FAQ Entry'
        verbose_name_plural = 'FAQ Entries'

    def __str__(self):
        return self.question


class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
    ]

    session_key = models.CharField(max_length=80)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.role}: {self.text[:30]}'
