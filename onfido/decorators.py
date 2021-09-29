from __future__ import annotations

import hashlib
import hmac
import logging
from functools import wraps
from typing import Any, Callable

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden

from .settings import TEST_MODE, WEBHOOK_TOKEN

logger = logging.getLogger(__name__)


def _hmac(token: bytes, text: bytes) -> str:
    """
    Calculate SHA1 HMAC digest from request body and token.

    Args:
        token: bytes, the webhook token from Onfido API settings.
        text: string, the text to hash.

    Return the SHA1 HMAC as a string.

    """
    auth_code = hmac.new(token, text, hashlib.sha256).hexdigest()
    logger.debug("Onfido callback request HMAC: %s", auth_code)
    return auth_code


def _match(token: bytes, request: HttpRequest) -> bool:
    """
    Calculate signature and return True if it matches header.

    Args:
        token: string, the webhook_token.
        request: an HttpRequest object from which the body content and
            X-Signature header will be extracted and matched.

    Returns True if there is a match.

    """
    try:
        signature = request.headers["X-SHA2-Signature"]
        logger.debug("Onfido callback X-Signature: %s", signature)
        logger.debug("Onfido callback request body: %s", request.body)
        return _hmac(token, request.body) == signature
    except KeyError:
        logger.warning(
            "Onfido callback missing X-Signature - this may be an unauthorised request."
        )
        return False
    except Exception:  # noqa: B902
        logger.exception("Error attempting to decode Onfido signature.")
        return False


def verify_signature() -> Callable:
    """
    View function decorator used to verify Onfido webhook signatures.

    This function uses the WEBHOOK_TOKEN specified in settings to calculate
    the HMAC. If it doesn't exist, then this decorator will immediately fail
    hard with an ImproperlyConfigured exception.

    If TEST_MODE is on (ONFIDO_TEST_MODE setting) then the verification will
    be ignored.

    See: https://documentation.onfido.com/#webhooks

        Each webhook URL is associated with a secret token. This is
        visible in the response.token field when registering a webhook.

        Events sent to your application will be signed using this token:
        verifying the request signature on your server prevents attackers
        from imitating valid webhooks. The HMAC digest signature, generated
        using SHA-1, will be stored in a X-Signature header.

        When you receive an event, you should compute a hash using your
        secret token, and ensure that the X-Signature sent by Onfido
        matches that hash.

    If the HMAC signatures don't match, return a 403

    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def _wrapped_func(
            request: HttpRequest, *args: Any, **kwargs: Any
        ) -> HttpResponse:
            if TEST_MODE:
                logger.debug(
                    "Ignoring Onfido callback verification (ONFIDO_TEST_MODE enabled)"
                )
                return func(request, *args, **kwargs)
            if not WEBHOOK_TOKEN:
                raise ImproperlyConfigured("Missing ONFIDO_WEBHOOK_TOKEN")
            if _match(WEBHOOK_TOKEN, request):
                return func(request, *args, **kwargs)
            else:
                # logging as a warning means it'll likely appear in logs,
                # but it's by design - if people are sending invalid requests
                # we need to know.
                logger.warning("Onfido callback request verification failed.")
                return HttpResponseForbidden("Invalid X-Signature")

        return _wrapped_func

    return decorator
