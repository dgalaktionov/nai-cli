import click

from prompt_toolkit import prompt

echo = click.echo_via_pager

def start_prompt():
    while 1:
        user_input = prompt('>')
        #message = click.edit(user_input)
        #print(message)
        echo(user_input)