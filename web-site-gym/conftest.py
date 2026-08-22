import pytest
from rest_framework.test import APIClient
from plans.models import Plan
from django.utils import timezone
from dateutil.relativedelta import relativedelta


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, valid_user):
    api_client.force_authenticate(user=valid_user)
    return api_client


@pytest.fixture
def valid_user(db, django_user_model):
    return django_user_model.objects.create_user(
        username='pedro',
        email='pedro@gmail.com',
        phone_number='74999668392',
        password='pedro123'
    )


@pytest.fixture
def valid_plan(db, valid_user):
    return Plan.objects.create(
        user=valid_user,
        kind_plan='mensal',
        expected_payment=timezone.now().date() + relativedelta(months=1)
    )


@pytest.fixture
def valid_user_1(db, django_user_model):
    return django_user_model.objects.create_user(
        username='manel',
        email='manel@gmail.com',
        phone_number='74999873645',
        password='manel123'
    )


@pytest.fixture
def create_five_users(db, django_user_model):
    users = []

    for i in range(5):
        user = django_user_model.objects.create(
            username=f'user{i}',
            email=f'user{i}@gmail.com',
            phone_number=f'7499912345{i}',
            password='12345678'
        )
        users.append(user)

    return users