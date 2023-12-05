import ast, re, inspect, os

from hypergen.template import base_element, Component

from django.utils.cache import defaultdict
from django.conf import settings

TRANSLATABLE_ATTRIBUTES = {
    "alt", "placeholder", "title", "label", "aria-label", "aria-placeholder", "aria-describedby", "value"
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

def extract_translations(module):
    source = inspect.getsource(module)
    tree = ast.parse(source)
    visitor = ASTVisitor(module)
    visitor.visit(tree)

    return visitor.translations
