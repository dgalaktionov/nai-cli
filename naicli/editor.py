

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

from .story_model import *
from .story_control import StoryControl

def launch_editor(story: "Story") -> None:
    layout = Layout(Window(content=StoryControl(story=story), wrap_lines=True))
    app = Application(layout=layout, full_screen=True)
    app.run()
