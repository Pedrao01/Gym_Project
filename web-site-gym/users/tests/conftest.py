import pytest
from rest_framework.test import APIClient
import jwt

from plans.models import Plan
from users.serializers import UserSerializer


@pytest.fixture
def payload_valid_user():
    return {
        'username': 'manel',
        'email': 'manel@gmail.com',
        'phone_number': '74999458944',
        'password': 'manel123'
    }


@pytest.fixture
def return_jwt_decoded():
    def _calc(access_token):
        return jwt.decode(access_token, options={"verify_signature": False})
    return _calc


@pytest.fixture
def admin_user(db, django_user_model):
    admin = django_user_model.objects.create_superuser(
        username='cleber',
        email='clebin@gmail.com',
        password='123456',
    )

    return admin


@pytest.fixture
def authenticated_admin(admin_user, api_client):
    api_client.force_authenticate(admin_user)

    return api_client


@pytest.fixture
def create_five_plans(db, create_five_users):
    plans = []

    for i in range(5):
        plan = Plan.objects.create(
            user=create_five_users[i],
            kind_plan='mensal',
            payment_id=f'123456{i}'
        )

        plans.append(plan)

    return plans

