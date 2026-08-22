from celery import shared_task
from .models import Plan
from django.utils import timezone


@shared_task
def check_expired_plans():
    today = timezone.now().date()
    expired_plans = Plan.objects.filter(
        is_valid=True,
        expected_payment__isnull=False,
        expected_payment__lte=today

    )
    total = expired_plans.update(is_active=False, is_valid=False, expected_payment=None)

    return total
