from contextlib import contextmanager

from hypergen.imports import context
from hypergen_translation.api import get_translations, translate, TRANSLATABLE_ATTRIBUTES, NON_TRANSLATABLE_ELEMENTS

from django.utils.translation import get_language
from django.utils import translation

class TranslationPlugin:
    @contextmanager
    def context(self):
        with context(at="hypergen_translation", translations=get_translations()):
            yield

    @contextmanager
    def wrap_element_init(self, element, children, attrs):
        language_code = get_language()

        if element.__class__.__name__ not in NON_TRANSLATABLE_ELEMENTS:
            for i in range(len(children)):
                if type(children[i]) is str:
                    children[i] = translate(language_code, children[i])

        for k in attrs.keys():
            if k in TRANSLATABLE_ATTRIBUTES and type(attrs[k] is str):
                attrs[k] = translate(language_code, attrs[k])

        yield
