from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from dateutil.parser import parse as date_parse
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import BaseQuerySet, BaseStatusModel

if TYPE_CHECKING:
    from .client import Client

logger = logging.getLogger(__name__)


class RecordQuerySet(BaseQuerySet):
    """Record model manager."""

    def create_record(self, client: Client, raw: dict) -> Record:
        """Create a new Record object from the raw JSON."""
        logger.debug("Creating new Amiqus record from JSON: %s", raw)
        return Record(user=client.user, client=client).parse(raw).save()


class Record(BaseStatusModel):
    """The state of an individual record made against an Client."""

    base_href = "records"

    class RecordStatus(models.TextChoices):
        PENDING = ("pending", _("Pending"))
        STARTED = ("started", _("Started"))
        COMPLETE = ("complete", _("Complete"))
        INCOMPLETE = ("incomplete", _("Incomplete"))
        WAITING = ("waiting", _("Waiting"))
        FAILED = ("failed", _("Failed"))
        EMPTY = ("empty", _("Empty"))
        AMENDMENTS = ("amendments", _("Amendments"))
        PAUSED = ("paused", _("Paused"))
        REVIEWED = ("reviewed", _("Reviewed"))
        UNKNOWN = ("unknown", _("Unknown"))

    class RecordType(models.TextChoices):
        CREDIT = "credit"
        CRIMINAL_RECORD = "criminal_record"
        DOCUMENT = "document"
        DUMMY = "dummy"
        IDENTITY = "identity"
        THORNTONS_ONBOARDING = "thorntons_onboarding"
        WATCHLIST = "watchlist"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text=_(
            "The Django user (denormalised from Client to make navigation easier)."
        ),  # noqa
        related_name="amiqus_records",
    )

    perform_url = models.CharField(max_length=200, blank=True, null=True)

    status = models.CharField(
        max_length=20,
        help_text=_("The current status of the record / check (from API)."),
        choices=RecordStatus.choices,
        db_index=True,
        blank=True,
        null=True,
    )

    client = models.ForeignKey(
        "amiqus.Client",
        on_delete=models.CASCADE,
        help_text=_("The client for whom the record is being made."),
        related_name="records",
    )

    objects = RecordQuerySet.as_manager()

    def __str__(self) -> str:
        return f"Amiqus record for {self.user}"

    def __repr__(self) -> str:
        return (
            f"<Record amiqus_id={self.amiqus_id} id={self.id} user_id={self.user_id}>"
        )

    def parse(self, raw_json: dict) -> Record:
        """Parse the raw value out into other properties."""
        self.raw = raw_json
        self.amiqus_id = self.raw["id"]
        self.status = self.raw["status"]
        if isinstance(self.status, int):
            self.status = self.deprecated_status_mapper(self.status)
        self.created_at = date_parse(self.raw["created_at"])
        try:
            self.perform_url = self.raw["links"]["perform"]
        except KeyError:
            # There's no url to perform as part of this request.
            pass
        try:
            from .check import Check

            # Loop through all checks in the response, and update our downstream models.
            for response_check in self.raw["checks"]["data"]:
                check, _ = Check.objects.get_or_create(
                    amiqus_id=response_check["id"],
                    user=self.user,
                    check_type=response_check["type"],
                    amiqus_record=self,
                )
                check.parse(response_check)
                # Strictly speaking we shouldn't do this here.
                # There's currently no API endpoint to fire a sequential update.
                # So we pick the fields from the record fetch.
                check.save()
        except KeyError:
            # We have no checks
            pass
        return self

    def deprecated_status_mapper(self, status: int) -> RecordStatus | None:
        """
        Return a v2 status for a v1 endpoint.

        V1 endpoint returns an integer based status value. V2 endpoint
        returns and uses a text based status value. This function
        patches the two.

        """
        CHECK_STATUS_MAP = {
            0: self.RecordStatus.PENDING.value,  # type: ignore[attr-defined]
            1: self.RecordStatus.STARTED.value,  # type: ignore[attr-defined]
            2: self.RecordStatus.UNKNOWN.value,  # type: ignore[attr-defined]
            3: self.RecordStatus.UNKNOWN.value,  # type: ignore[attr-defined]
            4: self.RecordStatus.UNKNOWN.value,  # type: ignore[attr-defined]
            5: self.RecordStatus.FAILED.value,  # type: ignore[attr-defined]
            6: self.RecordStatus.UNKNOWN.value,  # type: ignore[attr-defined]
            7: self.RecordStatus.UNKNOWN.value,  # type: ignore[attr-defined]
            8: self.RecordStatus.REVIEWED.value,  # type: ignore[attr-defined]
        }
        return CHECK_STATUS_MAP[status]
