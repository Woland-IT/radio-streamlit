# app.py

import streamlit as st
import json
import os

from utils import (
    get_real_stream_url, station_overrides, get_audio_format,
    fallback_stations, search_stations
)
from components.tiles import render_station_tile
from streamlit_player import st_player
from db import get_favorites, add_favorite

# ================================
# KONFIGURACJA STRONY
# ================================
st.set_page_config(page_title="Radio + Gazetki + Design dla Seniora", layout="wide")

# Inicjalizacja stanu sesji
if 'favorites' not in st.session_state:
    st.session_state.favorites = get_favorites()
if 'selected_station' not in st.session_state:
    st.session_state.selected_station = None

# ================================
# ŁADOWANIE JSONÓW
# ================================
def load_json(file_name):
    json_path = file_name
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Błąd odczytu {file_name}: {e}")
            return []
    else:
        st.warning(f"Nie znaleziono pliku {file_name} – dodaj go do folderu z aplikacją.")
        return []

promotions = load_json("promotions.json")  # gazetki spożywcze itd.
design_fashion = load_json("design_fashion.json")  # design wnętrz + moda premium

# ================================
# ZAKŁADKI
# ================================
tab1, tab2, tab3 = st.tabs(["🎵 Radio Online", "🛒 Gazetki i Sklepy", "🏡 Design i Moda Premium"])

# ==================================================================
# ZAKŁADKA 1: RADIO
# ==================================================================
with tab1:
    col_radio, col_player = st.columns([3, 1])

    with col_radio:
        st.header("🇵🇱 Polskie Radio dla Seniora")
        st.markdown("### Kliknij wielki kafelek – radio gra od razu po prawej! 🎶🔊")

        query = st.text_input("🔍 Szukaj stacji (np. RMF, Eska, Trójka)", key="radio_search")

        try:
            stations = search_stations(query=query, country="Poland", limit=100)
            st.success(f"Znaleziono {len(stations)} stacji")
        except:
            st.warning("Brak połączenia – ładuję listę zapasową")
            stations = fallback_stations

        cols = st.columns(3)
        for idx, station in enumerate(stations):
            with cols[idx % 3]:
                render_station_tile(station, idx)

    with col_player:
        st.header("🎵 Teraz gra...")

        if st.session_state.selected_station:
            selected = st.session_state.selected_station
            original_url = selected.get('url_resolved') or selected.get('url', '')

            st.markdown(f"### **{selected['name']}** 🔊")
            st.caption(f"{selected.get('tags', 'brak')} • {selected.get('bitrate', '?')} kbps")

            candidates = []
            name_lower = selected['name'].lower()
            for key, urls in station_overrides.items():
                if key in name_lower:
                    candidates.extend(urls)
            real_urls = get_real_stream_url(selected['name'], original_url)
            for u in real_urls:
                if u not in candidates:
                    candidates.append(u)
            if original_url and original_url not in candidates:
                candidates.append(original_url)

            play_url = candidates[0] if candidates else original_url
            audio_type = get_audio_format(play_url)

            if play_url.endswith('.m3u8') or 'playlist.m3u8' in play_url:
                try:
                    st_player(play_url, playing=True, height=100)
                except:
                    st.error("Błąd HLS")
            else:
                cors_attr = 'crossOrigin="anonymous"' if "redcdn" in play_url.lower() else ""
                audio_html = f"""
                <audio controls autoplay style="width:100%; height:60px;" {cors_attr}>
                    <source src="{play_url}" type="{audio_type}">
                </audio>
                <script>document.querySelector('audio').volume = 0.8;</script>
                """
                st.components.v1.html(audio_html, height=120)

            if st.button("🔇 Zatrzymaj", use_container_width=True):
                st.session_state.selected_station = None
                st.rerun()

            if any(fav[0] == selected['name'] for fav in st.session_state.favorites):
                st.success("❤️ W ulubionych")
            else:
                if st.button("❤️ Dodaj do ulubionych", use_container_width=True):
                    add_favorite(selected)
                    st.session_state.favorites = get_favorites()
                    st.rerun()

            st.markdown("**Nie słychać?** Naciśnij ▶️ i sprawdź głośność 🔊")

        else:
            st.info("Wybierz stację z lewej 👈")
            st.markdown("### 🎄 Wesołych Świąt! 🎅")

