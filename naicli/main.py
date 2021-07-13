import sys

from .story import *

def main(argv=sys.argv):
    book = open_story_file("example/grug.story")
    #print(assemble_story_fragments(book.content.story))
    print(assemble_story_datablocks(book.content.story))
    #assemble_story_datablocks(book.content.story)


if __name__ == "__main__":
    main(sys.argv)
