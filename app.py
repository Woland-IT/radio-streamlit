import streamlit as st
from pyradios import RadioBrowser
import sqlite3
import random

# Konfiguracja
st.set_page_config(page_title="Radio + Gazetki dla Seniorów", layout="wide")

# Baza danych ulubionych
conn = sqlite3.connect('favorites.db')
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

# Kolory Metro (Windows 8 style)
metro_colors = [
    "#0072C6", "#D13438", "#00A300", "#F09609", "#A200FF",
    "#E51400", "#339933", "#00ABA9", "#FFC40D", "#1BA1E2"
]

# Fallback stacje
fallback_stations = [
    {"name": "Polskie Radio Jedynka", "url_resolved": "http://mp3.polskieradio.pl:8900/;stream.mp3", "tags": "news, talk", "bitrate": 128},
    {"name": "Polskie Radio Dwójka", "url_resolved": "http://mp3.polskieradio.pl:8902/;stream.mp3", "tags": "classical", "bitrate": 128},
    {"name": "Polskie Radio Trójka", "url_resolved": "http://mp3.polskieradio.pl:8904/;stream.mp3", "tags": "music, alternative", "bitrate": 128},
    {"name": "RMF FM", "url_resolved": "https://rs101-krk.rmfstream.pl/rmf_fm", "tags": "pop, hits", "bitrate": 128},
    {"name": "Radio ZET", "url_resolved": "https://n-15-21.dcs.redcdn.pl/sc/o2/Eurozet/live/audio.livx", "tags": "pop", "bitrate": 128},
    {"name": "VOX FM", "url_resolved": "https://ic2.smcdn.pl/3990-1.mp3", "tags": "hits", "bitrate": 128},
    {"name": "Eska Warszawa", "url_resolved": "https://stream.open.fm/1", "tags": "pop, dance", "bitrate": 128},
    {"name": "Antyradio", "url_resolved": "https://n-15-21.dcs.redcdn.pl/sc/o2/Eurozet/live/antyradio.livx", "tags": "rock", "bitrate": 128},
]

# Zakładki
tab1, tab2 = st.tabs(["🎵 Radio Online", "🛒 Gazetki Promocyjne"])

with tab1:
    st.header("🇵🇱 Polskie Radio – Duże Kafelki jak w Windows 8!")
    st.markdown("Kliknij kolorowy kafelek, by słuchać radia. Dodaj do ulubionych ❤️")

    # Styl kafelków
    st.markdown("""
    <style>
        .station-tile {
            background-color: #0072C6;
            border-radius: 8px;
            padding: 30px;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            color: white;
            margin: 10px 0;
            box-shadow: 0 6px 12px rgba(0,0,0,0.2);
            height: 160px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
        }
        .tile-small-text {
            font-size: 16px;
            margin-top: 8px;
            opacity: 0.9;
        }
    </style>
    """, unsafe_allow_html=True)

    # === ULUBIONE ===
    st.subheader("❤️ Moje Ulubione Stacje")
    favorites = get_favorites()
    
    if favorites:
        cols = st.columns(3)
        favorite_dicts = []
        for idx, row in enumerate(favorites):
            name = row[0]
            url = row[1]
            tags = row[2] if len(row) > 2 else "brak"
            bitrate = row[3] if len(row) > 3 else 128
            color = random.choice(metro_colors)
            favorite_dicts.append({"name": name, "url_resolved": url, "tags": tags, "bitrate": bitrate})
            
            with cols[idx % 3]:
                st.markdown(f"""
                    <div class="station-tile" style="background-color: {color};">
                        {name}
                        <div class="tile-small-text">{tags} | {bitrate} kbps</div>
                    </div>
                """, unsafe_allow_html=True)
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("Słuchaj", key=f"fav_play_{idx}"):
                        st.session_state.selected_station = favorite_dicts[idx]
                        st.rerun()
                with col_btn2:
                    if st.button("Usuń ❌", key=f"fav_del_{idx}"):
                        remove_favorite(name)
                        st.success("Usunięto!")
                        st.rerun()
    else:
        st.info("Brak ulubionych. Dodaj stacje z listy poniżej!")

    # === ODTWARZACZ ===
    if 'selected_station' in st.session_state:
        selected = st.session_state.selected_station
        url = selected['url_resolved']
        
        st.markdown(f"## 🎶 Gra: **{selected['name']}**")
        st.markdown(f"**Tagi:** {selected.get('tags', 'brak')} • **Bitrate:** {selected.get('bitrate', '?')} kbps")
        
        st.audio(url, format="audio/mpeg")
        
        st.markdown("""
        <div style="background-color: #f0f8ff; padding: 20px; border-radius: 12px; text-align: center; font-size: 22px; margin: 20px 0;">
            🔊 <strong>Nie słychać? Naciśnij przycisk PLAY 🔘 powyżej!</strong><br>
            Sprawdź głośność w telefonie lub komputerze.
        </div>
        """, unsafe_allow_html=True)
        
        fav_names = [f[0] for f in favorites]
        if selected['name'] not in fav_names:
            if st.button("❤️ Dodaj do ulubionych", key="add_main"):
                if add_favorite(selected):
                    st.success("Dodano do ulubionych!")
                    st.rerun()
        else:
            st.success("✅ Już w ulubionych!")
        
        if st.button("🔙 Wybierz inną stację"):
            if 'selected_station' in st.session_state:
                del st.session_state.selected_station
            st.rerun()

    # === PRZEGLĄDANIE STACJI ===
    st.subheader("🔍 Wszystkie Polskie Stacje")
    query = st.text_input("Szukaj stacji (np. RMF, Eska, Trójka):", key="search")

    try:
        rb = RadioBrowser()
        if query:
            stations = rb.search(name=query, country="Poland", limit=100, order="clickcount", reverse=True)
        else:
            stations = rb.search(country="Poland", limit=100, order="clickcount", reverse=True)
        st.success("Połączono z bazą stacji!")
    except:
        st.warning("Brak internetu – używam listy zapasowej.")
        stations = [s for s in fallback_stations if query.lower() in s['name'].lower()] if query else fallback_stations

    if stations:
        cols = st.columns(3)
        for idx, station in enumerate(stations):
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
                    if st.button("Słuchaj", key=f"play_{idx}"):
                        st.session_state.selected_station = station
                        st.rerun()
                with col2:
                    if st.button("❤️ Dodaj", key=f"add_{idx}"):
                        if add_favorite(station):
                            st.success("Dodano!")
                            st.rerun()
    else:
        st.error("Nie znaleziono stacji.")

