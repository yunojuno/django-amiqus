"""
Basic wire operations with the API - GET/POST/PUT.

This is a simple wrapper around requests.

"""
from __future__ import annotations

import logging
from urllib import parse as urlparse

import requests
from django.http import HttpResponse

from .settings import API_KEY, DEFAULT_REQUESTS_TIMEOUT

logger = logging.getLogger(__name__)

# the API HTTP root url
API_ROOT = "https://id.amiqus.co/api/"
API_ROOT_V2 = "https://id.amiqus.co/api/v2/"

API_ROOT_MAP = {
    1: API_ROOT,
    2: API_ROOT_V2,
}


class ApiError(Exception):
    """Error raised when interacting with the API."""

    def __init__(self, response: HttpResponse) -> None:
        """Initialise error from response object."""
        data = response.json()
        logger.debug("Amiqus API error: %s", data)
        super().__init__(data["error"])
        self.status_code = response.status_code
        self.error_type = data["error"]


def _url(path: str, version: int) -> str:
    """Format absolute API URL."""
    api_root = API_ROOT_MAP.get(version, API_ROOT_V2)
    return urlparse.urljoin(api_root, path)


def _headers(api_key: str = API_KEY) -> dict[str, str]:
    """Format request headers."""
    return {
        "Authorization": "Bearer {}".format(api_key),
        "Content-Type": "application/json",
    }


def _respond(response: HttpResponse) -> dict:
    """Process common response object."""
    if not str(response.status_code).startswith("2"):
        raise ApiError(response)
    data = response.json()
    logger.debug("Amiqus API response: %s", data)
    return data


def get(href: str, *, version: int = 2) -> dict:
    """Make a GET request and return the response as JSON."""
    logger.debug("Amiqus API GET request: %s", href)
    return _respond(
        requests.get(
            _url(href, version), headers=_headers(), timeout=DEFAULT_REQUESTS_TIMEOUT
        )
    )


def post(href: str, *, data: dict, version: int = 2) -> dict:
    """Make a POST request and return the response as JSON."""
    logger.debug("Amiqus API POST request: %s", href)
    return _respond(
        requests.post(
            _url(href, version),
            headers=_headers(),
            json=data,
            timeout=DEFAULT_REQUESTS_TIMEOUT,
        )
    )
