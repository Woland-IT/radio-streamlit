import streamlit as st
from db import add_favorite, remove_favorite, get_favorites


def render_station_tile(station, idx):
    favorites = st.session_state.favorites
    is_favorite = any(fav[0] == station['name'] for fav in favorites)
    
    # Duży kafelek radia jako przycisk
    if st.button(station['name'], key=f"play_{idx}", use_container_width=True):
        print(f"START: Rozpoczynam odtwarzanie radia: {station['name']}")
        st.session_state.selected_station = station
        print(f"END: Zakończono ustawianie stacji: {station['name']}")
    
    # Małe przyciski pod kafelkiem
    st.markdown('<div class="favorite-button">', unsafe_allow_html=True)
    if is_favorite:
        if st.button("➖ Usuń z ulubionych", key=f"remove_{idx}", use_container_width=False):
            print(f"START: Rozpoczynam usuwanie {station['name']} z ulubionych")
            remove_favorite(station['name'])
            st.session_state.favorites = get_favorites()
            print(f"END: Zakończono usuwanie {station['name']} z ulubionych")
            st.success("Usunięto z ulubionych")
    else:
        if st.button("➕ Dodaj do ulubionych", key=f"add_{idx}", use_container_width=False):
            print(f"START: Rozpoczynam dodawanie {station['name']} do ulubionych, URL: {station.get('url_resolved', 'brak')}")
            add_favorite(station)
            st.session_state.favorites = get_favorites()
            print(f"END: Zakończono dodawanie {station['name']} do ulubionych")
            # Sprawdź czy jest w ulubionych
            updated_favorites = st.session_state.favorites
            is_now_favorite = any(fav[0] == station['name'] for fav in updated_favorites)
            print(f"POTWIERDZENIE: Stacja {station['name']} jest teraz w ulubionych: {is_now_favorite}")
            st.success("Dodano do ulubionych")
    st.markdown('</div>', unsafe_allow_html=True)


def render_promo_tile(promo: dict):
    color = promo.get("color", "#0072C6")
    html = f"""
        <div style="text-align: center; margin-bottom: 80px;">
            <a href="{promo['url']}" target="_blank">
                <div style="background-color: {color}; border-radius: 40px; padding: 100px 20px; box-shadow: 0 35px 70px rgba(0,0,0,0.5); height: 420px; display: flex; align-items: center; justify-content: center; flex-direction: column;">
                    <img src="{promo['image']}" width="220" style="margin-bottom: 40px;" alt="{promo['name']}">
                    <p style="font-size: 50px; color: white; margin: 0;">{promo['name']}</p>
                </div>
            </a>
        </div>
    """
    st.markdown(html, unsafe_allow_html=True)
