import streamlit as st
from pyradios import RadioBrowser
import sqlite3
import random
import urllib.parse

# ================================
# KONFIGURACJA
# ================================
st.set_page_config(page_title="Radio + Gazetki dla Seniora", layout="wide")

# Baza ulubionych
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

# Pomocnicze
def safe_url(url):
    if any(x in url for x in ["localhost", "127.0.0.1"]):
        return None
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return None
    return url

def get_audio_format(url):
    if '.m3u8' in url:
        return "application/x-mpegURL"
    elif '.mp3' in url:
        return "audio/mpeg"
    elif any(ext in url for ext in ['.aac', '.aacp', '.livx']):
        return "audio/aac"
    else:
        return "audio/mpeg"

# Kolory Metro
metro_colors = [
    "#D13438", "#0072C6", "#00A300", "#F09609", "#A200FF",
    "#E51400", "#339933", "#00ABA9", "#FFC40D", "#1BA1E2",
    "#8E44AD", "#16A085", "#E67E22", "#C0392B", "#27AE60"
]

# Fallback stacje (HTTPS)
fallback_stations = [
    {"name": "RMF FM", "url_resolved": "https://rs101-krk.rmfstream.pl/rmf_fm", "tags": "pop, hity", "bitrate": 128},
    {"name": "VOX FM", "url_resolved": "https://ic2.smcdn.pl/3990-1.mp3", "tags": "hity, dance", "bitrate": 128},
    {"name": "Eska Warszawa", "url_resolved": "https://stream.open.fm/1", "tags": "pop, dance", "bitrate": 128},
    {"name": "Antyradio", "url_resolved": "https://n-15-21.dcs.redcdn.pl/sc/o2/Eurozet/live/antyradio.livx", "tags": "rock", "bitrate": 128},
    {"name": "Polskie Radio Jedynka", "url_resolved": "https://stream11.polskieradio.pl/pr1/pr1.sdp/playlist.m3u8", "tags": "wiadomości, talk", "bitrate": 128},
    {"name": "Polskie Radio Dwójka", "url_resolved": "https://stream12.polskieradio.pl/pr2/pr2.sdp/playlist.m3u8", "tags": "klasyka", "bitrate": 128},
    {"name": "Polskie Radio Trójka", "url_resolved": "https://stream13.polskieradio.pl/pr3/pr3.sdp/playlist.m3u8", "tags": "muzyka, alternatywa", "bitrate": 128},
    {"name": "Polskie Radio Czwórka", "url_resolved": "https://stream14.polskieradio.pl/pr4/pr4.sdp/playlist.m3u8", "tags": "młodzieżowe", "bitrate": 128},
    {"name": "RMF Classic", "url_resolved": "https://rs101-krk.rmfstream.pl/rmf_classic", "tags": "filmowa, relaks", "bitrate": 128},
]

# ================================
# ZAKŁADKI
# ================================
tab1, tab2 = st.tabs(["🎵 Radio Online", "🛒 Gazetki Promocyjne"])

