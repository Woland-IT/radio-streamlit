import streamlit as st
from pyradios import RadioBrowser
import sqlite3
import random
import urllib.parse
import requests

# Konfiguracja strony
st.set_page_config(page_title="Radio + Gazetki dla Seniorów", layout="wide")

# Baza danych ulubionych
conn = sqlite3.connect('favorites.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS favorites
             (name TEXT PRIMARY KEY, url TEXT, tags TEXT, bitrate INTEGER)''')
conn.commit()

def get_favorites():
    c.execute("SELECT * FROM favorites")
    return c.fetchall()

def add_favorite(station):
    try:
        c.execute("INSERT OR REPLACE INTO favorites VALUES (?, ?, ?, ?)",
                  (station['name'], station['url_resolved'], station.get('tags', 'brak'), station.get('bitrate', 0)))
        conn.commit()
        return True
    except:
        return False

def remove_favorite(name):
    c.execute("DELETE FROM favorites WHERE name=?", (name,))
    conn.commit()

# Bezpieczny URL – filtrujemy niebezpieczne i wymuszamy HTTPS
def safe_url(url):
    if not url or any(x in url.lower() for x in ["localhost", "127.0.0.1", "195.150.20"]):
        return None
    if url.startswith("http://"):
        url = "https://" + url[7:]
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return None
    return url

# Dynamiczne wykrywanie formatu strumienia
def get_stream_format(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.head(url, headers=headers, allow_redirects=True, timeout=8)
        content_type = r.headers.get('Content-Type', '').lower()
        if 'aac' in content_type:
            return "audio/aac"
        elif 'mpeg' in content_type or 'mp3' in content_type:
            return "audio/mpeg"
        elif 'm3u8' in content_type or 'hls' in content_type:
            return "application/x-mpegURL"
    except:
        pass
    # Fallback – jeśli nie udało się wykryć
    if 'rmf' in url.lower():
        return "audio/aac"  # RMF często używa AAC
    return "audio/mpeg"

# Kolory w stylu Metro / Windows 8
metro_colors = [
    "#0072C6", "#D13438", "#00A300", "#F09609", "#A200FF",
    "#E51400", "#339933", "#00ABA9", "#FFC40D", "#1BA1E2"
]

# Fallback – lista popularnych stacji (z aktualnym RMF FM)
fallback_stations = [
    {"name": "Polskie Radio Jedynka", "url_resolved": "https://stream.polskieradio.pl/program1", "tags": "news, talk", "bitrate": 128},
    {"name": "Polskie Radio Dwójka", "url_resolved": "https://stream.polskieradio.pl/program2", "tags": "classical", "bitrate": 128},
    {"name": "Polskie Radio Trójka", "url_resolved": "https://stream.polskieradio.pl/program3", "tags": "music, alternative", "bitrate": 128},
    {"name": "RMF FM", "url_resolved": "https://rmf-ssl.cdn.eurozet.pl/rmffm.mp3", "tags": "pop, hits", "bitrate": 128},
    {"name": "Radio ZET", "url_resolved": "https://n-15-21.dcs.redcdn.pl/sc/o2/Eurozet/live/audio.livx", "tags": "pop", "bitrate": 128},
    {"name": "VOX FM", "url_resolved": "https://ic2.smcdn.pl/3990-1.mp3", "tags": "hits", "bitrate": 128},
    {"name": "Eska Warszawa", "url_resolved": "https://stream.open.fm/1", "tags": "pop, dance", "bitrate": 128},
    {"name": "Antyradio", "url_resolved": "https://n-15-21.dcs.redcdn.pl/sc/o2/Eurozet/live/antyradio.livx", "tags": "rock", "bitrate": 128},
]

# Cache wyszukiwania stacji
@st.cache_data(ttl=3600)
def search_stations(query="", limit=50):
    try:
        rb = RadioBrowser(timeout=10)
        if query:
            return rb.search(name=query, country="Poland", limit=limit, order="clickcount", reverse=True)
        return rb.search(country="Poland", limit=limit, order="clickcount", reverse=True)
    except:
        return []

# Zakładki
tab1, tab2 = st.tabs(["🎵 Radio Online", "🛒 Gazetki Promocyjne"])

# === ZAKŁADKA RADIO ===
with tab1:
    st.header("🇵🇱 Polskie Radio – Duże Kafelki jak w Windows 8")
    st.markdown("Kliknij kafelek → radio gra w panelu po prawej stronie")

    # Styl kafelków
    st.markdown("""
    <style>
        .station-tile {
            background-color: #0072C6;
            border-radius: 12px;
            padding: 25px 15px;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            color: white;
            margin: 12px 0;
            box-shadow: 0 6px 14px rgba(0,0,0,0.25);
            min-height: 150px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .tile-small-text {
            font-size: 16px;
            margin-top: 8px;
            opacity: 0.9;
        }
    </style>
    """, unsafe_allow_html=True)

    # === Ulubione stacje ===
    st.subheader("❤️ Moje Ulubione")
    favorites = get_favorites()
    if favorites:
        cols = st.columns(3)
        for idx, row in enumerate(favorites):
            name = row[0]
            url = safe_url(row[1])
            if not url:
                continue
            tags = row[2] if len(row) > 2 else "brak"
            bitrate = row[3] if len(row) > 3 else 128
            color = random.choice(metro_colors)

            with cols[idx % 3]:
                st.markdown(f"""
                    <div class="station-tile" style="background-color: {color};">
                        {name}
                        <div class="tile-small-text">{tags} | {bitrate} kbps</div>
                    </div>
                """, unsafe_allow_html=True)

                b1, b2 = st.columns(2)
                with b1:
                    if st.button("▶️ Słuchaj", key=f"fav_play_{idx}"):
                        st.session_state.selected_station = {"name": name, "url_resolved": url, "tags": tags, "bitrate": bitrate}
                        st.rerun()
                with b2:
                    if st.button("🗑️ Usuń", key=f"fav_del_{idx}"):
                        remove_favorite(name)
                        st.rerun()
    else:
        st.info("Brak ulubionych stacji. Dodaj z listy poniżej!")

    # === Wyszukiwanie stacji ===
    st.subheader("🔍 Wszystkie polskie stacje")
    query = st.text_input("Wpisz nazwę stacji (np. RMF, ZET, Trójka):", key="search_query")

    stations = search_stations(query, limit=60) if query or not st.session_state.get('stations_loaded') else st.session_state.get('cached_stations', [])
    if not stations:
        stations = fallback_stations

    valid_stations = []
    for station in stations:
        safe = safe_url(station.get('url_resolved', ''))
        if safe:
            station_copy = station.copy()
            station_copy['url_resolved'] = safe
            valid_stations.append(station_copy)

    if valid_stations:
        st.success(f"Znaleziono {len(valid_stations)} działających stacji")
        cols = st.columns(3)
        for idx, station in enumerate(valid_stations):
            color = random.choice(metro_colors)
            with cols[idx % 3]:
                st.markdown(f"""
                    <div class="station-tile" style="background-color: {color};">
                        {station['name']}
                        <div class="tile-small-text">{station.get('tags', 'brak')} | {station.get('bitrate', '?')} kbps</div>
                    </div>
                """, unsafe_allow_html=True)

                b1, b2 = st.columns(2)
                with b1:
                    if st.button("▶️ Słuchaj", key=f"play_{idx}"):
                        st.session_state.selected_station = station
                        st.rerun()
                with b2:
                    if st.button("❤️ Dodaj", key=f"add_{idx}"):
                        if add_favorite(station):
                            st.success(f"Dodano {station['name']}!")
                            st.rerun()
    else:
        st.warning("Brak działających stacji. Spróbuj innego wyszukiwania.")

# === ZAKŁADKA GAZETKI ===
with tab2:
    st.header("🛒 Gazetki Promocyjne – Duże Kafelki")
    st.markdown("Kliknij logo sklepu → otwiera się oficjalna gazetka")

    st.markdown("""
    <style>
        .shop-tile {
            background-color: #0072C6;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            color: white;
            margin: 20px 0;
            box-shadow: 0 8px 18px rgba(0,0,0,0.2);
            min-height: 220px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            cursor: pointer;
        }
        .shop-tile:hover { opacity: 0.9; }
    </style>
    """, unsafe_allow_html=True)

    promotions = [
        {"name": "Biedronka", "image": "https://www.biedronka.pl/sites/default/files/styles/logo/public/logo-biedronka.png", "url": "https://www.biedronka.pl/gazetki", "color": "#D13438"},
        {"name": "Lidl", "image": "https://www.lidl.pl/assets/pl/logo.svg", "url": "https://www.lidl.pl/c/nasze-gazetki/s10008614", "color": "#0072C6"},
        {"name": "Kaufland", "image": "https://sklep.kaufland.pl/assets/img/kaufland-logo.svg", "url": "https://sklep.kaufland.pl/gazeta-reklamowa.html", "color": "#E51400"},
        {"name": "Dino", "image": "https://marketdino.pl/themes/dino/assets/img/logo.svg", "url": "https://marketdino.pl/gazetki-promocyjne", "color": "#F09609"},
        {"name": "Carrefour", "image": "https://www.carrefour.pl/themes/custom/carrefour/logo.svg", "url": "https://www.carrefour.pl/gazetka-handlowa", "color": "#00A300"},
        {"name": "Leroy Merlin", "image": "https://www.leroymerlin.pl/img/logo-lm.svg", "url": "https://www.leroymerlin.pl/gazetka/", "color": "#FFC40D"},
        {"name": "Bricomarché", "image": "https://www.bricomarche.pl/themes/custom/bricomarche/logo.png", "url": "https://www.bricomarche.pl/gazetka", "color": "#A200FF"},
        {"name": "Empik", "image": "https://www.empik.com/static/img/empik-logo.svg", "url": "https://www.empik.com/promocje", "color": "#00ABA9"},
    ]

    cols = st.columns(3)
    for idx, promo in enumerate(promotions):
        color = promo.get("color", random.choice(metro_colors))
        with cols[idx % 3]:
            st.markdown(
                f'<a href="{promo["url"]}" target="_blank" style="text-decoration:none;">'
                f'<div class="shop-tile" style="background-color:{color};">'
                f'<img src="{promo["image"]}" width="120" style="margin-bottom:12px;">'
                f'<div>{promo["name"]}</div>'
                f'</div></a>',
                unsafe_allow_html=True
            )

# === SIDEBAR – ODTWARZACZ RADIA ===
with st.sidebar:
    st.header("🎵 Odtwarzacz Radia")
    if 'selected_station' in st.session_state:
        selected = st.session_state.selected_station
        url = safe_url(selected.get('url_resolved'))
        if url:
            st.markdown(f"### Słuchasz: **{selected['name']}**")
            st.markdown(f"**Tagi:** {selected.get('tags', 'brak')} • **Bitrate:** {selected.get('bitrate', '?')} kbps")

            # HTML audio – obsługuje MP3 i AAC jednocześnie
            st.components.v1.html(f"""
                <audio controls autoplay style="width:100%; margin-top:10px;">
                    <source src="{url}" type="{get_stream_format(url)}">
                    <source src="{url}" type="audio/aac">
                    <source src="{url}" type="audio/mpeg">
                    Twoja przeglądarka nie obsługuje odtwarzania.
                </audio>
            """, height=120)

            st.markdown("""
            <div style="background:#e6f7ff; padding:15px; border-radius:10px; text-align:center; margin-top:15px;">
                🔊 <strong>Nie słychać?</strong><br>
                Naciśnij PLAY 🔘 lub odśwież stronę.<br>
                Sprawdź głośność w telefonie/komputerze.
            </div>
            """, unsafe_allow_html=True)

            fav_names = [f[0] for f in get_favorites()]
            if selected['name'] not in fav_names:
                if st.button("❤️ Dodaj do ulubionych", key="sidebar_add"):
                    if add_favorite(selected):
                        st.success("Dodano do ulubionych!")
                        st.rerun()
            else:
                st.success("✅ Już w ulubionych!")

            if st.button("🛑 Zatrzymaj radio"):
                del st.session_state.selected_station
                st.rerun()
        else:
            st.error("Błędny link stacji – wybierz inną.")
    else:
        st.info("Wybierz stację z kafelków po lewej stronie.")

st.sidebar.success("Prosta aplikacja dla seniorów – duże kafelki wszędzie! 🎉")
