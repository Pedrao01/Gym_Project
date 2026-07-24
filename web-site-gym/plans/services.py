from .models import Plan
from users.models import User
from django.db import transaction
from .utils import get_sdk
from .plans import PLANS
from dateutil.relativedelta import relativedelta
from datetime import date
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone


def create_preference(plan_id: str, user: User):
    sdk = get_sdk()
    plan = PLANS.get(plan_id)

    preference_data = {
        "items": [{
            "id": str(user.id),
            "title": plan['title'],
            "quantity": 1,
            "currency_id": "BRL",
            "unit_price": plan['unit_price'],
            "description": plan['description']
        }, ],
        "back_urls": {
            "success": "localhost:5173/?status=approved",
            "failure": "localhost:5173/?status=failure",
            "pending": "localhost:5173/?status=pending",
        },
        "auto_return": "all"
    }

    result = sdk.preference().create(preference_data)
    payment = result["response"]

    return payment


def get_status_payment_mercadopago(payment_id: int) -> str:
    sdk = get_sdk()

    request = sdk.payment().get(payment_id=payment_id)

    return request['response'].get('status')


def update_plan(user: User, plan_kind: str, payment_id):
    with transaction.atomic():
        plan = Plan.objects.get(user=user)
        if not plan.is_active:
            plan.is_active = True
            plan.is_valid = True
            plan.payment_id = payment_id
            plan.save(update_fields=['is_active', 'is_valid',  'payment_id'])

            number_months = PLANS.get(plan_kind).get('number_months')
            print(plan_kind, number_months)
            plan = update_next_payment(plan, number_months)

        return plan


def create_plan(user: User, kind_plan: str, payment_id: str) -> Plan:
    number_months = PLANS.get(kind_plan).get('number_months')

    with transaction.atomic():
        plan = Plan.objects.create(
            user=user,
            kind_plan=kind_plan,
            payment_id=payment_id
        )

        new_plan = update_next_payment(plan, number_months)

        return new_plan


def update_next_payment(plan: Plan, plan_months: int):
    data = plan.expected_payment
    if data is None:
        data = timezone.now().date()

    next_payment = data + relativedelta(months=plan_months)

    plan.expected_payment = next_payment
    plan.save(update_fields=['expected_payment'])

    return plan


def cancel_plan(user: User):
    plan = user.plan
    today_date = date.today()
    if today_date < plan.expected_payment:
        with transaction.atomic():
            plan.is_active = False
            plan.save(update_fields=['is_active'])

            return plan


def user_plan_is_active(user: User):
    try:
        plan = Plan.objects.get(user=user)

        if plan.is_active:
            return True

    except ObjectDoesNotExist:
        return False
