import mercadopago
from decouple import config

MERCADOPAGO_ACCESS_TOKEN = config('MERCADOPAGO_ACCESS_TOKEN')


def get_sdk():
    return mercadopago.SDK(MERCADOPAGO_ACCESS_TOKEN)
