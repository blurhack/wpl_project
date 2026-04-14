from celery import shared_task

from .models import DelayAlert


@shared_task
def active_delay_alert_count():
    return DelayAlert.objects.filter(active=True).count()
