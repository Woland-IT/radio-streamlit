import streamlit as st
from pyradios import RadioBrowser

# Konfiguracja
st.set_page_config(page_title="Proste Radio + Gazetki", layout="wide")
st.markdown("<h1 style='text-align: center; font-size: 50px;'>🎵 Proste Radio i Gazetki 🛒</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 30px;'>Kliknij dużą ikonę – gra od razu! 😊</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🎵 Radio Online", "🛒 Gazetki Promocyjne"])

# Fallback – tylko sprawdzone HTTPS streamy (grudzień 2025)
fallback_stations = [
    {"name": "RMF FM", "url_resolved": "https://rs101-krk.rmfstream.pl/rmf_fm", "tags": "pop, hits", "bitrate": 128},
    {"name": "RMF Classic", "url_resolved": "https://rs201-krk.rmfstream.pl/rmf_classic", "tags": "classical, film", "bitrate": 128},
    {"name": "Radio ZET", "url_resolved": "https://n-15-21.dcs.redcdn.pl/sc/o2/Eurozet/live/audio.livx", "tags": "pop", "bitrate": 128},
    {"name": "VOX FM", "url_resolved": "https://ic2.smcdn.pl/3990-1.mp3", "tags": "hits", "bitrate": 128},
    {"name": "Eska", "url_resolved": "https://stream.open.fm/1", "tags": "pop, dance", "bitrate": 128},
    {"name": "Antyradio", "url_resolved": "https://n-15-21.dcs.redcdn.pl/sc/o2/Eurozet/live/antyradio.livx", "tags": "rock", "bitrate": 128},
    {"name": "Złote Przeboje", "url_resolved": "https://stream.open.fm/74", "tags": "oldies", "bitrate": 128},
    {"name": "Polskie Radio Jedynka", "url_resolved": "https://stream.polskieradio.pl/sls/1/pr1.aac", "tags": "news, talk", "bitrate": 128},
    {"name": "Polskie Radio Dwójka", "url_resolved": "https://stream.polskieradio.pl/sls/1/pr2.aac", "tags": "classical", "bitrate": 128},
    {"name": "Polskie Radio Trójka", "url_resolved": "https://stream.polskieradio.pl/sls/1/pr3.aac", "tags": "alternative", "bitrate": 128},
]

with tab1:
    st.header("🇵🇱 Ulubione stacje – duże przyciski")

    favorite = [
        {"name": "RMF Classic", "emoji": "🎻"},
        {"name": "Złote Przeboje", "emoji": "🕺"},
        {"name": "Polskie Radio Trójka", "emoji": "🎸"},
        {"name": "Polskie Radio Dwójka", "emoji": "🎼"},
        {"name": "Polskie Radio Jedynka", "emoji": "📰"},
        {"name": "RMF FM", "emoji": "🔥"},
        {"name": "Radio ZET", "emoji": "💥"},
        {"name": "VOX FM", "emoji": "🎉"},
        {"name": "Eska", "emoji": "🥳"},
        {"name": "Antyradio", "emoji": "🤘"},
    ]

    cols = st.columns(2)
    for idx, s in enumerate(favorite):
        with cols[idx % 2]:
            is_selected = st.session_state.get('current_name', '') == s['name']
            if st.button(f"{s['emoji']} {s['name']}", key=f"fav_btn_{idx}", use_container_width=True, type="primary" if is_selected else "secondary"):
                st.session_state.query = s['name']
                st.rerun()

    st.markdown("<h2 style='font-size: 40px; text-align: center;'>🔍 Wyszukaj stację</h2>", unsafe_allow_html=True)
    query = st.text_input("Szukaj", value=st.session_state.get('query', ''), placeholder="Wpisz np. RMF, ZET...", label_visibility="hidden")

    # API z filtracją tylko HTTPS
    stations = fallback_stations
    mirror_list = ["https://de1.api.radio-browser.info", "https://de2.api.radio-browser.info", "https://nl1.api.radio-browser.info", "https://at1.api.radio-browser.info"]

    connected = False
    for mirror in mirror_list:
        try:
            rb = RadioBrowser(base_url=mirror)
            api_stations = rb.search(name=query if query else None, country="Poland" if not query else None, limit=50, order="clickcount", reverse=True)
            https_stations = [s for s in api_stations if s['url_resolved'].startswith('https://')]
            if https_stations:
                stations = https_stations
                st.success(f"API działa – tylko bezpieczne HTTPS! 🚀")
                connected = True
                break
        except:
            continue

    if not connected:
        st.warning("API nie dało HTTPS – używam sprawdzonej listy!")

    # Bezpieczny selectbox
    if not stations:
        st.error("Brak stacji.")
    else:
        station_names = [f"{s['name']} ({s.get('tags', 'brak')} | {s.get('bitrate', '?')} kbps)" for s in stations]
        default_idx = 0
        if 'current_name' in st.session_state:
            for i, s in enumerate(stations):
                if s['name'] == st.session_state.current_name:
                    default_idx = i
                    break

        selected_idx = st.selectbox("Wybierz stację:", options=range(len(station_names)), index=default_idx, format_func=lambda i: station_names[i])

        selected = stations[selected_idx]
        st.session_state.current_url = selected['url_resolved']
        st.session_state.current_name = selected['name']

        st.markdown(f"<h2 style='text-align: center; font-size: 45px;'>🔊 Gra: <strong>{selected['name']}</strong></h2>", unsafe_allow_html=True)

        unique = f"<!-- {selected['name']} -->"
        st.components.v1.html(f"""
            {unique}
            <audio controls autoplay style="width:100%; height:120px;">
                <source src="{selected['url_resolved']}" type="audio/mpeg">
                Przeglądarka nie obsługuje radia.
            </audio>
        """, height=180)

        if st.button("⏹ ZATRZYMAJ RADIO", use_container_width=True):
            for key in ['current_url', 'current_name', 'query']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

