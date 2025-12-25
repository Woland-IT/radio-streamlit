import requests
import base64
import urllib.parse
import streamlit as st
from pyradios import RadioBrowser

def probe_url(url: str, timeout: int = 5):
    """
    Zwraca szczegóły dostępności URL: status, final_url, content-type, range, błędy.
    Nie rzuca wyjątków – zwraca słownik z polami.
    """
    if not url:
        return {"ok": False, "error": "Brak URL"}
    result = {"url": url}
    try:
        r = requests.head(url, timeout=timeout, allow_redirects=True)
        result.update({
            "head_status": r.status_code,
            "final_url": str(r.url),
            "content_type": r.headers.get('content-type'),
            "accept_ranges": r.headers.get('accept-ranges'),
            "access_control": r.headers.get('access-control-allow-origin'),
        })
    except Exception as e:
        result["head_error"] = str(e)
    try:
        r2 = requests.get(url, timeout=timeout, stream=True, headers={'Range': 'bytes=0-1023'})
        result.update({
            "get_status": r2.status_code,
            "get_ct": r2.headers.get('content-type'),
            "get_ac": r2.headers.get('access-control-allow-origin'),
        })
        result["ok"] = r2.status_code in (200,206)
    except Exception as e2:
        result["get_error"] = str(e2)
        result["ok"] = False
    return result


def get_real_stream_url(station_name: str, original_url: str = None) -> list:
    """
    Próbuje pobrać rzeczywiste URL-y streamów dla problematycznych stacji
    przez parsowanie ich metadata lub szukanie w API.
    """
    station_name_lower = station_name.lower()
    
    # Dla znanych stacji – zwróć zmapowane URL-y
    if "eska warszawa" in station_name_lower:
        return [
            "https://ic2.smcdn.pl/3996-1.mp3",
            "https://ic7.smcdn.pl/3996-1.mp3",
            "https://stream.smcdn.pl/eska-warszawa",
        ]
    elif "antyradio" in station_name_lower or "anty radio" in station_name_lower:
        return [
            "https://n-15-21.dcs.redcdn.pl/sc/o2/Eurozet/live/antyradio.mp3",
            "https://n-15-21.dcs.redcdn.pl/sc/o2/Eurozet/live/antyradio.livx",
            # Alternatywne adresy z różnych serwerów
            "https://n10-12.dcs.redcdn.pl/sc/o2/Eurozet/live/antyradio.mp3",
            "https://n-11-21.dcs.redcdn.pl/sc/o2/Eurozet/live/antyradio.mp3",
        ]
    elif "rmf fm" in station_name_lower:
        return [
            "https://rs101-krk.rmfstream.pl/rmf_fm",
            "https://rs101.rmfstream.pl/rmf_fm",
        ]
    elif "polskie radio jedynka" in station_name_lower or "pr1" in station_name_lower:
        # Polskie Radio ma wersje zarówno HLS jak i MP3
        return [
            "https://stream11.polskieradio.pl/pr1/pr1.sdp/playlist.m3u8",  # HLS
            "https://stream11.polskieradio.pl/pr1/pr1.mp3",  # MP3 fallback
            "https://stream11.polskieradio.pl/pr1",  # Alternatywa
        ]
    
    return [original_url] if original_url else []


