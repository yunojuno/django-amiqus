from __future__ import annotations

from typing import Any

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


def create_record(client: Client, steps: list[dict[str, Any]]) -> Record:
    """
    Create a new Record (and child Steps).

    Args:
        client: Client for whom the records are being made.
        steps: list of dicts, each of which is a step in the record. These
        should be structured according to the documentation linked below. Example:
        [
            {
                "type": "check.dummy",
                "preferences": {"report_type": "standard"}
            }
        ]

    Returns a new Record object, and creates the child Steps.

    https://developers.amiqus.co/aqid/api-reference.html#tag/Records/operation/post-records

    """
    # We can add a custom message to the link here if we like, with a "message"
    # key in the data dict.
    data = {
        "client": client.amiqus_id,
        "notification": "email",
        "reminder": True,
    }

    data["steps"] = steps

    response = post("records", data=data)
    record = Record.objects.create_record(client=client, raw=response)

    for step in data["steps"]:
        if step.get("check"):
            Check.objects.create_check(record=record, raw=step["check"])

    return record
