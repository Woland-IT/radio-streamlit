import streamlit as st
import random
import urllib.parse

from db import get_favorites, add_favorite, remove_favorite
from utils import safe_url, get_audio_format, metro_colors, fallback_stations, search_stations
from ui import clickable_tile_html, promotion_tile_html
from components.tiles import render_station_tile
from streamlit_player import st_player

# ================================
# KONFIGURACJA
# ================================
st.set_page_config(page_title="Radio + Gazetki dla Seniora", layout="wide")

# CSS dla małych przycisków ulubionych
st.markdown("""
<style>
.favorite-button .stButton button {
    font-size: 12px;
    padding: 4px 8px;
    background-color: #e0e0e0;
    border: 1px solid #bbb;
    border-radius: 4px;
    color: #333;
}
.favorite-button .stButton button:hover {
    background-color: #d0d0d0;
}
.radio-tile .stButton button {
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
    border: none;
    outline: none;
}
.radio-tile .stButton button:hover {
    transform: translateY(-40px) scale(1.12);
    box-shadow: 0 80px 140px rgba(0,0,0,0.6);
}
.radio-tile .stButton button p {
    font-size: 34px;
    margin-top: 30px;
    opacity: 0.9;
}
</style>
""", unsafe_allow_html=True)

# (helpers and constants moved to utils.py)

# ================================
# ZAKŁADKI
# ================================
tab1, tab2 = st.tabs(["🎵 Radio Online", "🛒 Gazetki Promocyjne"])

# Inicjalizacja ulubionych w session_state
if 'favorites' not in st.session_state:
    st.session_state.favorites = get_favorites()

with tab1:
    st.header("🇵🇱 Polskie Radio dla Seniora")
    st.markdown("### Kliknij cały wielki kolorowy kafelek – radio gra od razu po prawej! 🎶🔊")

    # Styl kafelków – czysty i piękny
    st.markdown("""
    <style>
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
        a.tile-link {
            text-decoration: none;
            color: inherit;
            display: block;
            width: 100%;
            height: 100%;
        }
    </style>
    """, unsafe_allow_html=True)

    # === Ulubione ===
    st.subheader("❤️ Moje Ulubione")
    favorites = st.session_state.favorites
    if favorites:
        cols = st.columns(3)
        for idx, row in enumerate(favorites):
            name, url, tags, bitrate = row[0], safe_url(row[1]), row[2] if len(row)>2 else "brak", row[3] if len(row)>3 else 128
            if not url or not url.startswith("https://"):
                continue
            color = random.choice(metro_colors)
            station = {"name": name, "url_resolved": url, "tags": tags, "bitrate": bitrate}
            with cols[idx % 3]:
                render_station_tile(station, f"fav_{idx}")
    else:
        st.info("Brak ulubionych – kliknij ❤️ pod kafelkiem poniżej!")

    # === Wszystkie stacje ===
    st.subheader("🔍 Wszystkie działające stacje")
    query = st.text_input("Szukaj (np. RMF, Trójka):", key="search")

    valid_stations = fallback_stations[:]
    try:
        stations = search_stations(query)
        station_dict = {}
        for station in stations:
            url = safe_url(station.get('url_resolved', ''))
            if url and url.startswith("https://"):
                s = station.copy()
                s['url_resolved'] = url
                name = s['name']
                if name not in station_dict:
                    station_dict[name] = s
        valid_stations.extend(station_dict.values())
        st.success(f"Znaleziono {len(valid_stations)} stacji – kliknij kafelek!")
    except Exception as e:
        st.warning(f"Brak połączenia: {e}. Zapasowe zawsze działają!")

    if valid_stations:
        cols = st.columns(3)
        favorites = st.session_state.favorites
        for idx, station in enumerate(valid_stations):
            color = random.choice(metro_colors)
            bitrate = station.get('bitrate', '?')
            with cols[idx % 3]:
                render_station_tile(station, idx)

# ================================
# ZAKŁADKA GAZETKI
# ================================
with tab2:
    st.header("🛒 Gazetki Promocyjne – Wielkie Kafelki")
    st.markdown("Kliknij kafelek sklepu → otwiera się gazetka")

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
        with cols[idx % 3]:
            html = promotion_tile_html(promo)
            st.markdown(html, unsafe_allow_html=True)

# ================================
# SIDEBAR – ODTWARZACZ
# ================================
with st.sidebar:
    st.header("🎵 Teraz gra...")
    if 'selected_station' in st.session_state:
        selected = st.session_state.selected_station
        url = selected['url_resolved']
        
        st.markdown(f"### **{selected['name']}** 🔊🎶")
        st.markdown(f"**Tagi:** {selected.get('tags', 'brak')} • **Bitrate:** {selected.get('bitrate', '?')} kbps")
        
        print(f"SIDEBAR: Rozpoczynam ładowanie radia: {selected['name']}, URL: {url}")
        
        # Wybór formatu audio
        format_option = st.selectbox("Wybierz format audio:", ["Automatycznie", "MP3", "AAC", "HLS"], key="audio_format")
        
        try:
            print(f"SIDEBAR: Próbuję st_player dla URL: {url}")
            st_player(url, playing=True, height=100)
            print(f"SIDEBAR: st_player załadowany pomyślnie dla {selected['name']}")
        except Exception as e:
            print(f"SIDEBAR: Błąd st_player: {e}, używam fallback <audio>")
            st.warning(f"Player HLS nie działa: {e}. Próbuję standardowy audio.")
            audio_type = "audio/mpeg" if format_option == "MP3" else "audio/aac" if format_option == "AAC" else get_audio_format(url)
            print(f"SIDEBAR: Używam <audio> z type={audio_type}")
            st.components.v1.html(f"""
                <audio controls autoplay style="width:100%;">
                    <source src="{url}" type="{audio_type}">
                    Twoja przeglądarka nie obsługuje audio.
                </audio>
            """, height=100)
            print(f"SIDEBAR: <audio> załadowany dla {selected['name']}")
        
        st.markdown("""
        <div style="background-color: #e6f7ff; padding: 50px; border-radius: 30px; text-align: center; font-size: 32px; margin: 40px 0;">
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
            print(f"SIDEBAR: Zatrzymuję radio {selected['name']}")
