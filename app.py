import streamlit as st
from pyradios import RadioBrowser
import requests  # Na ewentualne future poprawki

# Konfiguracja
st.set_page_config(page_title="Radio + Gazetki Oficjalne", layout="wide")

# Zakładki
tab1, tab2 = st.tabs(["🎵 Radio Online", "🛒 Gazetki Oficjalne"])

# Fallback – statyczna lista popularnych polskich stacji (zawsze działa!)
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

with tab1:
    st.header("🇵🇱 Polskie Radio Online")
    st.markdown("Szukaj lub przeglądaj – jeśli API nie odpowie, ładuje się lista zapasowa!")

    query = st.text_input("Szukaj stacji (np. RMF, ZET, Trójka):", key="radio_search")

    # Lista stabilnych mirrorów API (możesz dodać więcej jeśli chcesz)
    possible_urls = [
        "https://de1.api.radio-browser.info",
        "https://de2.api.radio-browser.info",
        "https://nl1.api.radio-browser.info",
        "https://at1.api.radio-browser.info",
    ]

    stations = None
    connected_base = None

    for base in possible_urls:
        try:
            rb = RadioBrowser(base_url=base)
            if query:
                stations = rb.search(name=query, country="Poland", limit=50, order="clickcount", reverse=True)
            else:
                stations = rb.search(country="Poland", limit=50, order="clickcount", reverse=True)
            st.success(f"Połączono z API ({base}) – aktualne stacje! 🚀")
            connected_base = base
            break
        except Exception as e:
            st.info(f"Mirror {base} nie działa: {str(e)} – próbuję następny...")
            continue

    if stations is None:
        st.warning("Wszystkie mirrory API niedostępne. Ładuję listę zapasową – działa zawsze!")
        stations = fallback_stations

    if not stations:
        st.error("Brak stacji – sprawdź internet.")
    else:
        station_names = [f"{s['name']} ({s.get('tags', 'brak') or 'brak'} | {s.get('bitrate', '?')} kbps)" for s in stations]
        selected_idx = st.selectbox("Wybierz stację:", range(len(station_names)), format_func=lambda i: station_names[i])

        if selected_idx is not None:
            selected = stations[selected_idx]
            url = selected['url_resolved']
            st.markdown(f"### 🎶 Słuchasz: **{selected['name']}**")
            st.markdown(f"Tagi: {selected.get('tags', 'brak')} • Bitrate: {selected.get('bitrate', '?')} kbps")

            st.components.v1.html(f"""
                <audio controls autoplay style="width:100%;">
                    <source src="{url}" type="audio/mpeg">
                    <source src="{url}" type="audio/aac">
                    Twoja przeglądarka nie obsługuje audio.
                </audio>
            """, height=100)

# Zakładka Gazetki – bez zmian
with tab2:
    st.header("🛒 Gazetki Promocyjne – Linki Oficjalne")
    st.markdown("Kliknij logo → oficjalna gazetka!")

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

st.sidebar.success("Appka super stabilna – automatycznie wybiera działający serwer API! 🚀")
