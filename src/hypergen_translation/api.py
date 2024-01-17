import ast, re, inspect, os, json

from hypergen.imports import context
from hypergen.template import base_element, Component
from hypergen_translation.models import Occurrence, String, Translation, Language

import requests

from django.utils.cache import defaultdict
from django.conf import settings
from django.core.cache import cache

TRANSLATABLE_ATTRIBUTES = {
    "alt", "placeholder", "title", "label", "aria-label", "aria-placeholder", "aria-describedby"
}
NON_TRANSLATABLE_ELEMENTS = {
    "meta", "link", "base", "title", "style", "script", "noscript", "img", "iframe", "embed", "object", "param",
    "source", "track", "area", "canvas", "audio", "video", "input", "button", "select", "option", "optgroup",
    "textarea", "keygen", "output", "progress", "meter", "fieldset", "legend", "br", "hr"
}

class ASTVisitor(ast.NodeVisitor):
    def __init__(self, module):
        self.module = module
        self.stack = [module.__name__]
        self.translations = defaultdict(set)
        self.is_translatable = re.compile(r'[a-zA-Z]', re.UNICODE)

        super().__init__()

    def visit_ClassDef(self, node):
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def visit_FunctionDef(self, node):
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def visit_Call(self, node):
        # It it's not
        if not (
                # It's a func with an id
                hasattr(node, "func") and hasattr(node.func, "id") and hasattr(self.module, node.func.id)
                # And it's either
                and (
                    # A class subclassing base_element or Component
                    (inspect.isclass(getattr(self.module, node.func.id)) and
                     issubclass(getattr(self.module, node.func.id), (base_element, Component)))
                    # OR a function marked with hypergen_is_component
                    or (inspect.isfunction(getattr(self.module, node.func.id)) and
                        getattr(getattr(self.module, node.func.id), "hypergen_is_component", False) is True))):
            # Then stop.
            self.generic_visit(node)
            return

        # Translation strings from constant args not in list.
        if node.func.id not in NON_TRANSLATABLE_ELEMENTS:
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    if self.is_translatable.search(arg.value):
                        self.add_string(arg.value, arg.lineno)
        # Translation strings from constant args in list.
        for keyword in node.keywords:
            if keyword.arg in TRANSLATABLE_ATTRIBUTES and type(keyword.value) is ast.Constant and type(
                    keyword.value.value) is str:
                if self.is_translatable.search(keyword.value.value):
                    self.add_string(keyword.value.value, keyword.value.lineno)

        # Continue visit.
        self.generic_visit(node)

    def add_string(self, s, lineno):
        self.translations[s].add((
            os.path.relpath(self.module.__file__, start=settings.HYPERGEN_TRANSLATION_PROJECT_DIR),
            ".".join(self.stack),
            lineno,
        ))

def collect_translations(module):
    source = inspect.getsource(module)
    tree = ast.parse(source)
    visitor = ASTVisitor(module)
    visitor.visit(tree)

    return visitor.translations

def save_translations(translations):
    Occurrence.objects.all().delete()
    for value, occurences in translations.items():
        string, _ = String.objects.get_or_create(value=value)
        for file_path, python_path, line_number in occurences:
            Occurrence.objects.create(string=string, file_path=file_path, python_path=python_path,
                                      line_number=line_number)

def set_translations():
    translations = {}
    for translation in Translation.objects.all():
        if translation.language.language_code not in translations:
            translations[translation.language.language_code] = {}
        translations[translation.language.language_code][translation.string.value] = translation.value

    cache.set("hypergen_translations", translations)

def get_translations():
    translations = cache.get("hypergen_translations")
    if translations is None:
        set_translations()
        translations = cache.get("hypergen_translations")
        assert translations is not None, "cache mechanism error"

    return translations

def translate(language_code, s):
    try:
        return context["hypergen_translation"]["translations"][language_code][s]
    except:
        context["hypergen_translation"]["missing"].add(s)
        return s

def add_missing_strings(strings):
    String.objects.bulk_create([String(value=x) for x in strings])

def deepl_translate(source_lang, target_lang):
    language = Language.objects.get(language_code=target_lang)
    translated_strings = Translation.objects.filter(language=language).values_list("string__pk", flat=True)
    missing = list(String.objects.exclude(pk__in=translated_strings).values_list("pk", "value"))

    response = requests.post(
        'https://api.deepl.com/v2/translate',
        headers={'Authorization': f'DeepL-Auth-Key {settings.HYPERGEN_TRANSLATION_DEEPL_API_KEY}'},
        data={
            'text': [x[1] for x in missing],
            'source_lang': source_lang,
            'target_lang': target_lang
        },
    )

    if response.status_code == 200:
        Translation.objects.bulk_create([
            Translation(string_id=string_id, language=language, value=translation["text"])
            for (string_id, _), translation in zip(missing,
                                                   response.json()['translations'])
        ])

        return len(missing)
    else:
        print(response.json())
        raise Exception("Could not translate text.")
