import urllib.parse
import streamlit as st
from pyradios import RadioBrowser


def safe_url(url: str):
    if not url:
        return None
    if any(x in url for x in ["localhost", "127.0.0.1"]):
        return None
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return None
    if not parsed.netloc:
        return None
    return url


def get_audio_format(url: str):
    if '.m3u8' in url:
        return "application/x-mpegURL"
    elif '.mp3' in url:
        return "audio/mpeg"
    elif any(ext in url for ext in ['.aac', '.aacp', '.livx']):
        return "audio/aac"
    else:
        return "audio/mpeg"


metro_colors = [
    "#D13438", "#0072C6", "#00A300", "#F09609", "#A200FF",
    "#E51400", "#339933", "#00ABA9", "#FFC40D", "#1BA1E2",
    "#8E44AD", "#16A085", "#E67E22", "#C0392B", "#27AE60"
]


fallback_stations = [
    {"name": "RMF FM", "url_resolved": "https://rs101-krk.rmfstream.pl/rmf_fm", "tags": "pop, hity", "bitrate": 128},
    {"name": "VOX FM", "url_resolved": "https://ic2.smcdn.pl/3990-1.mp3", "tags": "hity, dance", "bitrate": 128},
    {"name": "Eska Warszawa", "url_resolved": "https://stream.open.fm/1", "tags": "pop, dance", "bitrate": 128},
    {"name": "Antyradio", "url_resolved": "https://n-15-21.dcs.redcdn.pl/sc/o2/Eurozet/live/antyradio.livx", "tags": "rock", "bitrate": 128},
    {"name": "Polskie Radio Jedynka", "url_resolved": "https://stream11.polskieradio.pl/pr1/pr1.sdp/playlist.m3u8", "tags": "wiadomości, talk", "bitrate": 128},
]


@st.cache_data(ttl=300)
def search_stations(query: str = "", country: str = "Poland", limit: int = 100):
    rb = RadioBrowser()
    return rb.search(name=query if query else "", country=country, limit=limit, order="clickcount", reverse=True)
