import pytest

from naicli.encoder import *

@pytest.fixture(scope="module")
def encoder():
    return get_encoder()

@pytest.fixture(scope="module")
def large_text():
    text: str = ""
    
    with open("tests/frankenstein.txt", "r", encoding="utf-8") as text_file:
        text = text_file.read()
    
    return text

def test_encoder(encoder):
    assert encoder != None
    assert len(encoder.encoder) == len(encoder.decoder) > 0

def test_large_text(encoder, large_text):
    tokens = encoder.encode(large_text)
    assert len(tokens) > 0
    assert encoder.decode(tokens) == large_text

def test_ellipsis(encoder):
    tokens = encoder.encode("… …")
    assert tokens == [1399, 3926]
    assert encoder.decode(tokens) == "… …"
