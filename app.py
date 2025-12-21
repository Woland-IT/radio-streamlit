import streamlit as st
from pyradios import RadioBrowser
import sqlite3
import random
import urllib.parse

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

# Bezpieczny URL
def safe_url(url):
    if not url or any(x in url.lower() for x in ["localhost", "127.0.0.1", "195.150.20"]):
        return None
    if url.startswith("http://"):
        url = "https://" + url[7:]
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return None
    return url

# Format audio
def get_audio_format(url):
    url = url.lower()
    if '.mp3' in url:
        return "audio/mpeg"
    elif any(x in url for x in ['.aac', '.aacp']):
        return "audio/aac"
    elif '.m3u8' in url:
        return "application/x-mpegURL"
    return "audio/mpeg"

# Cache dla zapytań do RadioBrowser
@st.cache_data(ttl=3600)
def search_stations(query, limit=50):
    rb = RadioBrowser(timeout=10)
    if query:
        return rb.search(name=query, country="Poland", limit=limit, order="clickcount", reverse=True)
    return rb.search(country="Poland", limit=limit, order="clickcount", reverse=True)

# Kolory Metro
metro_colors = [
    "#0072C6", "#D13438", "#00A300", "#F09609", "#A200FF",
    "#E51400", "#339933", "#00ABA9", "#FFC40D", "#1BA1E2"
]

# Fallback – statyczna lista
fallback_stations = [
    {"name": "Polskie Radio Jedynka", "url_resolved": "http://mp3.polskieradio.pl:8900/;stream.mp3", "tags": "news, talk", "bitrate": 128},
    {"name": "Polskie Radio Dwójka", "url_resolved": "http://mp3.polskieradio.pl:8902/;stream.mp3", "tags": "classical", "bitrate": 128},
    {"name": "Polskie Radio Trójka", "url_resolved": "http://mp3.polskieradio.pl:8904/;stream.mp3", "tags": "music, alternative", "bitrate": 128},
    {"name": "RMF FM", "url_resolved": "https://rs101-krk.rmfstream.pl/rmf_fm", "tags": "pop, hits", "bitrate": 128},
    {"name": "Radio ZET", "url_resolved": "https://n-15-21.dcs.redcdn.pl/sc/o2/Eurozet/live/audio.livx", "tags": "pop", "bitrate": 128},
]

# Zakładki
tab1, tab2 = st.tabs(["🎵 Radio Online", "🛒 Gazetki Promocyjne"])

