from __future__ import annotations

from typing import Any, Iterable

from django.conf import settings

from .api import post
from .models import Check, Client, Record


def create_client(user: settings.AUTH_USER_MODEL, **kwargs: Any) -> Client:
    """
    Create an client in the Amiqus system.

    Args:
        user: a Django User instance to register as a Client.
    Kwargs:
       any kwargs passed in are merged into the data dict sent to the
       API. This enables support for additional client properties - e.g
       dob, gender, country, and any others that may change over time.

    """
    data = {
        "name": {
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
        "email": user.email,
    }
    data.update(kwargs)
    response = post("clients", data=data)
    return Client.objects.create_client(user, response)


def create_record(client: Client, check_names: Iterable, **kwargs: Any) -> Record:
    """
    Create a new Record (and child Checks).

    Args:
        client: Client for whom the records are being made. check_names:
        list of strings, each of which is a valid check type.

    Kwargs:
        any kwargs passed in are merged into the data dict sent to the
        API. This enables support for additional record properties -
        e.g. redirect_uri, tags, suppress_form_emails and any other that
        may change over time. See

    Returns a new Record object, and creates the child Check objects.

    """
    data = {
        "client_id": client.amiqus_id,
        "checks": check_names,
        "reset_client_status": True,
        "send_email": True,
        "send_reminder": True,
    }
    # merge in the additional kwargs
    data.update(kwargs)

    # V2 here, this isn't yet implemented. It will error with a 405 method not allowed.
    # response = post("records", data=data)
    # We need to use API v1 for this until they add this method to v2 :) :( :)
    response = post("records", data=data, version=1)
    record = Record.objects.create_record(client=client, raw=response)

    try:
        for response_check in data["checks"]["data"]:
            Check.objects.create_check(record=record, raw=response_check)
    except KeyError:
        # No checks
        pass
    return record
