from os import getenv

from django.conf import settings


def _setting(key, default):
    return getenv(key, default) or getattr(settings, key, default)


# API key from evnironment by default
API_KEY = _setting("AMIQUS_ACCESS_TOKEN", None)

# Webhook token - see https://documentation.onfido.com/#webhooks
WEBHOOK_SECURITY_TOKEN = _setting("AMIQUS_WEBHOOK_SECURITY_TOKEN", None)
# token must be a bytestring for HMAC function to work
WEBHOOK_SECURITY_TOKEN = (
    str.encode(WEBHOOK_SECURITY_TOKEN) if WEBHOOK_SECURITY_TOKEN else None
)

# Set to False to turn off event logging
LOG_EVENTS = _setting("AMIQUS_LOG_EVENTS", True)

# Set to True to bypass request verification (NOT RECOMMENDED)
TEST_MODE = _setting("AMIQUS_TEST_MODE", True)


def DEFAULT_CHECK_SCRUBBER(raw):
    """Remove specified properties."""
    return {k: v for k, v in raw.items() if k not in ("email")}


def DEFAULT_CLIENT_SCRUBBER(raw):
    """Remove _all_ data except the given properties."""
    return {k: v for k, v in raw.items() if k in ("id", "status", "created_at")}


# functions used to scrub sensitive data from checks
scrub_check_data = (
    getattr(settings, "AMIQUS_CHECK_SCRUBBER", None) or DEFAULT_CHECK_SCRUBBER
)

scrub_client_data = (
    getattr(settings, "AMIQUS_CLIENT_SCRUBBER", None) or DEFAULT_CLIENT_SCRUBBER
)

DEFAULT_REQUESTS_TIMEOUT = _setting("DEFAULT_REQUESTS_TIMEOUT", 30)