# === ZAKŁADKA RADIO ===
with tab1:
    st.header("🇵🇱 Polskie Radio – Kafelki Windows 8")
    st.markdown("Kliknij kafelek, by słuchać w panelu po prawej")

    # Styl kafelków
    st.markdown("""
    <style>
        .station-tile {
            background-color: #0072C6;
            border-radius: 12px;
            padding: 20px 10px;
            text-align: center;
            font-size: 22px;
            font-weight: bold;
            color: white;
            margin: 10px 0;
            box-shadow: 0 6px 12px rgba(0,0,0,0.2);
            min-height: 140px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .tile-small-text {
            font-size: 14px;
            margin-top: 6px;
            opacity: 0.9;
        }
        .station-tile:hover {
            opacity: 0.9;
        }
    </style>
    """, unsafe_allow_html=True)

    # === Ulubione ===
    st.subheader("❤️ Moje Ulubione")
    favorites = get_favorites()
    if favorites:
        cols = st.columns(3)
        for idx, row in enumerate(favorites):
            name, url, tags, bitrate = row
            url = safe_url(url)
            if not url:
                continue
            tags = tags or "brak"
            bitrate = bitrate or 128
            color = random.choice(metro_colors)

            with cols[idx % 3]:
                st.markdown(f"""
                    <div class="station-tile" style="background-color: {color};">
                        {name}
                        <div class="tile-small-text">{tags} | {bitrate} kbps</div>
                    </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("▶️ Słuchaj", key=f"fav_play_{idx}_{name}"):
                        st.session_state.selected_station = {
                            "name": name, "url_resolved": url, "tags": tags, "bitrate": bitrate
                        }
                with col2:
                    if st.button("🗑️ Usuń", key=f"fav_del_{idx}_{name}"):
                        remove_favorite(name)
                        st.success(f"Usunięto {name}!")
                        st.rerun()
    else:
        st.info("Brak ulubionych. Dodaj stacje z listy poniżej!")

    # === Wyszukiwanie ===
    st.subheader("🔍 Znajdź stację")
    query = st.text_input("Wpisz nazwę (np. RMF, ZET):", key="search")

    stations = []
    try:
        stations = search_stations(query, limit=50)
    except Exception as e:
        st.warning(f"Problem z API radia: {e}. Używam listy zapasowej.")
        stations = fallback_stations if not query else [
            s for s in fallback_stations if query.lower() in s['name'].lower()
        ]

    valid_stations = []
    for station in stations:
        url = safe_url(station.get('url_resolved'))
        if url:
            station['url_resolved'] = url
            valid_stations.append(station)

    if valid_stations:
        st.success(f"Znaleziono {len(valid_stations)} stacji")
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

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("▶️ Słuchaj", key=f"play_{idx}_{station['name']}"):
                        st.session_state.selected_station = station
                with col2:
                    if st.button("❤️ Dodaj", key=f"add_{idx}_{station['name']}"):
                        if add_favorite(station):
                            st.success(f"Dodano {station['name']}!")
                            st.rerun()
                        else:
                            st.warning("Już w ulubionych lub błąd.")
    else:
        st.warning("Nie znaleziono stacji. Spróbuj innej nazwy.")

# === ZAKŁADKA GAZETKI ===
with tab2:
    st.header("🛒 Gazetki Promocyjne")
    st.markdown("Kliknij kafelek, by zobaczyć promocje")

    st.markdown("""
    <style>
        .shop-tile {
            background-color: #0072C6;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            color: white;
            margin: 10px 0;
            box-shadow: 0 6px 12px rgba(0,0,0,0.2);
            min-height: 180px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .shop-tile:hover {
            opacity: 0.9;
        }
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
                f'<img src="{promo["image"]}" width="100" style="margin-bottom:8px;">'
                f'<div>{promo["name"]}</div>'
                f'</div></a>',
                unsafe_allow_html=True
            )

# === SIDEBAR – ODTWARZACZ ===
with st.sidebar:
    st.header("🎵 Odtwarzacz Radia")
    if 'selected_station' in st.session_state:
        selected = st.session_state.selected_station
        url = safe_url(selected.get('url_resolved'))
        if url:
            st.markdown(f"### Słuchasz: **{selected['name']}**")
            st.markdown(f"**Tagi:** {selected.get('tags', 'brak')} • **Bitrate:** {selected.get('bitrate', '?')} kbps")
            try:
                st.audio(url, format=get_audio_format(url))
            except Exception as e:
                st.error(f"Nie można odtworzyć: {e}")

            st.markdown("""
            <div style="background:#e6f7ff; padding:15px; border-radius:10px; text-align:center;">
                🔊 Nie słychać? Naciśnij <strong>PLAY</strong> 🔘<br>
                Sprawdź głośność w telefonie/komputerze.
            </div>
            """, unsafe_allow_html=True)

            fav_names = [f[0] for f in get_favorites()]
            if selected['name'] not in fav_names:
                if st.button("❤️ Dodaj do ulubionych", key="add_sidebar"):
                    if add_favorite(selected):
                        st.success("Dodano!")
                        st.rerun()
            else:
                st.success("✅ Już w ulubionych!")

            if st.button("🛑 Zatrzymaj radio"):
                del st.session_state.selected_station
                st.rerun()
        else:
            st.error("Nieprawidłowy link stacji – wybierz inną.")
    else:
        st.info("Wybierz stację z kafelków po lewej.")

st.sidebar.success("Prosta aplikacja dla seniorów – duże kafelki! 🎉")
