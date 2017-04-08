from django.core.management.base import BaseCommand
from ...models import Check, Report, Applicant


class Command(BaseCommand):

    help = "Pull all Check / Report objects."

    def add_arguments(self, parser):
        parser.add_argument(
            'model',
            choices=['applicant', 'check', 'report'],
            help="Type of model to sync"
        )
        parser.add_argument(
            '--filter',
            nargs='+',
            help="Status field values to filter on"
        )
        parser.add_argument(
            '--exclude',
            nargs='+',
            help="Status field values to exclude"
        )

    def handle(self, *args, **options):

        if options['model'] == 'check':
            model = Check
        elif options['model'] == 'report':
            model = Report
        elif options['model'] == 'applicant':
            model = Applicant

        filters = options['filter']
        excludes = options['exclude']

        objs = model.objects.all()
        objs = objs.filter(status__in=filters) if filters else objs
        objs = objs.exclude(status__in=excludes) if excludes else objs
        objs.pull()