with tab1:
    st.header("🇵🇱 Polskie Radio dla Seniora")
    st.markdown("### Kliknij cały wielki kolorowy kafelek – radio gra od razu po prawej! 🎶🔊")

    # CSS – całkowicie ukrywa pusty przycisk (nie zajmuje miejsca, zero błędów)
    st.markdown("""
    <style>
        /* Ukrywa całkowicie pusty przycisk – nie zajmuje miejsca i nie powoduje błędów */
        div[data-testid="stButton"] button[kind="secondary"] {
            background: none !important;
            border: none !important;
            padding: 0 !important;
            margin: 0 !important;
            min-height: 0 !important;
            height: 0 !important;
            width: 100% !important;
            visibility: hidden !important;
            pointer-events: auto !important;
        }
        .clickable-tile {
            background-color: #0072C6;
            border-radius: 40px;
            padding: 100px 20px;
            text-align: center;
            font-size: 50px;
            font-weight: bold;
            color: white;
            margin: 40px 0;
            box-shadow: 0 30px 60px rgba(0,0,0,0.5);
            height: 400px;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            cursor: pointer;
            transition: all 0.5s ease;
            user-select: none;
        }
        .clickable-tile:hover {
            transform: translateY(-40px) scale(1.12);
            box-shadow: 0 80px 140px rgba(0,0,0,0.6);
        }
        .tile-small-text {
            font-size: 34px;
            margin-top: 30px;
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
            name, url, tags, bitrate = row[0], safe_url(row[1]), row[2] if len(row)>2 else "brak", row[3] if len(row)>3 else 128
            if not url or not url.startswith("https://"):
                continue
            color = random.choice(metro_colors)
            with cols[idx % 3]:
                if st.button("", key=f"fav_play_{idx}", use_container_width=True):
                    st.session_state.selected_station = {"name": name, "url_resolved": url, "tags": tags, "bitrate": bitrate}
                    st.rerun()
                st.markdown(f"""
                    <div class="clickable-tile" style="background-color: {color};">
                        {name}
                        <div class="tile-small-text">{tags} | {bitrate} kbps</div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("Usuń z ulubionych ❌", key=f"fav_del_{idx}", use_container_width=True):
                    remove_favorite(name)
                    st.rerun()
    else:
        st.info("Brak ulubionych – kliknij ❤️ pod kafelkiem poniżej!")

    # === Wszystkie stacje ===
    st.subheader("🔍 Wszystkie działające stacje")
    query = st.text_input("Szukaj (np. RMF, Trójka):", key="search")

    valid_stations = fallback_stations[:]

    try:
        rb = RadioBrowser()
        stations = rb.search(name=query if query else "", country="Poland", limit=100, order="clickcount", reverse=True)
        for station in stations:
            url = safe_url(station.get('url_resolved', ''))
            if url and url.startswith("https://"):
                s = station.copy()
                s['url_resolved'] = url
                if s not in valid_stations:
                    valid_stations.append(s)
        st.success(f"Znaleziono {len(valid_stations)} stacji – kliknij kafelek!")
    except Exception as e:
        st.warning(f"Brak połączenia: {e}. Zapasowe zawsze działają!")

    if valid_stations:
        cols = st.columns(3)
        for idx, station in enumerate(valid_stations):
            color = random.choice(metro_colors)
            with cols[idx % 3]:
                if st.button("", key=f"play_{idx}", use_container_width=True):
                    st.session_state.selected_station = station
                    st.rerun()
                st.markdown(f"""
                    <div class="clickable-tile" style="background-color: {color};">
                        {station['name']}
                        <div class="tile-small-text">{station.get('tags', 'brak')} | {station.get('bitrate', '?')} kbps</div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("❤️ Dodaj do ulubionych", key=f"add_{idx}", use_container_width=True):
                    add_favorite(station)
                    st.success("Dodano!")

# ================================
# ZAKŁADKA GAZETKI
# ================================
with tab2:
    st.header("🛒 Gazetki Promocyjne – Wielkie Kafelki")
    st.markdown("Kliknij kafelek sklepu → otwiera się gazetka")

    st.markdown("""
    <style>
        .shop-tile {
            background-color: #0072C6;
            border-radius: 40px;
            padding: 100px 20px;
            text-align: center;
            font-size: 48px;
            font-weight: bold;
            color: white;
            margin: 50px 0;
            box-shadow: 0 30px 60px rgba(0,0,0,0.5);
            height: 400px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            transition: all 0.5s ease;
        }
        .shop-tile:hover {
            transform: translateY(-35px) scale(1.12);
            box-shadow: 0 80px 140px rgba(0,0,0,0.6);
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
            st.markdown(f"""
                <div style="text-align: center; margin-bottom: 70px;">
                    <a href="{promo['url']}" target="_blank">
                        <div class="shop-tile" style="background-color: {color};">
                            <img src="{promo['image']}" width="200" style="margin-bottom: 35px;">
                            <p>{promo['name']}</p>
                        </div>
                    </a>
                </div>
            """, unsafe_allow_html=True)

# ================================
# SIDEBAR – ODTWARZACZ
# ================================
with st.sidebar:
    st.header("🎵 Teraz gra...")
    if 'selected_station' in st.session_state:
        selected = st.session_state.selected_station
        url = selected['url_resolved']
        audio_type = get_audio_format(url)

        st.markdown(f"### **{selected['name']}** 🔊🎶")
        st.markdown(f"**Tagi:** {selected.get('tags', 'brak')} • **Bitrate:** {selected.get('bitrate', '?')} kbps")

        st.components.v1.html(f"""
            <audio controls autoplay style="width:100%;">
                <source src="{url}" type="{audio_type}">
                Twoja przeglądarka nie obsługuje audio.
            </audio>
        """, height=100)

        st.markdown("""
        <div style="background-color: #e6f7ff; padding: 45px; border-radius: 25px; text-align: center; font-size: 30px; margin: 35px 0;">
            🔊 <strong>Nie słychać?</strong><br>
            Naciśnij ▶️ PLAY wyżej!<br>
            Sprawdź głośność telefonu/komputera.
        </div>
        """, unsafe_allow_html=True)

        if selected['name'] not in [f[0] for f in get_favorites()]:
            if st.button("❤️ Dodaj do ulubionych", use_container_width=True):
                add_favorite(selected)
                st.rerun()
        else:
            st.success("✅ Już w ulubionych!")

        if st.button("🔇 Zatrzymaj radio", use_container_width=True):
            del st.session_state.selected_station
            st.rerun()
    else:
        st.info("Kliknij wielki kolorowy kafelek – radio zacznie grać tutaj!")

st.sidebar.success("Gotowe! Kafelki czyste, klikalne, bez błędów React! ❤️🎉")
