import pytest


def test__str__of_model(valid_plan):
    fstring = f'Payment ID: {valid_plan.id} - Is valid: {valid_plan.is_valid} - Is active: {valid_plan.is_active}'

    assert str(valid_plan) == fstring