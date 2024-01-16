from django.core.files.storage import import_string
from django.core.management.base import BaseCommand
from django.conf import settings

from hypergen_translation import api

class Command(BaseCommand):
    help = 'Translates untranslated strings with deepL.'

    def add_arguments(self, parser):
        parser.add_argument('source_lang', type=str, help='Source language code (e.g., "en")')
        parser.add_argument('target_lang', type=str, help='Target language code (e.g., "de")')

    def handle(self, *args, **options):
        source_lang = options['source_lang']
        target_lang = options['target_lang']

        n = api.deepl_translate(source_lang, target_lang)

        self.stdout.write(self.style.SUCCESS(f"Translated {n} strings with deepL"))
