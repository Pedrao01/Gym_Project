from .models import User
from django.core.exceptions import ValidationError
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


def update_user(user_id: str, username: str, email: str, phone_number: str) -> User:
    print(user_id, username, email, phone_number)
    data = User.objects.filter(username=username, email=email, phone_number=phone_number)
    if data:
        raise ValidationError('Someone this fields already are using: Username, email or phone number')

    try:
        user = User.objects.filter(id=user_id).update(
            username=username,
            email=email,
            phone_number=phone_number
        )

        return user

    except OperationalError:
        raise ValidationError('Database internal error')

    except TypeError as e:
        print(e)
