import streamlit as st
from pyradios import RadioBrowser
import sqlite3
import random
import urllib.parse

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

# Walidacja URL – filtrujemy problematyczne linki i wymuszamy HTTPS
def safe_url(url):
    if any(x in url for x in ["localhost", "195.150.20", "127.0.0.1"]):
        return None
    if url.startswith("http://"):
        url = url.replace("http://", "https://", 1)
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return None
    return url

# Dynamiczny format audio
def get_audio_format(url):
    if url.endswith('.mp3') or '.mp3' in url:
        return "audio/mpeg"
    elif url.endswith('.aac') or '.aac' in url or '.aacp' in url:
        return "audio/aac"
    elif url.endswith('.m3u8') or '.m3u8' in url:
        return "application/x-mpegURL"
    else:
        return "audio/mpeg"

# Kolory w stylu Metro (Windows 8)
metro_colors = [
    "#0072C6", "#D13438", "#00A300", "#F09609", "#A200FF",
    "#E51400", "#339933", "#00ABA9", "#FFC40D", "#1BA1E2"
]

# Zakładki
tab1, tab2 = st.tabs(["🎵 Radio Online", "🛒 Gazetki Promocyjne"])

# === ZAKŁADKA RADIO ===
with tab1:
    st.header("🇵🇱 Polskie Radio – Kafelki jak w Windows 8!")
    st.markdown("Kliknij kafelek → słuchaj w panelu po prawej")

    # Styl kafelków stacji
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

    # === Ulubione stacje ===
    st.subheader("❤️ Moje Ulubione Stacje")
    favorites = get_favorites()
    
    if favorites:
        cols = st.columns(3)
        favorite_dicts = []
        for idx, row in enumerate(favorites):
            name = row[0]
            url = safe_url(row[1])
            if not url:
                continue
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
                    if st.button("Wybierz", key=f"fav_play_{idx}"):
                        st.session_state.selected_station = favorite_dicts[idx]
                        st.rerun()
                with col_btn2:
                    if st.button("Usuń ❌", key=f"fav_del_{idx}"):
                        remove_favorite(name)
                        st.success("Usunięto!")
                        st.rerun()
    else:
        st.info("Brak ulubionych. Dodaj stacje z listy poniżej!")

    # === Wyszukiwanie i przeglądanie stacji ===
    st.subheader("🔍 Wszystkie Polskie Stacje")
    query = st.text_input("Szukaj stacji (np. RMF, Eska, Trójka):", key="search")

    try:
        rb = RadioBrowser()
        if query:
            stations = rb.search(name=query, country="Poland", limit=100, order="clickcount", reverse=True)
        else:
            stations = rb.search(country="Poland", limit=100, order="clickcount", reverse=True)
        
        valid_stations = []
        for station in stations:
            safe_station_url = safe_url(station['url_resolved'])
            if safe_station_url:
                valid_station = station.copy()
                valid_station['url_resolved'] = safe_station_url
                valid_stations.append(valid_station)
        
        if valid_stations:
            st.success(f"Znaleziono {len(valid_stations)} działających stacji!")
        else:
            st.warning("Brak działających stacji z poprawnymi linkami.")
        
    except Exception as e:
        st.warning(f"Brak połączenia: {e}. Spróbuj później.")
        valid_stations = []

    if valid_stations:
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
                    if st.button("Wybierz", key=f"play_{idx}"):
                        st.session_state.selected_station = station
                        st.rerun()
                with col2:
                    if st.button("❤️ Dodaj", key=f"add_{idx}"):
                        if add_favorite(station):
                            st.success("Dodano!")
                            st.rerun()

# === ZAKŁADKA GAZETKI ===
with tab2:
    st.header("🛒 Gazetki Promocyjne – Duże Kafelki")
    st.markdown("Kliknij kafelek sklepu → otwiera się oficjalna gazetka")

    # Styl kafelków sklepów
    st.markdown("""
    <style>
        .shop-tile {
            background-color: #0072C6;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            color: white;
            margin: 15px 0;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
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

    # Tworzymy 3 kolumny
    col1, col2, col3 = st.columns(3)

    # Wypełniamy je po kolei
    for idx, promo in enumerate(promotions):
        color = promo.get("color", random.choice(metro_colors))
        
        # Wybieramy kolumnę cyklicznie
        if idx % 3 == 0:
            col = col1
        elif idx % 3 == 1:
            col = col2
        else:
            col = col3
        
with col:
    st.markdown(
        f'<a href="{promo["url"]}" target="_blank" style="text-decoration: none;">'
        f'<div class="shop-tile" style="background-color: {color};">'
        f'<img src="{promo["image"]}" width="120" style="margin-bottom: 10px;">'
        f'<div>{promo["name"]}</div>'
        f'</div></a>',
        unsafe_allow_html=True
    )

# === SIDEBAR – ODTWARZACZ RADIA ===
with st.sidebar:
    st.header("🎵 Odtwarzacz Radia")
    if 'selected_station' in st.session_state:
        selected = st.session_state.selected_station
        url = selected['url_resolved']
        audio_format = get_audio_format(url)
        
        st.markdown(f"### Gra: **{selected['name']}**")
        st.markdown(f"**Tagi:** {selected.get('tags', 'brak')} • **Bitrate:** {selected.get('bitrate', '?')} kbps")
        
        st.audio(url, format=audio_format)
        
        st.markdown("""
        <div style="background-color: #f0f8ff; padding: 15px; border-radius: 10px; text-align: center; font-size: 18px; margin: 15px 0;">
            🔊 <strong>Nie słychać? Naciśnij PLAY 🔘!</strong><br>
            Sprawdź głośność w telefonie/komputerze.
        </div>
        """, unsafe_allow_html=True)
        
        fav_names = [f[0] for f in favorites]
        if selected['name'] not in fav_names:
            if st.button("❤️ Dodaj do ulubionych", key="add_main"):
                if add_favorite(selected):
                    st.success("Dodano!")
                    st.rerun()
        else:
            st.success("✅ Już w ulubionych!")
        
        if st.button("🔙 Zatrzymaj radio"):
            if 'selected_station' in st.session_state:
                del st.session_state.selected_station
            st.rerun()
    else:
        st.info("Wybierz stację z kafelków po lewej.")

st.sidebar.success("Aplikacja dla Seniorów – duże kafelki wszędzie! 🎉")
