import sys

from . import repl
from .story import *

def main(argv=sys.argv):
    book = open_story_file("example/grug.story")
    #repl.echo(assemble_story_fragments(book.content.story))
    #repl.print_pager(assemble_story_datablocks(book.content.story))
    #assemble_story_datablocks(book.content.story)
    repl.start_prompt(assemble_story_datablocks(book.content.story))
    # bigtext = ""
    # with open("../book.txt") as bigfile:
        # bigtext = bigfile.read()
        
    #repl.start_prompt(bigtext)
    

if __name__ == "__main__":
    main(sys.argv)
