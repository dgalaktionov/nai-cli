import click

from prompt_toolkit import print_formatted_text as print
from prompt_toolkit.history import DummyHistory
from .overrides.prompt import prompt, PromptSession
#from prompt_toolkit import prompt, PromptSession

from . import constants


# https://github.com/pallets/click/issues/1905
print_pager = print if constants.WINDOWS else click.echo_via_pager

def start_prompt(initial_text: str = "") -> None:
    s = PromptSession(multiline=True, history=DummyHistory(), enable_undo_redo=False)
    text = initial_text

    while 1:
        text += s.prompt(text)
        click.clear()