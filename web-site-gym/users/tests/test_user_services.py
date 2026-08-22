import pytest
from users.services import get_by_username, creates_user, update_user, update_user_plan
from django.db import IntegrityError
from django.core.exceptions import ValidationError


def test_get_user_by_username_function(valid_user):
    user = get_by_username('pedro')

    assert user == valid_user


def test_successful_create_user(db, payload_valid_user):

    user = creates_user(**payload_valid_user)

    assert user.username == payload_valid_user['username']
    assert user.email == payload_valid_user['email']
    assert user.phone_number == payload_valid_user['phone_number']


def test_create_user_when_someone_field_already_are_using(valid_user):
    with pytest.raises(
            ValidationError, match='Someone this fields already are using: Username, email, phone_number'
    ):
        creates_user(
            username='pedro',
            email='pedro@gmail.com',
            phone_number='74999668392',
            password='123456'
        )


def test_update_user_is_successful(valid_user):

    update_user(
        user=valid_user,
        username='manel',
        email='cabeca@gmail.com',
        phone_number='74999458944'
    )

    valid_user.refresh_from_db()

    assert valid_user.username == 'manel'
    assert valid_user.email == 'cabeca@gmail.com'
    assert valid_user.phone_number == '74999458944'


def test_update_user_plan(valid_user, valid_plan):
    user = update_user_plan(valid_user.id, False)

    assert user.plan.is_active is False
    valid_plan.refresh_from_db()
    assert valid_plan.is_active is False


def test_try_update_user_with_invalid_id(valid_user):
    with pytest.raises(Exception, match='Dont exists user with id provided or user dont have a plan'):
        update_user_plan(3, False)


def test_try_update_user_that_dont_have_plan(valid_user):
    with pytest.raises(Exception, match='Dont exists user with id provided or user dont have a plan'):
        update_user_plan(valid_user.id, False)