# ==================================================================
# ZAKŁADKA 2: GAZETKI SPOŻYWCZE
# ==================================================================
with tab2:
    st.header("🛒 Aktualne Gazetki Promocyjne")
    st.markdown("### Kliknij nazwę sklepu → otwiera się oficjalna gazetka")

    if not promotions:
        st.info("Brak danych. Sprawdź plik `promotions.json`.")
    else:
        cols = st.columns(3)
        for idx, promo in enumerate(promotions):
            with cols[idx % 3]:
                color = promo.get("color", "#0072C6")
                name = promo["name"]
                url = promo["url"]

                html = f"""
                <div style="text-align: center; margin: 40px 0;">
                    <a href="{url}" target="_blank" style="text-decoration: none;">
                        <div style="
                            background-color: {color};
                            border-radius: 40px;
                            padding: 100px 20px;
                            box-shadow: 0 30px 60px rgba(0,0,0,0.4);
                            min-height: 380px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            transition: all 0.5s ease;
                            cursor: pointer;
                        "
                        onmouseover="this.style.transform='translateY(-30px) scale(1.1)'; this.style.boxShadow='0 60px 120px rgba(0,0,0,0.5)'"
                        onmouseout="this.style.transform='translateY(0) scale(1)'; this.style.boxShadow='0 30px 60px rgba(0,0,0,0.4)'">
                            <p style="
                                font-size: 60px;
                                color: white;
                                margin: 0;
                                font-weight: bold;
                                text-shadow: 2px 2px 8px rgba(0,0,0,0.5);
                            ">{name}</p>
                        </div>
                    </a>
                </div>
                """
                st.markdown(html, unsafe_allow_html=True)

# ==================================================================
# ZAKŁADKA 3: DESIGN I MODA PREMIUM
# ==================================================================
with tab3:
    st.header("🏡 Design Wnętrz i Moda Premium")
    st.markdown("### Kliknij nazwę sklepu → promocje na meble, dekoracje i markowe ubrania")

    if not design_fashion:
        st.info("Brak danych. Dodaj lub sprawdź plik `design_fashion.json`.")
    else:
        cols = st.columns(3)
        for idx, promo in enumerate(design_fashion):
            with cols[idx % 3]:
                color = promo.get("color", "#8E44AD")
                name = promo["name"]
                url = promo["url"]

                html = f"""
                <div style="text-align: center; margin: 40px 0;">
                    <a href="{url}" target="_blank" style="text-decoration: none;">
                        <div style="
                            background-color: {color};
                            border-radius: 40px;
                            padding: 100px 20px;
                            box-shadow: 0 30px 60px rgba(0,0,0,0.4);
                            min-height: 380px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            transition: all 0.5s ease;
                            cursor: pointer;
                        "
                        onmouseover="this.style.transform='translateY(-30px) scale(1.1)'; this.style.boxShadow='0 60px 120px rgba(0,0,0,0.5)'"
                        onmouseout="this.style.transform='translateY(0) scale(1)'; this.style.boxShadow='0 30px 60px rgba(0,0,0,0.4)'">
                            <p style="
                                font-size: 60px;
                                color: white;
                                margin: 0;
                                font-weight: bold;
                                text-shadow: 2px 2px 8px rgba(0,0,0,0.5);
                            ">{name}</p>
                        </div>
                    </a>
                </div>
                """
                st.markdown(html, unsafe_allow_html=True)

# ================================
# STOPKA
# ================================
st.markdown("---")
st.caption("Radio + Gazetki + Design dla Seniora ❤️ | Edytuj pliki JSON, by dodać własne sklepy!")