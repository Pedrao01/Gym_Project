import pytest
from plans.tasks import check_expired_plans
from django.utils import timezone
from dateutil.relativedelta import relativedelta


def test_check_expired_plans_search_for_invalid_dates_and_render_the_plan_invalid(inactive_plan):
    check_expired_plans()

    inactive_plan.refresh_from_db()

    assert inactive_plan.is_valid is False
    assert inactive_plan.is_active is False
    assert inactive_plan.expected_payment is None


def test_check_expired_plans_when_the_plan_is_valid(valid_plan):
    check_expired_plans()

    valid_plan.refresh_from_db()

    assert valid_plan.is_valid is True
    assert valid_plan.is_active is True
    assert valid_plan.expected_payment == timezone.now().date() + relativedelta(months=1)


def test_check_expired_plans_ignore_plan_invalid(invalid_plan):
    check_expired_plans()

    invalid_plan.refresh_from_db()

    assert invalid_plan.is_valid is False
    assert invalid_plan.is_active is False
    assert invalid_plan.expected_payment is not None


def test_return_check_expired_plans_total(five_plans_with_invalid_date):
    total = check_expired_plans()

    assert total == len(five_plans_with_invalid_date)