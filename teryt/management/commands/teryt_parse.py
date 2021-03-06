"""
./manage.py teryt_parse [xml/zip files] [--update]
------------

Command will parse xml/zip and upload it into teryt database.
Option --update must be used if files have records already existing in database
"""

import zipfile

from django.core.management.base import BaseCommand, CommandError

from teryt.utils_zip import update_database, sort_file_names


class Command(BaseCommand):
    args = '[xml/zip file list]'
    help = 'Import TERYT data from XML/ZIP files prepared by GUS'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            dest='update',
            default=False,
            help='Update exisitng data',
        )
        parser.add_argument('files', nargs='+', type=str)

    def handle(self, *args, **options):
        force_ins = not options['update']
        # Data must be enter in correct order. If you use starred syntax you cannot determine order.
        # We will sort files names to ensure we did not insert street data befoure city data.
        for data_file in sort_file_names(options['files']):
            self.stdout.write('Working on {}'.format(data_file))
            if zipfile.is_zipfile(data_file):
                zfile = zipfile.ZipFile(data_file)
                # we work only on xml
                fname = next(f for f in zfile.namelist() if f.endswith(".xml"))
                with zfile.open(fname) as xml_file:
                    update_database(xml_file, fname, force_ins)
            else:
                with open(data_file) as xml_file:
                    update_database(xml_file, data_file, force_ins)
            self.stdout.write('File {} uploaded'.format(data_file))

        self.stdout.write("Done.")
