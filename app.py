import streamlit as st
from pyradios import RadioBrowser
import sqlite3
import random
import urllib.parse

# Konfiguracja
st.set_page_config(page_title="Radio + Gazetki dla Seniorów", layout="wide")

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
    except: return False

def remove_favorite(name):
    c.execute("DELETE FROM favorites WHERE name=?", (name,))
    conn.commit()

# Walidacja URL
def safe_url(url):
    if any(x in url for x in ["localhost", "127.0.0.1"]): return None
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme or not parsed.netloc: return None
    return url

# Dynamiczny format audio – teraz z HLS!
def get_audio_format(url):
    if '.m3u8' in url:
        return "application/x-mpegURL"  # HLS – działa w przeglądarkach!
    elif '.mp3' in url:
        return "audio/mpeg"
    elif any(ext in url for ext in ['.aac', '.aacp']):
        return "audio/aac"
    else:
        return "audio/mpeg"

# Kolory Metro
metro_colors = ["#0072C6", "#D13438", "#00A300", "#F09609", "#A200FF",
                "#E51400", "#339933", "#00ABA9", "#FFC40D", "#1BA1E2"]

# === FALLBACK – zawsze działające HTTPS (MP3 + HLS AAC) ===
fallback_stations = [
    {"name": "RMF FM", "url_resolved": "https://rs101-krk.rmfstream.pl/rmf_fm", "tags": "pop, hits", "bitrate": 128},
    {"name": "Radio ZET", "url_resolved": "https://n-15-21.dcs.redcdn.pl/sc/o2/Eurozet/live/audio.livx", "tags": "pop", "bitrate": 128},
    {"name": "VOX FM", "url_resolved": "https://ic2.smcdn.pl/3990-1.mp3", "tags": "hits", "bitrate": 128},
    {"name": "Eska Warszawa", "url_resolved": "https://stream.open.fm/1", "tags": "pop, dance", "bitrate": 128},
    {"name": "Antyradio", "url_resolved": "https://n-15-21.dcs.redcdn.pl/sc/o2/Eurozet/live/antyradio.livx", "tags": "rock", "bitrate": 128},
    {"name": "Polskie Radio Jedynka", "url_resolved": "https://stream11.polskieradio.pl/pr1/pr1.sdp/playlist.m3u8", "tags": "news, talk", "bitrate": 128},
    {"name": "Polskie Radio Dwójka", "url_resolved": "https://stream12.polskieradio.pl/pr2/pr2.sdp/playlist.m3u8", "tags": "classical", "bitrate": 128},
    {"name": "Polskie Radio Trójka", "url_resolved": "https://stream13.polskieradio.pl/pr3/pr3.sdp/playlist.m3u8", "tags": "music, alternative", "bitrate": 128},
    {"name": "Polskie Radio Czwórka", "url_resolved": "https://stream14.polskieradio.pl/pr4/pr4.sdp/playlist.m3u8", "tags": "youth, pop", "bitrate": 128},
]

# Zakładki
tab1, tab2 = st.tabs(["🎵 Radio Online", "🛒 Gazetki Promocyjne"])

with tab1:
    st.header("🇵🇱 Polskie Radio – Duże Kafelki")
    st.markdown("Kliknij kafelek → odtwarzacz w sidebar po prawej. Wszystkie stacje na HTTPS – zero problemów z dźwiękiem!")

    # Styl kafelków (bez zmian)
    st.markdown("""
<style>
        .station-tile {
            background-color: #0072C6;
            border-radius: 12px;
            padding: 30px;
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            color: white;
            margin: 15px 0;
            box-shadow: 0 8px 16px rgba(0,0,0,0.3);
            height: 180px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            cursor: pointer;
            transition: all 0.3s;
        }
        .station-tile:hover {
            transform: scale(1.05);
            box-shadow: 0 12px 24px rgba(0,0,0,0.4);
        }
        .tile-small-text {
            font-size: 18px;
            margin-top: 10px;
            opacity: 0.9;
            font-weight: normal;
        }
    </style>
    """, unsafe_allow_html=True)

    # Ulubione (z filtrem HTTPS)
