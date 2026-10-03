"""
Rate throttling classes for account-related operations.
Protects sensitive endpoints like password reset against abuse and brute-force attacks.
"""
from rest_framework.throttling import SimpleRateThrottle
from django.conf import settings


class PasswordResetRateThrottle(SimpleRateThrottle):
    """
    Limits the rate of password reset requests from any single client IP.
    Configured via PASSWORD_RESET_RATE_LIMIT in Django settings or environment variables
    (default: '5/hour').
    """
    scope = 'password_reset'

    def get_cache_key(self, request, view):
        """
        Throttle based on the requester's client IP address.
        Applied to all requests on the endpoint to prevent abuse.
        """
        ident = self.get_ident(request)
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident,
        }

    def get_rate(self):
        """
        Retrieve throttle rate dynamically from Django settings,
        falling back to standard DRF THROTTLE_RATES or '5/hour'.
        """
        rate = getattr(settings, 'PASSWORD_RESET_RATE_LIMIT', None)
        if rate:
            return rate
        try:
            return super().get_rate()
        except Exception:
            return '5/hour'
