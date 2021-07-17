

from prompt_toolkit.application import Application
from prompt_toolkit.layout.containers import (
    ConditionalContainer,
    Float,
    HSplit,
    VSplit,
    Window,
    WindowAlign,
)
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.key_binding import KeyBindings

from .story_model import *
from .story_control import StoryControl

kb = KeyBindings()

@kb.add("q")
def quit(event):
    event.app.exit()

def launch_editor(story: "Story") -> None:
    layout = Layout(Window(content=StoryControl(story=story), wrap_lines=True))
    app = Application(layout=layout, key_bindings=kb, full_screen=True)
    app.run()
