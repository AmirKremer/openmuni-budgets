import os
from optparse import make_option
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from openbudget.settings import local as settings


class Command(BaseCommand):
    help = 'Bootstrap development environment'
    option_list = BaseCommand.option_list + (
            make_option(
                '-t',
                action='store_true',
                dest='test',
                default=False,
                help="Run tests"
            ),
            make_option(
                '-i',
                action='store_true',
                dest='interactive',
                default=False,
                help="Enable syncdb related input"
            ),
            make_option(
                '-m',
                action='store_true',
                dest='migrate',
                default=False,
                help="Run DB migrations"
            )
        )

    def handle(self, *args, **options):
        # say hello
        self.stdout.write("### DON'T PANIC\n")
        self.stdout.write("### Bootstrapping development environment\n")

        # remove current database file
        db_file_path = settings.DATABASES['default']['NAME']

        if os.path.isfile(db_file_path):
            try:
                self.stdout.write("### Removing DB\n")
                os.remove(db_file_path)
            except IOError as e:
                raise CommandError(e)

        # sync the db and do South migrations
        try:
            self.stdout.write("### Syncing DB\n")
            call_command('syncdb', **{
                'interactive': options['interactive'],
                'migrate': options['migrate']
            })
        except:
            raise CommandError('syncdb failed')

        # load fixtures
        self.stdout.write("### Loading fixtures\n")
        for fixture in settings.DEVSTRAP['FIXTURES']:
            call_command('loaddata', fixture)

        # run tests
        if options['test']:
            call_command('test', *settings.DEVSTRAP['TESTS'])

        # build the search index
        call_command(
            'rebuild_index',
            verbosity=0,
            interactive=False
        )
        self.stdout.write('### Just built the search index\n')

        # wave goodbye
        self.stdout.write("### Development bootstrapping completed successfully\n")
