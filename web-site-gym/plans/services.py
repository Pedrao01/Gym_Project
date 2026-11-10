from datetime import date

from dateutil.relativedelta import relativedelta
from decouple import config
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
from django.utils import timezone

from core.exceptions import PaymentAlreadyUsed
from users.models import User

from .models import Payment, Plan
from .plans import PLANS
from .utils import get_sdk


def create_preference(plan_id: str, user: User):
    sdk = get_sdk()
    plan = PLANS.get(plan_id)
    back_url = config("BACK_URL")

    preference_data = {
        "items": [
            {
                "id": str(user.id),
                "title": plan["title"],
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": plan["unit_price"],
                "description": plan["description"],
                "category_id": plan_id,
            },
        ],
        "back_urls": {
            "success": f"{back_url}/?status=approved",
            "failure": f"{back_url}/?status=failure",
            "pending": f"{back_url}/?status=pending",
        },
        "auto_return": "all",
    }

    result = sdk.preference().create(preference_data)
    payment = result["response"]

    return payment


def get_payment_mercadopago(payment_id: int) -> dict:
    sdk = get_sdk()

    request = sdk.payment().get(payment_id=payment_id)

    return request["response"]


def update_plan(user: User, plan_kind: str):
    with transaction.atomic():
        plan = Plan.objects.get(user=user)
        plan.is_active = True
        plan.is_valid = True
        plan.kind_plan = plan_kind
        plan.save(update_fields=["is_active", "is_valid", "kind_plan"])

        number_months = PLANS.get(plan_kind).get("number_months")
        plan = update_next_payment(plan, number_months)

        return plan


def create_plan(user: User, kind_plan: str) -> Plan:
    number_months = PLANS.get(kind_plan).get("number_months")

    with transaction.atomic():
        plan = Plan.objects.create(user=user, kind_plan=kind_plan)

        new_plan = update_next_payment(plan, number_months)

        return new_plan


def update_next_payment(plan: Plan, plan_months: int):
    data = plan.expected_payment
    if data is None:
        data = timezone.now().date()

    next_payment = data + relativedelta(months=plan_months)

    plan.expected_payment = next_payment
    plan.save(update_fields=["expected_payment"])

    return plan


def cancel_plan(user: User):
    plan = user.plan
    today_date = date.today()
    if plan.expected_payment is None:
        return None

    if today_date <= plan.expected_payment:
        with transaction.atomic():
            plan.is_active = False
            plan.save(update_fields=["is_active"])

            return plan


def user_plan_is_active(user: User):
    try:
        plan = Plan.objects.get(user=user)

        if plan.is_active:
            return True

        return False

    except ObjectDoesNotExist:
        return False


def create_payment(user: User, payment_id: str, payment_plan_name: str):
    try:
        with transaction.atomic():
            payment_user = Payment.objects.create(
                payment_id=payment_id,
                payment_plan_name=payment_plan_name,
                user=user,
            )

            return payment_user
    except IntegrityError:
        raise PaymentAlreadyUsed("This payment was already used")


def confirm_payment(user: User, payment_id: str, plan_kind: str):
    with transaction.atomic():
        create_payment(user, payment_id, plan_kind)

        if Plan.objects.filter(user=user).exists():
            plan = update_plan(user, plan_kind)

            return plan

        plan = create_plan(user, plan_kind)

        return plan
