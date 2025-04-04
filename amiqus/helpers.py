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

    https://developers.amiqus.co/aqid/api-reference.html#tag/Records/operation/post-records
    """
    # Checks to have structured like so 'check.photo_id'
    # custom_forms? message?
    data = {
        "client": client.amiqus_id,
        "steps": [{"type": check_name} for check_name in check_names],
        "notification": "email",
        "reminder": True,
    }

    # Merge in the additional kwargs
    data.update(kwargs)

    response = post("records", data=data)
    record = Record.objects.create_record(client=client, raw=response)

    try:
        for step in data["steps"]:
            if step.get("check"):
                Check.objects.create_check(record=record, raw=step["check"])
    except KeyError:
        # No checks
        pass
    return record
