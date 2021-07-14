import click

from prompt_toolkit import prompt

from . import constants

# https://github.com/pallets/click/issues/1905
print_pager = print if constants.WINDOWS else click.echo_via_pager

def start_prompt():
    while 1:
        user_input = prompt('>')
        #message = click.edit(user_input)
        print(user_input)