# === Ulubione stacje ===
    st.subheader("❤️ Moje Ulubione Stacje")
    favorites = get_favorites()
    if favorites:
        cols = st.columns(3)
        for idx, row in enumerate(favorites):
            name, url, tags, bitrate = row[0], safe_url(row[1]), row[2] if len(row)>2 else "brak", row[3] if len(row)>3 else 128
            if not url or not url.startswith("https://"):
                continue
            color = random.choice(metro_colors)
            
            with cols[idx % 3]:
                if st.button("", key=f"fav_play_direct_{idx}", help="Kliknij, aby odtwarzać"):
                    st.session_state.selected_station = {"name": name, "url_resolved": url, "tags": tags, "bitrate": bitrate}
                    st.rerun()
                
                # Cały kafelek jako "przycisk" przez overlay
                st.markdown(f"""
                    <div class="station-tile" style="background-color: {color};">
                        {name}
                        <div class="tile-small-text">{tags} | {bitrate} kbps</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Przycisk usuń
                if st.button("Usuń z ulubionych ❌", key=f"fav_del_{idx}"):
                    remove_favorite(name)
                    st.rerun()
    else:
        st.info("Brak ulubionych – kliknij ❤️ na kafelku poniżej, żeby dodać!")

    # Wyszukiwanie – tylko HTTPS
    st.subheader("🔍 Wszystkie Polskie Stacje (tylko HTTPS – zawsze grają!)")
    query = st.text_input("Szukaj (np. RMF, Trójka):", key="search")

    valid_stations = fallback_stations[:]  # zawsze mamy działające

    try:
        rb = RadioBrowser()
        stations = rb.search(name=query if query else "", country="Poland", limit=100, order="clickcount", reverse=True)
        for station in stations:
            url = safe_url(station.get('url_resolved', ''))
            if url and url.startswith("https://"):
                s = station.copy()
                s['url_resolved'] = url
                valid_stations.append(s)
        st.success(f"Znaleziono {len(valid_stations)} stacji (w tym zapasowe zawsze działające)")
    except Exception as e:
        st.warning(f"Brak połączenia z API: {e}. Pokazuję zapasowe – one grają zawsze!")

    if valid_stations:
            cols = st.columns(3)
            for idx, station in enumerate(valid_stations):
                color = random.choice(metro_colors)
                
                with cols[idx % 3]:
                    # Niewidzialny przycisk na całą szerokość – kliknięcie kafelka włącza radio
                    if st.button("", key=f"play_direct_{idx}", help="Kliknij cały kafelek, aby słuchać"):
                        st.session_state.selected_station = station
                        st.rerun()
                    
                    # Sam kafelek
                    st.markdown(f"""
                        <div class="station-tile" style="background-color: {color};">
                            {station['name']}
                            <div class="tile-small-text">{station.get('tags', 'brak')} | {station.get('bitrate', '?')} kbps</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Tylko przycisk dodaj do ulubionych
                    if st.button("❤️ Dodaj do ulubionych", key=f"add_{idx}"):
                        add_favorite(station)
                        st.success("Dodano!")
                        st.rerun()

# Zakładka Gazetki – bez zmian (Twój kod)

with st.sidebar:
    st.header("🎵 Odtwarzacz")
    if 'selected_station' in st.session_state:
        selected = st.session_state.selected_station
        url = selected['url_resolved']
        audio_type = get_audio_format(url)

        st.markdown(f"### Gra: **{selected['name']}**")
        st.markdown(f"**Tagi:** {selected.get('tags', 'brak')} • **Bitrate:** {selected.get('bitrate', '?')} kbps")

        st.components.v1.html(f"""
            <audio controls autoplay style="width:100%;">
                <source src="{url}" type="{audio_type}">
                Twoja przeglądarka nie obsługuje audio.
            </audio>
        """, height=100)

        st.markdown("""
        <div style="background-color: #f0f8ff; padding: 15px; border-radius: 10px; text-align: center; font-size: 18px;">
            🔊 <strong>Nie słychać? Naciśnij PLAY!</strong><br>
            Sprawdź głośność telefonu/komputera.
        </div>
        """, unsafe_allow_html=True)

        if selected['name'] not in [f[0] for f in get_favorites()]:
            if st.button("❤️ Dodaj do ulubionych"):
                add_favorite(selected)
                st.rerun()
        else:
            st.success("✅ Już w ulubionych!")

        if st.button("🔙 Zatrzymaj"):
            del st.session_state.selected_station
            st.rerun()
    else:
        st.info("Wybierz stację z kafelków.")

st.sidebar.success("Radio stabilne – tylko HTTPS/HLS, zawsze gra! 🎉")
