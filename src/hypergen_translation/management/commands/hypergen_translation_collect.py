from django.core.files.storage import import_string
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from hypergen_translation import api

class Command(BaseCommand):
    help = 'Parses files from settings.HYPERGEN_TRANSLATION_FILES and collects translatable strings.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        assert (module_names := getattr(settings, "HYPERGEN_TRANSLATION_MODULES", None))
        modules = [import_string(x) for x in module_names]

        for module in modules:
            translations = api.extract_translations(module)
            from pprint import pprint
            pprint({k: [".".join(x) for x in v] for k, v in translations.items()})

        self.stdout.write(self.style.SUCCESS("I rule!"))
