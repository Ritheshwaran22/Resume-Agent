import logging
from django.conf import settings
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger('config.exceptions')

def production_exception_handler(exc, context):
    """
    Centralized exception handler for Django REST Framework.
    - Preserves standard DRF status codes (400, 401, 403, 404, 405, 429)
    - Preserves detailed validation errors (invalid email, password mismatch, etc.)
    - Catches unexpected 500 errors and returns a safe, sanitized JSON response
      without leaking tracebacks, SQL queries, or internal credentials.
    """
    # Call DRF's default exception handler first to obtain standard error responses
    response = exception_handler(exc, context)

    if response is not None:
        return response

    # Unhandled exception: log server-side safely without leaking to the client
    view = context.get('view')
    view_name = view.__class__.__name__ if view else 'UnknownView'
    request = context.get('request')
    user_id = getattr(getattr(request, 'user', None), 'id', 'anonymous')
    method = getattr(request, 'method', 'UNKNOWN')
    path = getattr(request, 'path', 'unknown')

    logger.error(
        f"[InternalServerError] Unhandled {type(exc).__name__} in {view_name} "
        f"({method} {path}, User: {user_id}): {exc}",
        exc_info=True
    )

    return Response(
        {"detail": "An unexpected error occurred. Please try again later."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
