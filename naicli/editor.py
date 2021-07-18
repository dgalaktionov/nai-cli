#import asyncio

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
from prompt_toolkit.key_binding.key_processor import KeyPress, KeyPressEvent

from .story_model import *
from .story_control import StoryControl

kb = KeyBindings()

@kb.add("q")
def quit(event):
    event.app.exit()

# TODO get these boring bindings outta here
def get_content(event: KeyPressEvent) -> "StoryControl":
    return event.app.layout.container.content

@kb.add("right")
def cursor_right(event):
    get_content(event).move_cursor_right()

@kb.add("left")
def cursor_left(event):
    get_content(event).move_cursor_left()

@kb.add("up")
def cursor_up(event):
    get_content(event).move_cursor_up()

@kb.add("down")
def cursor_down(event):
    get_content(event).move_cursor_down()

def launch_editor(story: "Story") -> None:
    sc = StoryControl(story=story)
    layout = Layout(Window(content=sc, wrap_lines=True))
    app = Application(layout=layout, key_bindings=kb, full_screen=True)
    app.run()
    