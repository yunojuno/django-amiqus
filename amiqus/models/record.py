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

        # First create and save the base record with required relations
        record = Record.objects.create(
            user=client.user,
            client=client,
            amiqus_id=raw["id"],
            status=raw["status"],
            created_at=date_parse(raw["created_at"]),
            perform_url=raw.get("perform_url"),
            raw=raw,
        )

        # Now handle the checks/steps after record is saved
        from .check import Check

        for step in raw.get("steps", []):
            if step.get("check"):
                # Use get_or_create but with the saved record
                Check.objects.get_or_create(
                    amiqus_id=step["check"],
                    amiqus_record=record,
                    check_type=step["type"],
                    defaults={
                        "user": record.user,
                    },
                )

        return record


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
