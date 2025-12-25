# components/tiles.py

import streamlit as st
from db import add_favorite, remove_favorite, get_favorites


def render_station_tile(station: dict, idx: int):
    # Pobierz aktualne ulubione
    if 'favorites' not in st.session_state:
        st.session_state.favorites = get_favorites()

    favorites = st.session_state.favorites
    is_favorite = any(fav[0] == station['name'] for fav in favorites)

    col1, col2 = st.columns([4, 1])

    with col1:
        # Duży przycisk – cały kafelek to przycisk
        if st.button(
            label=station['name'],
            key=f"play_btn_{idx}",
            use_container_width=True,
            type="primary"  # opcjonalnie, ładniejszy wygląd
        ):
            st.session_state.selected_station = station
            st.rerun()  # <--- TO JEST KLUCZOWE! Wymusza przeładowanie i aktualizację sidebaru

    with col2:
        # Mały przycisk ulubionych
        if is_favorite:
            if st.button("❤️", key=f"remove_fav_{idx}", help="Usuń z ulubionych"):
                remove_favorite(station['name'])
                st.session_state.favorites = get_favorites()
                st.rerun()
        else:
            if st.button("🤍", key=f"add_fav_{idx}", help="Dodaj do ulubionych"):
                add_favorite(station)
                st.session_state.favorites = get_favorites()
                st.rerun()

    # Opcjonalnie: tagi i bitrate pod nazwą
    st.caption(f"{station.get('tags', 'brak tagów')} • {station.get('bitrate', '?')} kbps")