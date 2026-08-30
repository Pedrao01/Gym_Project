from .models import User
from plans.models import Plan
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import IntegrityError, OperationalError


def get_by_username(username: str) -> User:
    users = User.objects.get_by_natural_key(username)
    return users


def creates_user(username: str, email: str, phone_number: str, password: str) -> User:
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            phone_number=phone_number,
            password=password
        )

        return user

    except IntegrityError:
        raise ValidationError('Someone this fields already are using: Username, email, phone_number')
    except OperationalError:
        raise ValidationError('Database internal error')


def update_user(user: User, username: str, email: str, phone_number: str) -> int:
    try:
        User.objects.filter(id=user.id).update(
            username=username,
            email=email,
            phone_number=phone_number
        )

    except OperationalError:
        raise ValidationError('Database internal error')

    except Exception:
        raise Exception('Internal server error')


def update_user_plan(user_id, is_active):
    try:
        user = User.objects.get(id=user_id)
        user.plan.is_active = is_active
        user.plan.save()

        return user

    except ObjectDoesNotExist:
        raise Exception('Dont exists user with id provided or user dont have a plan')
