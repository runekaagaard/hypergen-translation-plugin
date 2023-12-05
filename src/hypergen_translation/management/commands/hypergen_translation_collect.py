from pprint import pprint

from django.core.files.storage import import_string
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from hypergen_translation import api
from hypergen_translation.models import *

class Command(BaseCommand):
    help = 'Parses files from settings.HYPERGEN_TRANSLATION_FILES and collects translatable strings.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        assert (module_names := getattr(settings, "HYPERGEN_TRANSLATION_MODULES", None))
        modules = [import_string(x) for x in module_names]

        Occurrence.objects.all().delete()

        for module in modules:
            translations = api.extract_translations(module)
            for value, occurences in translations.items():
                string, _ = String.objects.get_or_create(value=value)
                print(value)
                for file_path, python_path, line_number in occurences:
                    print("    ", file_path, python_path, line_number)
                    Occurrence.objects.create(string=string, file_path=file_path, python_path=python_path,
                                              line_number=line_number)

        self.stdout.write(self.style.SUCCESS("Translations inserted!"))
