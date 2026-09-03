import pytest
from django.urls import reverse
from rest_framework import status
from plans.models import Plan
from users.models import User
from users.serializers import UserSerializer


class TestCreateUser:
    url = reverse('user-create')

    def test_return_400_when_serializer_return_invalid(self, db,  client):
        payload = {'username': 'pedro'}

        response = client.post(
            self.url,
            payload,
            format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_return_400_when_try_create_user_with_existing_credentials(
            self, db, client, valid_user
    ):
        payload = {
            'username': 'pedro',
            'email': 'pedro@gmail.com',
            'phone_number': '74999668392',
            'password': 'pedro123'
        }

        response = client.post(
            self.url,
            payload,
            format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_return_201_when_user_created_successful(self, db, api_client, payload_valid_user):

        response = api_client.post(
            self.url,
            payload_valid_user,
            format='json'
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['email'] == payload_valid_user['email']

    def test_return_error_when_password_has_less_then_8_characters(self, db, api_client):
        payload = {
            'username': 'manel',
            'email': 'manel@gmail.com',
            'phone_number': '74999458944',
            'password': 'man'
        }

        response = api_client.post(
            self.url,
            payload,
            format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data['error']


class TestLogin:
    url = reverse('login')

    def test_login_is_valid(self, valid_user, api_client):

        payload = {
            'username': 'pedro',
            'password': 'pedro123'
        }

        response = api_client.post(
            self.url,
            payload,
            format='json'
        )

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_verify_if_access_token_has_credentials(self, valid_user, api_client, return_jwt_decoded):
        payload = {
            'username': 'pedro',
            'password': 'pedro123'
        }

        response = api_client.post(
            self.url,
            payload,
            format='json'
        )

        token_decoded = return_jwt_decoded(response.data['access'])

        assert 'is_staff' in token_decoded
        assert token_decoded['is_staff'] is False

    def test_return_400_if_password_incorrect(self, valid_user, api_client):
        payload = {
            'username': 'pedro',
            'password': 'wrongPassword'
        }

        response = api_client.post(
            self.url,
            payload,
            format='json'
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'detail' in response.data

    def test_when_user_does_not_exists(self, db,  api_client):
        payload = {
            'username': 'pedro',
            'password': '123456'
        }

        response = api_client.post(
            self.url,
            payload,
            format='json'
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'detail' in response.data


class TestUser:
    url = reverse('user')

    def test_return_200_when_find_user_and_return_valid_credentials(self, authenticated_client):

        response = authenticated_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert 'username' in response.data
        assert 'email' in response.data
        assert 'phone_number' in response.data
        assert 'password' not in response.data

    def test_return_400_when_invalid_credentials(self, authenticated_client, valid_user_1):
        payload = {
            'username': 'manel',
            'email': 'pedro@gmail.com',
            'phone_number': '74999668392'
        }

        response = authenticated_client.patch(
            self.url,
            payload,
            format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_return_of_method_patch_when_updated_successful(self, authenticated_client, valid_user):

        data = {
            'username': 'pedro',
            'email': 'pedrin@gmail.com',
            'phone_number': '74999876543'
        }

        response = authenticated_client.patch(self.url, data, format='json')
        valid_user.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert valid_user.username == data.get('username')
        assert valid_user.email == data.get('email')
        assert valid_user.phone_number == data.get('phone_number')


class TestStats:
    url = reverse('admin-stats')

    def test_return_total_users_with_plan_without_plan(self, authenticated_admin, create_five_plans):

        response = authenticated_admin.get(self.url)

        assert response.status_code == status.HTTP_200_OK

        assert 'total' in response.data
        assert 'with_plan' in response.data
        assert 'without_plan' in response.data

        assert response.data['total'] == len(Plan.objects.all())
        assert response.data['with_plan'] == len(Plan.objects.filter(is_active=True))
        assert response.data['without_plan'] == len(Plan.objects.filter(is_active=False))

    def test_return_403_when_not_is_admin(self, authenticated_client):

        response = authenticated_client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestListUsers:
    url = reverse('list-users')

    def test_pagination_structure(self, authenticated_admin, create_five_users, create_five_plans):

        response = authenticated_admin.get(self.url)

        assert response.status_code == status.HTTP_200_OK

        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert 'results' in response.data

        assert isinstance(response.data['count'], int)
        assert isinstance(response.data['results'], list)

        if response.data['count'] > 0:
            assert len(response.data['results']) > 0

    def test_struct_pagination_results(self, authenticated_admin, create_five_plans):

        response = authenticated_admin.get(self.url)

        fields = ['id', 'username', 'email', 'phone_number', 'plan', 'is_staff']

        for user in response.data['results']:
            for field in fields:
                assert field in user

    def test_return_only_users_with_plan(self, authenticated_admin, create_five_plans):

        response = authenticated_admin.get(self.url)

        assert response.status_code == status.HTTP_200_OK

        for user in response.data['results']:
            assert user['plan'] is not None

    def test_return_403_when_user_not_is_admin(self, authenticated_client, create_five_plans):

        response = authenticated_client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_return_401_when_user_not_authenticated(self, client):

        response = client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_return_specific_user(self, authenticated_admin, valid_user, valid_plan):

        response = authenticated_admin.get(self.url, data={'search': 'pedro'}, format='json')

        fields = ['id', 'username', 'email', 'phone_number', 'plan', 'is_staff']

        for field in fields:
            assert field in response.data['results'][0]


class TestUpdatePlanUser:

    def test_when_update_plan_is_successful(self, authenticated_admin, valid_user, valid_plan):
        url = reverse('update-plan-user', kwargs={'user_id': valid_user.id})

        response = authenticated_admin.patch(url, {'is_active': False}, format='json')

        assert response.status_code == status.HTTP_200_OK

        valid_plan.refresh_from_db()
        assert valid_plan.is_active is False

    def test_response_contains_expected_fields(self, authenticated_admin, valid_user, valid_plan):
        url = reverse('update-plan-user', kwargs={'user_id': valid_user.id})

        response = authenticated_admin.patch(url, {'is_active': False}, format='json')

        fields = ['id', 'username', 'email', 'phone_number', 'plan', 'is_staff']

        for field in fields:
            assert field in response.data

    def test_when_body_is_not_sent(self, authenticated_admin, valid_user, valid_plan):
        url = reverse('update-plan-user', kwargs={'user_id': valid_user.id})

        response = authenticated_admin.patch(url, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_when_is_active_is_not_bool(self, authenticated_admin, valid_user, valid_plan):
        url = reverse('update-plan-user', kwargs={'user_id': valid_user.id})

        response = authenticated_admin.patch(url, {'is_active': 'string'}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_when_user_id_is_invalid(self, authenticated_admin):
        url = reverse('update-plan-user', kwargs={'user_id': 13})

        response = authenticated_admin.patch(url, {'is_active': False}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
