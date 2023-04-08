"""
Amiqus webhook handler.

The Amiqus API will send a webhook to the configured URL when an event
occurs, which we then use to update the relevant object.

"""
from __future__ import annotations

import json
import logging

from django.http import HttpRequest, HttpResponse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

from .decorators import verify_signature
from .models import Check, Event, Record
from .settings import LOG_EVENTS

logger = logging.getLogger(__name__)


@csrf_exempt
@verify_signature()
def status_update(request: HttpRequest) -> HttpResponse:
    """
    Handle event callbacks from the API.

    This is the request handler which does little other than log the
    request and call the _webhook function which does the processing.
    Done like this to make it easier to test without having to set up
    request objects.

    NB This view function will always return a 200 status - in order to
    prevent Amiqus from endlessly retrying. The only exceptions to this
    are caused by the verify_signature decorator - if it cannot verify
    the callback, then it will return a 403 - which should be ok, as if
    Amiqus sends the request it should never fail...

    """
    received_at = now()
    logger.debug("Received Amiqus callback: %s", request.body)
    data = json.loads(request.body)
    trigger = data["trigger"]
    alias = trigger["alias"]
    entity_type = alias.split(".")[0]
    event = Event(received_at=received_at)

    try:
        resource = event.parse(data, entity_type=entity_type).resource
        resource.update_status(event)
        if LOG_EVENTS:
            event.save()
        return HttpResponse("Update processed.")
    except KeyError as ex:
        logger.warning("Missing Amiqus event content.", exc_info=ex)
        return HttpResponse("Unexpected event content.")
    except ValueError:
        logger.warning("Unknown Amiqus resource type: %s", event.resource_type)
        return HttpResponse("Unknown resource type.")
    except Record.DoesNotExist:
        # TODO(source-of-truth) Create Record when *new* request is spawned from Amiqus
        # Missing Records can be synchronised as we utilise a reference shared
        # between the user, and Amiqus itself.
        logger.warning("Amiqus record does not exist: %s", event.amiqus_id)
        # 1. Get Record from API.
        # 2. Get Client attached to Record
        # 3. Use their reference to match with a user on system
        # 4. Create record as normal
        return HttpResponse("Record not found.")
    except Check.DoesNotExist:
        logger.warning("Amiqus check does not exist: %s", event.amiqus_id)
        return HttpResponse("Check not found.")
    except Exception:  # noqa: B902
        logger.exception("Amiqus update could not be processed.")
        return HttpResponse("Unknown error.")
