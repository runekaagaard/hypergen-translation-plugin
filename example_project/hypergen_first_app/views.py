# Interesting stuff can be imported more precisely from the template, liveview and context modules. For now lets
# get it all :)
from hypergen.imports import *
from hypergen.template import component
from hypergen_translation.plugins import TranslationPlugin

from contextlib import contextmanager
import codecs

from django.utils import translation

# Templates - as your app grows you probably want to move them to a templates.py file.

@contextmanager  # base templates must be context managers that yields where the main content will be.
def base_template():
    translation.activate("da")
    """
    This base template is meant to be shared between your views.
    """
    doctype()  # all html elements are available as functions.
    with html():  # elements can nest.
        with head():
            if title:
                title(
                    "Hello hypergen_first_app")  # arguments to elements becomes the html innerText of the element.
            link("https://unpkg.com/simpledotcss@2.0.7/simple.min.css")  # include all you html5 boilerplate.
        with body():  # warning, don't set the target_id directly on the body element, does not work!
            h1("Hello hypergen_first_app", title="translate this")
            p(i("Congratulations on installing your very first Django Hypergen app!")
             )  # elements can take elements.

            with div(id_="content"):  # see target_id below. Do NOT set the id_ on the body() tag!
                # The html triggered inside your views will appear here.
                yield

            h1("Where to go from here?")
            with ul():
                li(
                    "Play around with the source at",
                    code("./hypergen_first_app/views.py"),
                    sep=" ",  # arguments are joined by a " " separator.
                )
                li("Read the", a("getting started", href="https://hypergen.it/gettingstarted/begin/"), "guide",
                   sep=" ")
                li("Check out the full", a("documentation", href="https://hypergen.it/documentation/"), sep=" ")
                li("Drop by and", a("say hi", href="https://github.com/runekaagaard/django-hypergen/discussions"),
                   "- we would love to talk to you!", sep=" ")
                li("Submit ",
                   a("bug reports and feature requests",
                     href="https://github.com/runekaagaard/django-hypergen/issues"))  # kwargs becomes attributes.
                li("Go crazy 24/7!")

base_template.target_id = "content"  # Makes the base_template know where it's inner content is nested.

def content_template(encrypted_message=None):
    """
    This template is specific to your view and the actions belonging to it. Composes just like React functions.
    """
    p("Top secret agent? Encrypt your message with a super secret key:")
    input_(
        id_="message",
        # call "my_action" on each oninput event.
        # callback() takes all normal python datatypes and hypergen html elements as input.
        oninput=callback(my_action, THIS),  # 'THIS' means the value of the element it self.
    )
    pre(code(encrypted_message if encrypted_message else "Type something, dammit!"))

# Views - one view normally have multiple actions.

@liveview(perm=NO_PERM_REQUIRED, base_template=base_template, user_plugins=[TranslationPlugin()])
def my_view(request):
    """
    Views renders html and binds frontend events to actions.
    """
    content_template()
    p("stines nye text 1111111111111111111111")
    hprint(context.hypergen_translation["translations"])

@contextmanager
def base_template2():
    translation.activate("da")
    yield

base_template2.target_id = "bbb"

@liveview(perm=NO_PERM_REQUIRED, base_template=base_template2, user_plugins=[TranslationPlugin()])
def my_view2(request):
    p("ccccc")

# Actions - if you have a lot, move them to a actions.py file.

@action(perm=NO_PERM_REQUIRED, target_id="content")
def my_action(request, message):
    """
    Actions processes frontend events.
    
    This action tells the frontend to put the output of content_template into the 'content' div.

    The 'message' arg is the value of the <input> element.
    """
    content_template(codecs.encode(message if message is not None else "", 'rot_13'))

def extract_THIS(items):
    someotherguy("DONT ADD THIS!!!!!!!")

    def does_inner_work(ggg):
        p("Wow1", title="INNER1")

        def does_inner_wor2k(ggg):
            p("Wow1", title="INNER2")

            def does_inner_wor3k(ggg):
                p("Wow1", title="INNER3")

        def inner_XXXX(aaa):
            p("XXXXXXXXXx", alt="INNER4")

    for item in items:
        img(src="foo.svg", alt="This needs to be here!!")

    alsocomponent("This we must have!!!")

    script("1NOOOOOOH")
    style("1NOOOOOOH")

@component
def alsocomponent(title):
    h2(title)
    p("I'm doing it")
    p("Wow1", title="INNER3")
