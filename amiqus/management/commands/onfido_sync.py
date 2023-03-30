from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand

from ...models import Check, Client, Record


class Command(BaseCommand):
    help = "Pull all Record / Check objects."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "model",
            choices=["client", "record", "check"],
            help="Type of model to sync",
        )
        parser.add_argument(
            "--filter", nargs="+", help="Status field values to filter on"
        )
        parser.add_argument(
            "--exclude", nargs="+", help="Status field values to exclude"
        )

    def handle(self, *args: Any, **options: Any) -> None:
        if options["model"] == "record":
            model = Record
        elif options["model"] == "check":
            model = Check
        elif options["model"] == "client":
            model = Client

        filters = options["filter"]
        excludes = options["exclude"]

        objs = model.objects.all()
        objs = objs.filter(status__in=filters) if filters else objs
        objs = objs.exclude(status__in=excludes) if excludes else objs
        objs.pull()
