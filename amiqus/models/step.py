from __future__ import annotations

from django.db import models

from .check import Check
from .form import Form
from .review import Review
from .record import Record


class Step(models.Model):
    """
    A step in a record.

    These can be of type Check or Form and should be associated with one or more
    Reviews once they have been completed.
    """

    id = models.AutoField(primary_key=True)

    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name="steps")
    amiqus_check = models.OneToOneField(
        Check, on_delete=models.CASCADE, null=True, blank=True, related_name="step"
    )
    form = models.OneToOneField(
        Form, on_delete=models.CASCADE, null=True, blank=True, related_name="step"
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, null=True, blank=True, related_name="step"
    )
