from __future__ import annotations

import logging

from dateutil.parser import parse as date_parse
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class Event(models.Model):
    """Used to record callback events received from the API."""

    amiqus_id = models.CharField(
        "Amiqus ID",
        max_length=40,
        help_text=_("The Amiqus ID of the related resource."),
    )
    resource_type = models.CharField(
        max_length=20, help_text=_("The resource_type returned from the API callback.")
    )
    action = models.CharField(
        max_length=20, help_text=_("The event name as returned from the API callback.")
    )
    status = models.CharField(
        max_length=20, help_text=_("The status of the object after the event.")
    )
    completed_at = models.DateTimeField(
        help_text=_("The timestamp returned from the Amiqus API."),
        blank=True,
        null=True,
    )
    received_at = models.DateTimeField(
        help_text=_("The timestamp when the server received the event."),
    )
    raw = models.JSONField(
        help_text=_("The raw JSON returned from the API."), blank=True, null=True
    )

    class Meta:
        ordering = ["completed_at"]

    def __str__(self) -> str:
        return "{} event occurred on {}.{}".format(
            self.action, self.resource_type, self.amiqus_id
        )

    def __repr__(self) -> str:
        return "<Event id={} action='{}' amiqus_id='{}.{}'>".format(
            self.id, self.action, self.resource_type, self.amiqus_id
        )

    def _resource_manager(self) -> models.Manager:
        """Return the appropriate model manager for the resource_type."""
        if self.action not in (
            "record.bounced",
            "record.created",
            "record.updated",
            "record.finished",
            "record.reviewed",
            "client.created",
            "client.record",
            "client.updated",
            "client.status",
        ):
            raise ValueError(f"Unknown resource action: {self.action}")
        if self.resource_type == "record":
            from .record import Record

            return Record.objects
        elif self.resource_type == "client":
            from .client import Client

            return Client.objects

    @property
    def resource(self) -> models.Manager:
        """Return the underlying Record or Check resource."""
        return self._resource_manager().get(amiqus_id=self.amiqus_id)

    @property
    def user(self) -> settings.AUTH_USER_MODEL:
        """Return the user to whom the resource refers."""
        return self.resource.user

    def parse(self, raw_json: dict, *, entity_type: str) -> Event:
        """Parse the raw value out into other properties."""
        self.raw = raw_json
        data = self.raw["data"]
        trigger = self.raw["trigger"]
        self.resource_type = entity_type
        self.action = trigger["alias"]
        obj = data[entity_type]
        self.amiqus_id = obj["id"]
        # self.status = obj["status"]
        self.completed_at = date_parse(trigger["triggered_at"])
        return self
