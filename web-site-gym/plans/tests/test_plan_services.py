import pytest
from plans.services import create_plan, update_plan, update_next_payment, cancel_plan, user_plan_is_active
from django.utils import timezone
from plans.plans import PLANS


def test_plan_create_successful(valid_user, next_payment_data):
    today = timezone.now().date()

    plan = create_plan(
        user=valid_user,
        kind_plan='mensal',
        payment_id='123456'
    )

    assert plan.is_active is True
    assert plan.is_valid is True
    assert plan.user == valid_user
    assert plan.kind_plan == 'mensal'
    assert plan.payment_id == '123456'
    assert plan.expected_payment == next_payment_data(today)


def test_update_plan_when_is_not_active(valid_user, inactive_plan, next_payment_data):
    base_date = inactive_plan.expected_payment

    updated_plan = update_plan(
        user=valid_user,
        plan_kind='mensal',
        payment_id='123457'
    )

    assert updated_plan.user == valid_user
    assert updated_plan.expected_payment == next_payment_data(base_date)
    assert updated_plan.is_active is True
    assert updated_plan.payment_id == '123457'


def test_update_plan_next_payment(valid_plan_but_with_invalid_date, next_payment_data):
    number_months = PLANS[valid_plan_but_with_invalid_date.kind_plan]['number_months']
    base_date = valid_plan_but_with_invalid_date.expected_payment

    updated_plan = update_next_payment(valid_plan_but_with_invalid_date, number_months)

    assert updated_plan.expected_payment == next_payment_data(base_date)


def test_update_next_payment_when_expected_payment_is_none(valid_user, inactive_plan, next_payment_data):
    inactive_plan.expected_payment = None
    data = timezone.now().date()

    updated_plan = update_next_payment(inactive_plan, 1)

    assert updated_plan.expected_payment == next_payment_data(data, 1)


def test_cancel_plan_while_is_valid(valid_user, valid_plan):

    canceled_plan = cancel_plan(valid_user)

    assert canceled_plan.is_active is False
    assert canceled_plan.is_valid is True
    assert canceled_plan.expected_payment == valid_plan.expected_payment


def test_when_expected_payment_already_is_none(valid_user, invalid_plan):
    invalid_plan.expected_payment = None
    invalid_plan.save()

    canceled_plan = cancel_plan(user=valid_user)

    assert canceled_plan is None


def test_return_user_plan_is_active_is_true(valid_user, valid_plan):
    plan_state = user_plan_is_active(valid_user)
    assert plan_state is True


def test_return_user_plan_is_active_is_false(valid_user, inactive_plan):
    plan_state = user_plan_is_active(valid_user)
    assert plan_state is False


def test_user_plan_is_active_when_no_plan(valid_user):
    plan_state = user_plan_is_active(valid_user)
    assert plan_state is False
