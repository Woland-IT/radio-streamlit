import pytest
import sys, os
# Ensure repo package directory is importable when running pytest from parent folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import safe_url, get_audio_format


@pytest.mark.parametrize("url,expected", [
    ("https://example.com/stream.mp3", True),
    ("http://example.com/stream.m3u8", True),
    ("ftp://example.com/stream", False),
    ("", False),
    ("http://127.0.0.1/stream", False),
    ("http://localhost/stream", False),
])
def test_safe_url(url, expected):
    res = safe_url(url)
    assert (res is not None) == expected


@pytest.mark.parametrize("url,expected_type", [
    ("https://example.com/stream.m3u8", "application/x-mpegURL"),
    ("https://example.com/stream.mp3", "audio/mpeg"),
    ("https://example.com/stream.aac", "audio/aac"),
    ("https://example.com/stream.unknown", "audio/mpeg"),
])
def test_get_audio_format(url, expected_type):
    assert get_audio_format(url) == expected_type
