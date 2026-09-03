import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        return response

    logger.exception('Unhandled error in %s', context['view'].__class__.__name__)
    return Response({'Error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
