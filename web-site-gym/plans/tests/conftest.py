import pytest

from datetime import date
from dateutil.relativedelta import relativedelta
from plans.models import Plan


@pytest.fixture
def next_payment_data():
    def _calc(base_date, months=1):
        return base_date + relativedelta(months=months)
    return _calc


@pytest.fixture
def inactive_plan(db, valid_user):
    return Plan.objects.create(
        user=valid_user,
        kind_plan='mensal',
        payment_id='123456',
        is_active=False,
        expected_payment=date(2026, 6, 13)
    )


@pytest.fixture
def invalid_plan(db, valid_user):
    return Plan.objects.create(
        user=valid_user,
        kind_plan='mensal',
        is_valid=False
    )


@pytest.fixture
def valid_plan_but_with_invalid_date(db, valid_user):
    return Plan.objects.create(
        user=valid_user,
        kind_plan='mensal',
        payment_id='123456',
        expected_payment=date(2026, 5, 13)
    )


@pytest.fixture
def payment_mock_valid(valid_user, valid_plan):
    return {
        'status': 'approved',
        'additional_info': {
            'items': [{
                'id': str(valid_user.id),
                'category_id': valid_plan.kind_plan
            }]
        }
    }
