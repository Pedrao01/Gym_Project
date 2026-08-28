import pytest


def test__str__of_model(valid_user):
    fstring = f'Username: {valid_user.username} - Email: {valid_user.email}'

    assert str(valid_user) == fstring