# === ZAKŁADKA GAZETKI ===
with tab2:
    st.header("🛒 Gazetki Promocyjne")
    st.markdown("Kliknij logo sklepu → otwiera się oficjalna gazetka")

    promotions = [
        {"name": "Biedronka", "image": "https://www.biedronka.pl/sites/default/files/styles/logo/public/logo-biedronka.png", "url": "https://www.biedronka.pl/gazetki"},
        {"name": "Lidl", "image": "https://www.lidl.pl/assets/pl/logo.svg", "url": "https://www.lidl.pl/c/nasze-gazetki/s10008614"},
        {"name": "Kaufland", "image": "https://sklep.kaufland.pl/assets/img/kaufland-logo.svg", "url": "https://sklep.kaufland.pl/gazeta-reklamowa.html"},
        {"name": "Dino", "image": "https://marketdino.pl/themes/dino/assets/img/logo.svg", "url": "https://marketdino.pl/gazetki-promocyjne"},
        {"name": "Carrefour", "image": "https://www.carrefour.pl/themes/custom/carrefour/logo.svg", "url": "https://www.carrefour.pl/gazetka-handlowa"},
        {"name": "Leroy Merlin", "image": "https://www.leroymerlin.pl/img/logo-lm.svg", "url": "https://www.leroymerlin.pl/gazetka/"},
        {"name": "Bricomarché", "image": "https://www.bricomarche.pl/themes/custom/bricomarche/logo.png", "url": "https://www.bricomarche.pl/gazetka"},
        {"name": "Empik", "image": "https://www.empik.com/static/img/empik-logo.svg", "url": "https://www.empik.com/promocje"},
    ]

    cols = st.columns(3)
    for idx, promo in enumerate(promotions):
        with cols[idx % 3]:
            st.markdown(f"""
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{promo['url']}" target="_blank">
                        <img src="{promo['image']}" width="180" style="border-radius: 12px; box-shadow: 0 6px 12px rgba(0,0,0,0.2);">
                        <p style="margin-top: 12px; font-size: 20px; font-weight: bold;">{promo['name']}</p>
                    </a>
                </div>
            """, unsafe_allow_html=True)

st.sidebar.success("Radio dla Seniorów – duże kafelki, proste sterowanie! 🎉")
