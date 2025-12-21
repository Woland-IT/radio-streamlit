import streamlit as st
from pyradios import RadioBrowser
import sqlite3
import random

# Konfiguracja
st.set_page_config(page_title="Radio + Gazetki dla Seniorów", layout="wide")

# Inicjalizacja bazy danych dla ulubionych stacji
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

# Zakładki
tab1, tab2 = st.tabs(["🎵 Radio Online", "🛒 Gazetki Promocyjne"])

# Fallback – statyczna lista popularnych polskich stacji
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

# Lista kolorów w stylu Windows 8 (Metro UI)
metro_colors = [
    "#0072C6",  # Niebieski
    "#D13438",  # Czerwony
    "#00A300",  # Zielony
    "#F09609",  # Pomarańczowy
    "#A200FF",  # Fioletowy
    "#E51400",  # Ciemnoczerwony
    "#339933",  # Ciemnozielony
    "#00ABA9",  # Turkusowy
    "#FFC40D",  # Żółty
    "#1BA1E2",  # Jasnoniebieski
]

with tab1:
    st.header("🇵🇱 Polskie Radio Online – Styl Windows 8")
    st.markdown("Duże kolorowe kafelki jak w Windows 8! Kliknij kafelek, by słuchać. Dodaj do ulubionych.")

    # Styl dla kafelków – duże, kolorowe, w stylu Metro
    st.markdown("""
    <style>
        .station-tile {
            background-color: #0072C6;  /* Domyślny kolor */
            border-radius: 5px;
            padding: 30px;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            color: white;
            margin: 10px 0;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            cursor: pointer;
            height: 150px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .station-tile:hover {
            opacity: 0.9;
        }
        .tile-small-text {
            font-size: 14px;
            margin-top: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Sekcja Ulubione – jako duże kolorowe kafelki
    st.subheader("❤️ Moje Ulubione Stacje")
    favorites = get_favorites()
    
    if favorites:
        cols = st.columns(3)  # Siatka 3 kolumn
        favorite_dicts = []
        
        for idx, row in enumerate(favorites):
            name = row[0]
            url = row[1]
            tags = row[2] if len(row) > 2 else "brak"
            bitrate = row[3] if len(row) > 3 else 128
            color = random.choice(metro_colors)  # Losowy kolor dla każdego kafelka
            favorite_dicts.append({"name": name, "url_resolved": url, "tags": tags, "bitrate": bitrate})
            
            with cols[idx % 3]:
                st.markdown(f"""
                    <div class="station-tile" style="background-color: {color};" onclick="this.nextElementSibling.click()">
                        {name}
                        <div class="tile-small-text">{tags} | {bitrate} kbps</div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("Słuchaj", key=f"fav_button_{name}_{idx}", help="Kliknij, by odtwarzać"):
                    st.session_state.selected_station = favorite_dicts[idx]
                
                if st.button("Usuń z ulubionych ❌", key=f"remove_{name}_{idx}"):
                    remove_favorite(name)
                    st.success("Usunięto z ulubionych!")
                    st.experimental_rerun()
    else:
        st.info("Brak ulubionych stacji. Dodaj je z kafelków poniżej!")

    # Wybrana stacja – odtwarzacz
        # Wybrana stacja – odtwarzacz (na górze, duży i wyraźny)
    if 'selected_station' in st.session_state:
        selected = st.session_state.selected_station
        url = selected['url_resolved']
        
        st.markdown(f"## 🎶 Teraz gramy: **{selected['name']}**")
        st.markdown(f"**Tagi:** {selected.get('tags', 'brak')} • **Bitrate:** {selected.get('bitrate', '?')} kbps")
        
        # Duży odtwarzacz
        st.audio(url, format="audio/mpeg")
        
        # Wyraźny komunikat dla seniora
        st.markdown("""
        <div style="background-color: #e6f7ff; padding: 20px; border-radius: 10px; text-align: center; font-size: 20px; margin: 20px 0;">
            🔊 <strong>Jeśli nie słychać muzyki – naciśnij przycisk PLAY 🔘 powyżej!</strong><br>
            Upewnij się, że głośność jest włączona w telefonie/komputerze.
        </div>
        """, unsafe_allow_html=True)
        
        # Przycisk dodaj do ulubionych
        fav_names = [f[0] for f in favorites]
        if selected['name'] not in fav_names:
            if st.button("❤️ Dodaj do ulubionych (szybki dostęp)", key=f"add_selected_{selected['name']}"):
                if add_favorite(selected):
                    st.success("Dodano do ulubionych!")
                    st.experimental_rerun()
        else:
            st.success("✅ Ta stacja jest już w Twoich ulubionych!")
        
        # Opcja powrotu
        if st.button("🔙 Wybierz inną stację"):
            del st.session_state.selected_station
           st.experimental_rerun()

    # Wyszukiwanie i lista stacji – duże kolorowe kafelki, więcej stacji (limit 100)
    st.subheader("🔍 Przeglądaj Polskie Stacje Radio")
    query = st.text_input("Wpisz nazwę stacji (np. RMF, ZET):", key="radio_search")

    stations = None
    try:
        rb = RadioBrowser()
        if query:
            stations = rb.search(name=query, country="Poland", limit=100, order="clickcount", reverse=True)
        else:
            stations = rb.search(country="Poland", limit=100, order="clickcount", reverse=True)
        st.success("Połączono z bazą – top polskie stacje!")
    except Exception as e:
        st.warning(f"Problem: {str(e)}. Używam listy zapasowej!")
        stations = fallback_stations if not query else [s for s in fallback_stations if query.lower() in s['name'].lower()]

    if not stations:
        st.error("Nie znaleziono stacji.")
    else:
        cols = st.columns(3)  # Siatka 3 kolumn
        for idx, station in enumerate(stations):
            color = random.choice(metro_colors)  # Losowy kolor Metro
            with cols[idx % 3]:
                st.markdown(f"""
                    <div class="station-tile" style="background-color: {color};" onclick="this.nextElementSibling.click()">
                        {station['name']}
                        <div class="tile-small-text">{station.get('tags', 'brak')} | {station.get('bitrate', '?')} kbps</div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("Słuchaj", key=f"station_button_{station['name']}_{idx}", help="Kliknij, by odtwarzać"):
                    st.session_state.selected_station = station
                
                if st.button("Dodaj do ulubionych ❤️", key=f"add_{station['name']}_{idx}"):
                    if add_favorite(station):
                        st.success("Dodano do ulubionych!")
                        st.experimental_rerun()
                    else:
                        st.error("Nie udało się dodać – może już jest?")

with tab2:
    st.header("🛒 Gazetki Promocyjne – Łatwy Dostęp")
    st.markdown("Kliknij na logo sklepu, by zobaczyć aktualne promocje!")

    promotions = [
        {"name": "Biedronka", "image": "https://www.biedronka.pl/sites/default/files/styles/logo/public/logo-biedronka.png", "url": "https://www.biedronka.pl/gazetki"},
        {"name": "Lidl", "image": "https://www.lidl.pl/assets/pl/logo.svg", "url": "https://www.lidl.pl/c/nasze-gazetki/s10008614"},
        {"name": "Kaufland", "image": "https://sklep.kaufland.pl/assets/img/kaufland-logo.svg", "url": "https://sklep.kaufland.pl/gazeta-reklamowa.html"},
        {"name": "Dino", "image": "https://marketdino.pl/themes/dino/assets/img/logo.svg", "url": "https://marketdino.pl/gazetki-promocyjne"},
        {"name": "Carrefour", "image": "https://www.carrefour.pl/themes/custom/carrefour/logo.svg", "url": "https://www.carrefour.pl/gazetka-handlowa"},
        {"name": "Leroy Merlin", "image": "https://www.leroymerlin.pl/img/logo-lm.svg", "url": "https://www.leroymerlin.pl/gazetka/"},
        {"name": "Bricomarché", "image": "https://www.bricomarche.pl/themes/custom/bricomarche/logo.png", "url": "https://www.bricomarche.pl/gazetka"},
        {"name": "Home&You", "image": "https://home-you.com/pl/img/logo.svg", "url": "https://home-you.com/pl/promocje"},
        {"name": "Westwing", "image": "https://www.westwing.pl/img/logo.svg", "url": "https://www.westwing.pl/campaign/current/"},
        {"name": "Empik (książki)", "image": "https://www.empik.com/static/img/empik-logo.svg", "url": "https://www.empik.com/promocje"},
        {"name": "Świat Książki", "image": "https://swiatksiazki.pl/img/logo.svg", "url": "https://swiatksiazki.pl/promocja-specjalna"},
    ]

    cols = st.columns(3)
    for idx, promo in enumerate(promotions):
        with cols[idx % 3]:
            st.markdown(f"""
                <div style="text-align: center; margin-bottom: 30px;">
                    <a href="{promo['url']}" target="_blank">
                        <img src="{promo['image']}" width="150" style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                        <p style="margin: 10px 0 0; font-weight: bold;">{promo['name']}</p>
                    </a>
                </div>
            """, unsafe_allow_html=True)

st.sidebar.success("Aplikacja w stylu Windows 8 – duże kafelki! 🚀")
