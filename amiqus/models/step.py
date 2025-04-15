from __future__ import annotations
import logging

from django.db import models

from .base import BaseModel, BaseQuerySet
from .check import Check
from .form import Form
from .review import Review

logger = logging.getLogger(__name__)


class StepQuerySet(BaseQuerySet):
    def create_step(self, check: Check, raw: dict) -> Step:
        """Create a new Step from the raw JSON."""
        logger.debug("Creating new Amiqus step from JSON: %s", raw)
        return Step(amiqus_check=check).parse(raw).save()


class Step(BaseModel):
    """
    A step in a record.

    These can be of type Check or Form and should be associated with one or more
    Reviews once they have been completed.
    """

    amiqus_check = models.OneToOneField(
        Check, on_delete=models.CASCADE, null=True, blank=True, related_name="step"
    )
    form = models.OneToOneField(
        Form, on_delete=models.CASCADE, null=True, blank=True, related_name="step"
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, null=True, blank=True, related_name="step"
    )

    objects = StepQuerySet.as_manager()
