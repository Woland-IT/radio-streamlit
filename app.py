import streamlit as st
from pyradios import RadioBrowser
import sqlite3
from streamlit_audio_stream_player import st_audio_stream_player  # Nowy komponent!

# ================================
# KONFIGURACJA I DB (minimalna)
# ================================
st.set_page_config(page_title="Pro Radio PL", layout="wide")

@st.cache_resource
def get_conn():
    conn = sqlite3.connect('favorites.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS favorites (name TEXT PRIMARY KEY, url TEXT)')
    return conn

def get_favorites():
    c = get_conn().cursor()
    c.execute("SELECT name, url FROM favorites")
    return {row[0]: row[1] for row in c.fetchall()}

def add_favorite(name, url):
    c = get_conn().cursor()
    c.execute("INSERT OR REPLACE INTO favorites VALUES (?, ?)", (name, url))
    get_conn().commit()
    st.session_state.favorites = get_favorites()

def remove_favorite(name):
    c = get_conn().cursor()
    c.execute("DELETE FROM favorites WHERE name=?", (name,))
    get_conn().commit()
    st.session_state.favorites = get_favorites()

# Inicjalizacja stanu
if 'favorites' not in st.session_state:
    st.session_state.favorites = get_favorites()
if 'selected_station' not in st.session_state:
    st.session_state.selected_station = None

# ================================
# UI: WYSZUKIWANIE I STACJE
# ================================
st.header("🇵🇱 Pro Radio do Kuchni 🎶")
query = st.text_input("🔍 Szukaj stacji (np. RMF, Eska)", key="search")

rb = RadioBrowser()
stations = rb.search(name=query if query else "", country="Poland", limit=50, order="clickcount", reverse=True) or []

# Ulubione na górze
st.subheader("❤️ Ulubione")
fav_cols = st.columns(3)
for idx, (name, url) in enumerate(st.session_state.favorites.items()):
    with fav_cols[idx % 3]:
        if st.button(name, key=f"fav_{idx}", use_container_width=True):
            st.session_state.selected_station = {"name": name, "url": url}
            st.rerun()
        if st.button("❌ Usuń", key=f"rem_fav_{idx}"):
            remove_favorite(name)
            st.rerun()

# Inne stacje
st.subheader("Wszystkie stacje")
cols = st.columns(3)
favorite_names = set(st.session_state.favorites.keys())
for idx, station in enumerate([s for s in stations if s['name'] not in favorite_names]):
    with cols[idx % 3]:
        name = station['name']
        url = station.get('url_resolved') or station['url']
        if st.button(name, key=f"station_{idx}", use_container_width=True):
            st.session_state.selected_station = {"name": name, "url": url}
            st.rerun()
        if st.button("❤️ Dodaj", key=f"add_{idx}"):
            add_favorite(name, url)
            st.rerun()

# ================================
# FIXED FOOTER PLAYER (zawsze na dole)
# ================================
if st.session_state.selected_station:
    # CSS dla fixed footera
    st.markdown("""
    <style>
        .fixed-footer {
            position: fixed; bottom: 0; left: 0; width: 100%;
            background: #f0f2f6; padding: 10px; box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
            z-index: 1000;
        }
        .stApp { margin-bottom: 80px; }
    </style>
    """, unsafe_allow_html=True)

    footer = st.container()
    with footer:
        st.markdown('<div class="fixed-footer">', unsafe_allow_html=True)
        
        selected = st.session_state.selected_station
        st.markdown(f"**{selected['name']}** 🔊")
        
        # Nowy profesjonalny player!
        st_audio_stream_player(
            url=selected['url'],
            autoplay=True,
            show_controls=True,
            volume=0.8,
            visualizer_mode="bar",  # Lub "orb" dla innego stylu
            color="#0072C6",        # Custom kolor
            height=80
        )
        
        if st.button("🔇 Stop", use_container_width=True):
            st.session_state.selected_station = None
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("Wybierz stację powyżej 👆")

# Stopka
st.markdown("---")
st.caption("Pro Radio PL | Styczeń 2026 ❤️")