def check_url_accessible(url: str, timeout: int = 5) -> bool:
    print(f"CHECK: Sprawdzam dostępność URL: {url}")
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        if response.status_code == 200:
            print(f"CHECK: URL dostępny (HEAD): {url}")
            return True
        else:
            print(f"CHECK: URL niedostępny (HEAD status {response.status_code}): {url}")
            return False
    except requests.RequestException as e:
        print(f"CHECK: HEAD nie działa dla {url}, błąd: {e}, próbuję GET...")
        try:
            response = requests.get(url, timeout=timeout, stream=True, headers={'Range': 'bytes=0-1023'})
            if response.status_code in (200, 206):
                print(f"CHECK: URL dostępny (GET): {url}")
                return True
            else:
                print(f"CHECK: URL niedostępny (GET status {response.status_code}): {url}")
                return False
        except requests.RequestException as e2:
            print(f"CHECK: GET też nie działa dla {url}, błąd: {e2}")
            return False


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
    url_lower = url.lower()
    if any(ext in url_lower for ext in ['.m3u8', '.m3u']):
        return "application/x-mpegURL"
    elif any(ext in url_lower for ext in ['.mp3', '.mpga']):
        return "audio/mpeg"
    elif any(ext in url_lower for ext in ['.aac', '.aacp', '.adts']):
        return "audio/aac"
    elif any(ext in url_lower for ext in ['.livx']):
        # .livx to zazwyczaj AAC, ale spróbuj najpierw jako MP3 (bardziej kompatybilne)
        return "audio/aac"
    elif any(ext in url_lower for ext in ['.ogg', '.oga']):
        return "audio/ogg"
    elif any(ext in url_lower for ext in ['.wav']):
        return "audio/wav"
    elif any(ext in url_lower for ext in ['.pls']):
        return "audio/x-scpls"
    else:
        return "audio/mpeg"  # domyślnie MP3


def image_to_data_uri(url: str, timeout: int = 5):
    try:
        resp = requests.get(url, timeout=timeout, stream=True)
        content_type = resp.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            print(f"LOGO: Odrzucono {url} – content-type {content_type}")
            return None
        data = resp.content
        b64 = base64.b64encode(data).decode('ascii')
        data_uri = f"data:{content_type};base64,{b64}"
        print(f"LOGO: Załadowano jako data URI: {url}")
        return data_uri
    except requests.RequestException as e:
        print(f"LOGO: Błąd pobierania {url}: {e}")
        return None


metro_colors = [
    "#D13438", "#0072C6", "#00A300", "#F09609", "#A200FF",
    "#E51400", "#339933", "#00ABA9", "#FFC40D", "#1BA1E2",
    "#8E44AD", "#16A085", "#E67E22", "#C0392B", "#27AE60"
]


fallback_stations = [
    {"name": "RMF FM", "url_resolved": "https://rs101-krk.rmfstream.pl/rmf_fm", "tags": "pop, hity", "bitrate": 128},
    {"name": "VOX FM", "url_resolved": "https://ic2.smcdn.pl/3990-1.mp3", "tags": "hity, dance", "bitrate": 128},
    {"name": "Eska Warszawa", "url_resolved": "https://ic2.smcdn.pl/3996-1.mp3", "tags": "pop, dance", "bitrate": 128},
    {"name": "Antyradio", "url_resolved": "https://n-15-21.dcs.redcdn.pl/sc/o2/Eurozet/live/antyradio.mp3", "tags": "rock", "bitrate": 128},
    {"name": "Polskie Radio Jedynka", "url_resolved": "https://stream11.polskieradio.pl/pr1/pr1.sdp/playlist.m3u8", "tags": "wiadomości, talk", "bitrate": 128},
]

# Ręczne nadpisania URL dla problematycznych stacji (priorytetowo używane)
station_overrides = {
    # Eska Warszawa – stabilny MP3 + alternatywy
    "eska warszawa": [
        "https://ic2.smcdn.pl/3996-1.mp3",
        "https://stream.smcdn.pl/eska-warszawa",
        "https://ic7.smcdn.pl/3996-1.mp3",
    ],
    # Polskie Radio Jedynka – HLS
    "polskie radio jedynka": [
        "https://stream11.polskieradio.pl/pr1/pr1.sdp/playlist.m3u8",
        "https://stream11.polskieradio.pl/pr1",
    ],
    # Antyradio – MP3 zamiast LIVX (lepiej obsługiwane)
    "antyradio": [
        "https://n-15-21.dcs.redcdn.pl/sc/o2/Eurozet/live/antyradio.mp3",
        "https://n-15-21.dcs.redcdn.pl/sc/o2/Eurozet/live/antyradio.livx",
    ],
}


@st.cache_data(ttl=300)
def search_stations(query: str = "", country: str = "Poland", limit: int = 100):
    rb = RadioBrowser()
    return rb.search(name=query if query else "", country=country, limit=limit, order="clickcount", reverse=True)
