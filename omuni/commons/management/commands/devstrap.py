import os
from optparse import make_option
from subprocess import call
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from omuni import settings


class Command(BaseCommand):
    help = 'Bootstrap development environment'
    option_list = BaseCommand.option_list + (
            make_option('-i',
                    action='store_true',
                    dest='install',
                    default=False,
                    help="Install project's dependencies"),
            make_option('-t',
                        action='store_true',
                        dest='test',
                        default=False,
                        help="Run tests"),
        )

    def handle(self, *args, **options):
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

        # install python/django requirements
        if options['install']:
            self.stdout.write("### Installing requirements\n")
            call(['pip', 'install', '-r', 'requirements.txt'])

        # sync the db and do South migrations
        try:
            self.stdout.write("### Syncing DB\n")
            call_command('syncdb', interactive=False, migrate=True)
        except:
            raise CommandError('syncdb failed')

        # load fixtures
        self.stdout.write("### Loading fixtures\n")
        for fixture in settings.FIXTURES:
            call_command('loaddata', fixture)

        self.stdout.write("### Development bootstrapping completed successfully\n")