with tab2:
    st.header("🛒 Gazetki Promocyjne – Aktualne (grudzień 2025)")
    st.markdown("<p style='text-align: center; font-size: 30px;'>Kliknij kafelek!</p>", unsafe_allow_html=True)

    promotions = [
        {"name": "Biedronka", "thumbnail": "https://gazetka-oferta.com/wp-content/uploads/2025/12/biedronka-17122025-2d6d4d.webp", "url": "https://www.biedronka.pl/gazetki"},
        {"name": "Lidl", "thumbnail": "https://lidl.gazetkapromocyjna.com.pl/storage/images/shops/content/image_68284e8a6599b.webp", "url": "https://www.lidl.pl/c/nasze-gazetki/s10008614"},
        {"name": "Kaufland", "thumbnail": "https://sklep.kaufland.pl/assets/img/kaufland-logo.svg", "url": "https://sklep.kaufland.pl/gazeta-reklamowa.html"},
        {"name": "Dino", "thumbnail": "https://gazetka-oferta.com/wp-content/uploads/2025/12/dino-01122025-cf82b3.webp", "url": "https://marketdino.pl/gazetki-promocyjne"},
        {"name": "Carrefour", "thumbnail": "https://carrefour.gazetkapromocyjna.com.pl/storage/images/hotspots/offer/693f984132c11.jpg", "url": "https://www.carrefour.pl/gazetka-handlowa"},
        {"name": "Leroy Merlin", "thumbnail": "https://media.adeo.com/media/4789065/media.jpeg?width=592&format=jpg", "url": "https://www.leroymerlin.pl/gazetka/"},
        {"name": "Bricomarché", "thumbnail": "https://bricomarche.gazetkapromocyjna.com.pl/storage/images/shops/content/image_68346d6aaff98.webp", "url": "https://www.bricomarche.pl/gazetka"},
        {"name": "Home&You", "thumbnail": "https://home-you.com/pl/img/logo.svg", "url": "https://home-you.com/pl/promocje"},
        {"name": "Westwing", "thumbnail": "https://www.westwing.pl/img/logo.svg", "url": "https://www.westwing.pl/campaign/current/"},
        {"name": "Empik", "thumbnail": "https://www.empik.com/static/img/empik-logo.svg", "url": "https://www.empik.com/promocje"},
        {"name": "Świat Książki", "thumbnail": "https://swiatksiazki.pl/img/logo.svg", "url": "https://swiatksiazki.pl/promocja-specjalna"},
    ]

    cols = st.columns(3)
    for idx, promo in enumerate(promotions):
        with cols[idx % 3]:
            st.markdown(f"""
                <div style="text-align: center; margin-bottom: 40px; border: 3px solid #eee; border-radius: 15px; padding: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                    <a href="{promo['url']}" target="_blank">
                        <img src="{promo['thumbnail']}" width="250" style="border-radius: 10px;">
                        <p style="margin: 15px 0 0; font-weight: bold; font-size: 30px;">{promo['name']}</p>
                    </a>
                </div>
            """, unsafe_allow_html=True)

st.sidebar.success("Apka gotowa – wszystko gra! ❤️")
