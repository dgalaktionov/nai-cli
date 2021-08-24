from typing import List

from .story_model import *
from .story import *
from .encoder import *
from .util import *

# TODO make it a setting
MAX_TOKENS = 2048
ESTIMATE_TOKEN_LENGTH = 14 # generous estimate, just don't try it with a story full of Schwarzeneggers yet

def build_context(content: "Content") -> List[int]:
    encoder: "Encoder" = get_encoder()
    story: "Story" = content.story
    fragments: List["Fragment"] = story.fragments
    text_length: int = fragment_to_position(story, len(fragments))
    
    # we use an heuristic to approximate where should we start tokenizing
    # in future versions, I hope to replace it with proper line and word segmentation
    starting_position = max(0, text_length - MAX_TOKENS*ESTIMATE_TOKEN_LENGTH)
    story_text: str = assemble_story_fragments(fragments[position_to_fragment(story, starting_position)[0]:])
    tokens: List[int] = encoder.encode(story_text)
    return tokens[-MAX_TOKENS:]
