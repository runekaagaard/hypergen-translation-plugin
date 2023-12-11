Hypergen Translation Plugin
===========================

Translation plugin for `Django Hypergen <https://github.com/runekaagaard/django-hypergen/>`_. Processes the AST
of Hypergen template python files and inserts them into the database for translation.

Provides the `TranslationPlugin` that makes Hypergen liveviews and actions translatable based on the current
django translation language.

Usage
=====

Installation::

    pip install hypergen-translation-plugin

Change `settings.py`::

    # Add to installed apps:
    INSTALLED_APPS = [
        ...
        'hypergen_translation'
    ]

    # Select which importable modules to look for translatable strings in.
    HYPERGEN_TRANSLATION_MODULES = ["hypergen_first_app.views"]
    # The base dir of the git/whatever project.
    HYPERGEN_TRANSLATION_PROJECT_DIR = BASE_DIR.parent
    # Optionally display link directly to file and linenumber for each translation occurence. 
    HYPERGEN_TRANSLATION_GITHUB = "https://github.com/runekaagaard/hypergen-translation-plugin"
    # Optionally link to another branch than main.´ on github.
    HYPERGEN_TRANSLATION_BRANCH = "dev"

Collection collections and store it in the database::

    python manage.py hypergen_translation_collect

Then edit in the admin.

Add plugin to liveviews and actions::

    from hypergen_translation.plugins import TranslationPlugin

    @liveview(..., user_plugins=[TranslationPlugin()])
    def my_view(request):
        p("translate this!")
