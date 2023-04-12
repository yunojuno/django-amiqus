from __future__ import annotations

import logging

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..settings import scrub_check_data
from .base import BaseQuerySet, BaseStatusModel
from .record import Record

logger = logging.getLogger(__name__)


class CheckQuerySet(BaseQuerySet):
    """Check model queryset."""

    def create_check(self, record: Record, raw: dict) -> Check:
        """Create a new Check from the raw JSON."""
        logger.debug("Creating new Onfido check from JSON: %s", raw)
        return Check(user=record.user, amiqus_record=record).parse(raw).save()


class Check(BaseStatusModel):
    """Specific checks associated with a Record."""

    class CheckStatus(models.TextChoices):
        """Combined list of states values for record / check."""

        PENDING = ("pending", _("Pending"))
        SUBMITTED = ("submitted", _("Submitted"))
        ACCEPTED = ("accepted", _("Accepted"))
        REJECTED = ("rejected", _("Cancelled"))
        REFER = ("refer", _("Refer"))
        FAILED = ("failed", _("Failed"))
        PAUSED = ("paused", _("Paused"))

    base_href = "checks"

    class CheckType(models.TextChoices):
        # https://documentation.onfido.com/#check-names-in-api
        DOCUMENT = ("document", "Document")
        DOCUMENT_WITH_ADDRESS_INFORMATION = (
            "document_with_address_information",
            "Document with Address Information",
        )
        DOCUMENT_WITH_DRIVING_LICENCE_INFORMATION = (
            "document_with_driving_licence_information",
            "Document with Driving Licence Information",
        )
        FACIAL_SIMILARITY_PHOTO = (
            "facial_similarity_photo",
            "Facial Similarity (photo)",
        )
        FACIAL_SIMILARITY_PHOTO_FULLY_AUTO = (
            "facial_similarity_photo_fully_auto",
            "Facial Similarity (auto)",
        )
        FACIAL_SIMILARITY_VIDEO = (
            "facial_similarity_video",
            "Facial Similarity (video)",
        )
        KNOWN_FACES = ("known_faces", "Known Faces")
        IDENTITY_ENHANCED = ("identity_enhanced", "Identity (enhanced)")
        WATCHLIST_ENHANCED = ("watchlist_enhanced", "Watchlist (enhanced)")
        WATCHLIST_STANDARD = ("watchlist_standard", "Watchlist")
        WATCHLIST_PEPS_ONLY = ("watchlist_peps_only", "Watchlist (PEPs only)")
        WATCHLIST_SANCTIONS_ONLY = (
            "watchlist_sanctions_only",
            "Watchlist (sanctions only)",
        )
        PROOF_OF_ADDRESS = ("proof_of_address", "Proof of Address")
        RIGHT_TO_WORK = ("right_to_work", "Right to Work")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text=_(
            "The Django user (denormalised from Client to make navigation easier)."
        ),  # noqa
        related_name="amiqus_checks",
    )
    amiqus_record = models.ForeignKey(
        Record,
        on_delete=models.CASCADE,
        help_text=_("Record to which this check is attached."),
        related_name="checks",
    )
    check_type = models.CharField(
        max_length=50,
        choices=CheckType.choices,
        help_text=_(
            "The name of the check - see https://documentation.onfido.com/#checks"
        ),
    )

    objects = CheckQuerySet.as_manager()

    def __str__(self) -> str:
        return "{} for {}".format(self.get_check_type_display().capitalize(), self.user)

    def __repr__(self) -> str:
        return "<Check id={} type='{}' user_id={}>".format(
            self.id, self.check_type, self.user.id
        )

    def parse(self, raw_json: dict) -> Check:
        """
        Parse the raw value out into other properties.

        Before parsing the data, this method will call the
        scrub_check_data function to remove sensitive data
        so that it is not saved into the local object.

        """
        super().parse(scrub_check_data(raw_json))
        self.check_type = self.raw["type"]
        self.status = self.raw["status"]
        # Once the V2 API has been implemented, this won't be necessary.
        if isinstance(self.status, int):
            self.status = self.deprecated_status_mapper(self.status)
        return self

    def deprecated_status_mapper(self, status: int) -> CheckStatus | None:
        """
        Return a v2 status for a v1 endpoint.

        V1 endpoint returns an integer based status value.
        V2 endpoint returns and uses a text based status value.
        This function patches the two.
        """
        return {
            0: self.CheckStatus.PENDING.value,  # type: ignore[attr-defined]
            1: self.CheckStatus.SUBMITTED.value,  # type: ignore[attr-defined]
            2: self.CheckStatus.ACCEPTED.value,  # type: ignore[attr-defined]
            3: self.CheckStatus.REJECTED.value,  # type: ignore[attr-defined]
            4: self.CheckStatus.REFER.value,  # type: ignore[attr-defined]
            5: self.CheckStatus.FAILED.value,  # type: ignore[attr-defined]
            6: self.CheckStatus.PAUSED.value,  # type: ignore[attr-defined]
        }[status]
