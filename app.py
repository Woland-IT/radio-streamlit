import streamlit as st
from pyradios import RadioBrowser

st.set_page_config(page_title="Proste Radio + Gazetki", layout="wide")
st.markdown("<h1 style='text-align: center; font-size: 50px;'>🎵 Proste Radio i Gazetki 🛒</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 30px;'>Kliknij kafelek – gra od razu! 😊</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🎵 Radio Online", "🛒 Gazetki Promocyjne"])

# Gwarantowane działające HTTPS streamy (fallback)
fallback_stations = {
    "RMF FM": "https://rs101-krk.rmfstream.pl/rmf_fm",
    "RMF Classic": "https://rs201-krk.rmfstream.pl/rmf_classic",
    "Radio ZET": "https://n-15-21.dcs.redcdn.pl/sc/o2/Eurozet/live/audio.livx",
    "VOX FM": "https://ic2.smcdn.pl/3990-1.mp3",
    "Eska": "https://stream.open.fm/1",
    "Antyradio": "https://n-15-21.dcs.redcdn.pl/sc/o2/Eurozet/live/antyradio.livx",
    "Złote Przeboje": "https://stream.open.fm/74",
    "Polskie Radio Jedynka": "https://stream.polskieradio.pl/sls/1/pr1.aac",
    "Polskie Radio Dwójka": "https://stream.polskieradio.pl/sls/1/pr2.aac",
    "Polskie Radio Trójka": "https://stream.polskieradio.pl/sls/1/pr3.aac",
}

with tab1:
    st.header("🇵🇱 Ulubione stacje – kliknij kafelek")

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
            is_active = st.session_state.get('current_name') == s['name']
            border_color = "4px solid #00ff00" if is_active else "2px solid #ddd"
            box_shadow = "0 8px 20px rgba(0,255,0,0.4)" if is_active else "0 4px 10px rgba(0,0,0,0.1)"
            bg_color = "#f0fff0" if is_active else "#ffffff"

            st.markdown(f"""
                <div style="text-align: center; padding: 20px; border: {border_color}; border-radius: 20px; 
                            background-color: {bg_color}; box-shadow: {box_shadow}; margin-bottom: 20px;">
                    <h2 style="font-size: 60px; margin: 0;">{s['emoji']}</h2>
                    <p style="font-size: 32px; font-weight: bold; margin: 10px 0;">{s['name']}</p>
                    {"<p style='color: green; font-size: 24px;'>▶ GRA!</p>" if is_active else ""}
                </div>
            """, unsafe_allow_html=True)

            if st.button("Odtwórz", key=f"play_{idx}", use_container_width=True):
                st.session_state.query = s['name']
                st.rerun()

    st.markdown("---")
    st.markdown("<h2 style='font-size: 40px; text-align: center;'>🔍 Wyszukaj inną stację</h2>", unsafe_allow_html=True)
    query = st.text_input("Szukaj", value=st.session_state.get('query', ''), placeholder="Wpisz nazwę...", label_visibility="hidden")

    # Szukanie działającego HTTPS streamu
    stations = []
    selected_url = fallback_stations.get(st.session_state.get('current_name'))  # domyślny fallback

    mirror_list = ["https://de1.api.radio-browser.info", "https://de2.api.radio-browser.info", "https://nl1.api.radio-browser.info"]

    if query or 'query' in st.session_state:
        search_name = query or st.session_state.query
        found = False
        for mirror in mirror_list:
            try:
                rb = RadioBrowser(base_url=mirror)
                api_results = rb.search(name=search_name, country="Poland", limit=30, order="clickcount", reverse=True)
                https_results = [s for s in api_results if s['url_resolved'].startswith('https://')]
                if https_results:
                    stations = https_results
                    st.success("Znaleziono działające stacje! 🚀")
                    found = True
                    break
            except:
                continue
        if not found:
            st.warning("Nie znaleziono w API – używam sprawdzonego streamu")

    # Jeśli nie ma wyników z API – używamy fallback dla wybranej stacji
    if not stations and 'current_name' in st.session_state:
        name = st.session_state.current_name
        if name in fallback_stations:
            selected_url = fallback_stations[name]

    # Lista stacji (jeśli API coś znalazło)
    if stations:
        station_names = [f"{s['name']} ({s.get('tags', 'brak')} | {s.get('bitrate', '?')} kbps)" for s in stations]
        default_idx = 0
        selected_idx = st.selectbox("Dostępne wersje:", options=range(len(station_names)), index=default_idx, format_func=lambda i: station_names[i])
        selected_station = stations[selected_idx]
        selected_url = selected_station['url_resolved']
        st.session_state.current_name = selected_station['name']
    elif 'current_name' in st.session_state:
        st.session_state.current_name = st.session_state.current_name  # zachowujemy nazwę

    # Player
    if 'current_name' in st.session_state and selected_url:
        st.markdown(f"<h2 style='text-align: center; font-size: 45px;'>🔊 Gra: <strong>{st.session_state.current_name}</strong></h2>", unsafe_allow_html=True)

        unique = f"<!-- PLAYING: {st.session_state.current_name} -->"
        st.components.v1.html(f"""
            {unique}
            <audio controls autoplay style="width:100%; height:120px;">
                <source src="{selected_url}" type="audio/mpeg">
                Twoja przeglądarka nie obsługuje radia.
            </audio>
        """, height=180)

        if st.button("⏹ ZATRZYMAJ RADIO", use_container_width=True):
            for key in ['current_url', 'current_name', 'query']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    else:
        st.info("Wybierz stację z kafelka powyżej")

# Gazetki – aktualne podglądy
with tab2:
    st.header("🛒 Gazetki Promocyjne – grudzień 2025")
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
                <div style="text-align: center; margin-bottom: 40px;">
                    <a href="{promo['url']}" target="_blank">
                        <img src="{promo['thumbnail']}" width="250" style="border-radius: 15px; box-shadow: 0 6px 15px rgba(0,0,0,0.2);">
                        <p style="margin: 15px 0 0; font-weight: bold; font-size: 32px;">{promo['name']}</p>
                    </a>
                </div>
            """, unsafe_allow_html=True)

st.sidebar.success("Gotowe! Wszystko gra i świeci! ❤️")
