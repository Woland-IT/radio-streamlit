# app.py

import streamlit as st
import random

from db import get_favorites, add_favorite, remove_favorite
from utils import (
    metro_colors, fallback_stations, search_stations,
    get_real_stream_url, station_overrides, get_audio_format
)
from components.tiles import render_station_tile
from streamlit_player import st_player

# ================================
# KONFIGURACJA STRONY
# ================================
st.set_page_config(page_title="Radio + Gazetki dla Seniora", layout="wide")

# Inicjalizacja stanu sesji
if 'favorites' not in st.session_state:
    st.session_state.favorites = get_favorites()
if 'selected_station' not in st.session_state:
    st.session_state.selected_station = None

# ================================
# GŁÓWNY LAYOUT: Kolumny – radio | odtwarzacz
# ================================
main_col, player_col = st.columns([3, 1])

with main_col:
    st.header("🇵🇱 Polskie Radio dla Seniora")
    st.markdown("### Kliknij wielki kolorowy kafelek – radio od razu gra po prawej! 🎶🔊")

    # Wyszukiwanie stacji
    query = st.text_input("🔍 Szukaj stacji (np. RMF, Eska, Trójka)", "")

    # Pobieranie stacji
    try:
        stations = search_stations(query=query, country="Poland", limit=100)
        st.success(f"Znaleziono {len(stations)} stacji online")
    except Exception as e:
        st.warning("Brak połączenia z API – ładuję listę zapasową (zawsze działa!)")
        stations = fallback_stations

    # Siatka 3 kolumny z kafelkami
    cols = st.columns(3)
    for idx, station in enumerate(stations):
        with cols[idx % 3]:
            render_station_tile(station, idx)

    # Sekcja promocji / gazetek (opcjonalnie możesz dodać tu render_promo_tile)
    st.markdown("---")
    st.subheader("🛒 Gazetki promocyjne")
    st.info("Wkrótce dodamy ładne kafelki z gazetkami Biedronka, Lidl, Dino itp. 😊")

with player_col:
    # ================================
    # SIDEBAR / PRAWY PANEL – ODTWARZACZ
    # ================================
    st.header("🎵 Teraz gra...")

    if st.session_state.selected_station:
        selected = st.session_state.selected_station
        original_url = selected.get('url_resolved') or selected.get('url', '')

        st.markdown(f"### **{selected['name']}** 🔊")
        st.caption(f"{selected.get('tags', 'brak')} • {selected.get('bitrate', '?')} kbps")

        # Zbieranie najlepszych URL-i do odtwarzania
        candidates = []

        # 1. Ręczne poprawki dla problematycznych stacji
        name_lower = selected['name'].lower()
        for key, urls in station_overrides.items():
            if key in name_lower:
                candidates.extend(urls)

        # 2. Automatyczne wykrywanie alternatyw
        real_urls = get_real_stream_url(selected['name'], original_url)
        for u in real_urls:
            if u not in candidates:
                candidates.append(u)

        # 3. Oryginalny URL na końcu
        if original_url and original_url not in candidates:
            candidates.append(original_url)

        # Wybierz pierwszy działający (lub pierwszy z listy)
        play_url = candidates[0] if candidates else original_url
        audio_type = get_audio_format(play_url)

        # Obsługa HLS (głównie Polskie Radio)
        if play_url.endswith('.m3u8') or 'playlist.m3u8' in play_url:
            try:
                st_player(play_url, playing=True, height=100)
                st.success("HLS stream załadowany")
            except:
                st.error("Błąd HLS – spróbuj innej stacji")
        else:
            # Standardowy HTML5 audio z debugiem i CORS
            cors_attr = 'crossOrigin="anonymous"' if "redcdn" in play_url.lower() else ""

            audio_html = f"""
            <audio controls autoplay style="width:100%; height:60px;" {cors_attr}>
                <source src="{play_url}" type="{audio_type}">
                Twoja przeglądarka nie obsługuje audio.
            </audio>
            <script>
                const audio = document.querySelector('audio');
                audio.volume = 0.8;
                audio.play().catch(e => console.error("Autoplay error:", e));
            </script>
            """
            st.components.v1.html(audio_html, height=120)

        # Przycisk zatrzymania
        if st.button("🔇 Zatrzymaj odtwarzanie", use_container_width=True):
            st.session_state.selected_station = None
            st.rerun()

        # Ulubione w odtwarzaczu
        if any(fav[0] == selected['name'] for fav in st.session_state.favorites):
            st.success("❤️ Już w ulubionych")
        else:
            if st.button("❤️ Dodaj do ulubionych", use_container_width=True):
                add_favorite(selected)
                st.session_state.favorites = get_favorites()
                st.rerun()

        st.markdown("---")
        st.markdown("**Nie słychać?** Naciśnij ▶️ PLAY i sprawdź głośność urządzenia 🔊")

    else:
        st.info("Wybierz stację z lewej strony 👈")
        st.markdown("### 🎄 Wesołych Świąt! 🎁")

# ================================
# STOPKA
# ================================
st.markdown("---")
st.caption("Aplikacja działa offline dzięki zapasowej liście stacji. Made with ❤️ dla Seniorów")