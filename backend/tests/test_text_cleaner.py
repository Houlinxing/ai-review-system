# backend/tests/test_text_cleaner.py
from app.utils.text_cleaner import clean_text

def test_remove_html_tags():
    assert clean_text("<b>hello</b>") == "hello"

def test_remove_urls():
    assert "http" not in clean_text("visit http://example.com today")

def test_empty_string():
    assert clean_text("") == ""

def test_normal_text_unchanged():
    text = "This is a great place!"
    assert clean_text(text) == text