import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from users.models import User
from plans.models import Plan
from unittest.mock import patch


class TestPaymentPlan:

    url = reverse('plan-payment')

    def test_return_400_if_plan_is_active(self, authenticated_client, valid_user, valid_plan):
        response = authenticated_client.post(
            self.url, {}, format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {'error': '❌ Plano já está ativo.'}


class TestPaymentConfirm:

    url = reverse('payment-confirm')

    def test_return_400_when_no_payment_id(self, authenticated_client):
        response = authenticated_client.post(self.url, {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {'error': 'PaymentId no provide'}

    @patch('plans.views.get_payment_mercadopago')
    def test_return_400_when_payment_user_differs_from_authenticated_user(self, mock_mp, authenticated_client):
        mock_mp.return_value = {
            'additional_info': {'items': [{'id': '99999'}]}
        }

        response = authenticated_client.post(
            self.url, {'payment_id': '123456'}, format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {'error': 'The payment ID is not the same as the user ID'}

    @patch('plans.views.get_payment_mercadopago')
    def test_return_400_when_payment_not_approved(self, mock_mp, authenticated_client, valid_user):
        mock_mp.return_value = {
            'status': 'failed',
            'additional_info': {'items': [{'id': str(valid_user.id)}]}
        }

        response = authenticated_client.post(
            self.url, {'payment_id': '123456'}, format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {'error': 'Invalid payment'}

    @patch('plans.views.get_payment_mercadopago')
    def test_return_200_when_plan_already_exists_with_same_payment_id(
            self, mock_mp, authenticated_client, payment_mock_valid, valid_plan
    ):
        mock_mp.return_value = payment_mock_valid

        valid_plan.payment_id = '123456'
        valid_plan.save()

        response = authenticated_client.post(
            self.url, {'payment_id': '123456'}, format='json'
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'plan_name': valid_plan.kind_plan,
            'expires_at': valid_plan.expected_payment,
            'is_active': valid_plan.is_valid
        }

    @patch('plans.views.get_payment_mercadopago')
    def test_updates_plan_when_payment_id_is_new(
            self, mock_mp, authenticated_client, valid_user, inactive_plan
    ):
        mock_mp.return_value = {
            'status': 'approved',
            'additional_info': {'items': [{
                'id': str(valid_user.id),
                'category_id': inactive_plan.kind_plan
            }]}
        }

        response = authenticated_client.post(
            self.url, {'payment_id': '999999'}, format='json'
        )

        inactive_plan.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert inactive_plan.payment_id == '999999'
        assert inactive_plan.is_active is True
        assert response.data == {
            'plan_name': inactive_plan.kind_plan,
            'expires_at': inactive_plan.expected_payment,
            'is_active': inactive_plan.is_valid
        }

    @patch('plans.views.get_payment_mercadopago')
    def test_creates_plan_when_user_has_no_plan(
            self, mock_mp, authenticated_client, valid_user
    ):
        mock_mp.return_value = {
            'status': 'approved',
            'additional_info': {
                'items': [{
                    'id': str(valid_user.id),
                    'category_id': 'mensal'
                }]
            }
        }

        assert not Plan.objects.filter(user=valid_user).exists()

        response = authenticated_client.post(
            self.url, {'payment_id': '123458'}, format='json'
        )

        plan = valid_user.plan

        assert response.status_code == status.HTTP_200_OK
        assert Plan.objects.filter(user=valid_user).exists()
        assert response.data == {
            'plan_name': plan.kind_plan,
            'expires_at': plan.expected_payment,
            'is_active': plan.is_valid
        }

    def test_unauthenticated_user_cannot_confirm_payment(self, api_client):
        response = api_client.post(
            self.url,
            {'payment_id': '123456'},
            format='json'
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestPlanStatus:
    url = reverse('plan-status')

    def test_return_401_when_without_authentication(self, client):

        response = client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_return_200_when_user_plan_is_valid(
            self, authenticated_client, valid_user, valid_plan
    ):

        response = authenticated_client.get(
            self.url,
            {},
            format='json'
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'plan_name': valid_plan.kind_plan,
            'expires_at': valid_plan.expected_payment,
            'is_active': valid_plan.is_active
        }

    def test_return_400_when_user_does_not_has_plan(self, authenticated_client):

        response = authenticated_client.get(self.url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {'msg': 'User does not have plan'}

    def test_return_400_when_user_plan_is_invalid(
            self, authenticated_client, valid_user, invalid_plan
    ):

        response = authenticated_client.get(
            self.url,
            {},
            format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestCancelPlan:
    url = reverse('plan-cancel')

    def test_return_500_when_cancel_plan_function_return_none(
            self, authenticated_client, valid_user, valid_plan
    ):
        valid_plan.expected_payment = None

        response = authenticated_client.post(
            self.url,
            {},
            format='json'
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data == {'error': 'Internal server error'}

    def test_return_200_when_successful_in_plan_cancel(
            self, authenticated_client, valid_user, valid_plan
    ):

        response = authenticated_client.post(
            self.url,
            {},
            format='json'
        )

        assert response.status_code == status.HTTP_200_OK
        valid_plan.refresh_from_db()
        assert valid_plan.is_active is False
        assert response.data == {
            'plan_name': valid_plan.kind_plan,
            'expires_at': valid_plan.expected_payment,
            'is_active': valid_plan.is_active
        }
