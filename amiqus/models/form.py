from __future__ import annotations

import logging

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import BaseModel, BaseQuerySet
from .record import Record


logger = logging.getLogger(__name__)


class FormQuerySet(BaseQuerySet):
    def create_form(self, record: Record, raw: dict) -> Form:
        """Create a new Form from the raw JSON."""
        logger.debug("Creating new Amiqus form from JSON: %s", raw)
        return Form(user=record.user, amiqus_record=record).parse(raw).save()


class Form(BaseModel):
    """Specific Forms associated with a Record."""

    reference = models.CharField(max_length=255, unique=True, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text=_(
            "The Django user (denormalised from Client to make navigation easier)."
        ),  # noqa
        related_name="amiqus_forms",
    )

    objects = FormQuerySet.as_manager()
