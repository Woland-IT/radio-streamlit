import streamlit as st
from pyradios import RadioBrowser
import requests  # Na ewentualne future poprawki

# Konfiguracja
st.set_page_config(page_title="Proste Radio + Gazetki", layout="wide")
st.markdown("<h1 style='text-align: center; font-size: 50px;'>🎵 Proste Radio i Gazetki 🛒</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 30px;'>Kliknij przycisk – gra od razu! 😊</p>", unsafe_allow_html=True)

# Zakładki
tab1, tab2 = st.tabs(["🎵 Radio Online", "🛒 Gazetki Promocyjne"])

# Fallbacki – dwie grupy: publiczne (Polskie Radio – często zmieniają streamy) i komercyjne (stabilniejsze)
fallback_public = [
    {"name": "Polskie Radio Jedynka", "urls": ["https://stream3.polskieradio.pl:8900/pr1_mp3", "http://mp3.polskieradio.pl:8900/;stream.mp3", "https://stream1.polskieradio.pl/pr1"]},
    {"name": "Polskie Radio Dwójka", "urls": ["https://stream3.polskieradio.pl:8902/pr2_mp3", "http://mp3.polskieradio.pl:8902/;stream.mp3", "https://stream1.polskieradio.pl/pr2"]},
    {"name": "Polskie Radio Trójka", "urls": ["https://stream3.polskieradio.pl:8904/pr3_mp3", "http://mp3.polskieradio.pl:8904/;stream.mp3", "https://stream1.polskieradio.pl/pr3"]},
]

fallback_commercial = [
    {"name": "RMF FM", "urls": ["https://rs101-krk.rmfstream.pl/rmf_fm", "https://rs201-krk.rmfstream.pl/rmf_fm"]},
    {"name": "RMF Classic", "urls": ["https://rs201-krk.rmfstream.pl/rmf_classic", "https://rs101-krk.rmfstream.pl/rmf_classic"]},
    {"name": "Radio ZET", "urls": ["https://n-15-21.dcs.redcdn.pl/sc/o2/Eurozet/live/audio.livx", "https://n-15-21.dcs.redcdn.pl/sc/o2/Eurozet/live/radiozet.livx"]},
    {"name": "VOX FM", "urls": ["https://ic2.smcdn.pl/3990-1.mp3", "https://stream.rcs.revma.com/ypen1wqcm0hvv"]},
    {"name": "Eska", "urls": ["https://stream.open.fm/1", "https://stream.open.fm/10"]},
    {"name": "Antyradio", "urls": ["https://n-15-21.dcs.redcdn.pl/sc/o2/Eurozet/live/antyradio.livx", "https://n-15-21.dcs.redcdn.pl/sc/o2/Eurozet/live/antyradio.livx"]},
    {"name": "Złote Przeboje", "urls": ["https://stream.open.fm/74", "https://stream.open.fm/20"]},
]

# Funkcja do wyboru działającego URL (testuje HEAD request)
def get_working_url(urls):
    for url in urls:
        try:
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                return url
        except:
            continue
    return None  # Jeśli żaden nie działa

with tab1:
    st.header("🇵🇱 Ulubione stacje – kliknij przycisk (duże dla tabletu/telefonu)")
    favorites = [
        {"name": "RMF Classic", "emoji": "🎻", "type": "commercial"},
        {"name": "Złote Przeboje", "emoji": "🕺", "type": "commercial"},
        {"name": "Polskie Radio Trójka", "emoji": "🎸", "type": "public"},
        {"name": "Polskie Radio Dwójka", "emoji": "🎼", "type": "public"},
        {"name": "Polskie Radio Jedynka", "emoji": "📰", "type": "public"},
        {"name": "RMF FM", "emoji": "🔥", "type": "commercial"},
        {"name": "Radio ZET", "emoji": "💥", "type": "commercial"},
        {"name": "VOX FM", "emoji": "🎉", "type": "commercial"},
        {"name": "Eska", "emoji": "🥳", "type": "commercial"},
        {"name": "Antyradio", "emoji": "🤘", "type": "commercial"},
    ]
    
    cols = st.columns(2)  # Dwa kolumny dla dużych przycisków
    for idx, station in enumerate(favorites):
        with cols[idx % 2]:
            is_active = st.session_state.get('current_name') == station['name']
            if st.button(
                f"{station['emoji']} {station['name']}",
                key=f"fav_{idx}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
                help=f"Słuchaj {station['name']} od razu!"
            ):
                # Wybierz fallback w zależności od typu
                fallbacks = fallback_public if station['type'] == "public" else fallback_commercial
                fallback_station = next((s for s in fallbacks if s['name'] == station['name']), None)
                url = get_working_url(fallback_station['urls']) if fallback_station else None
                if url:
                    st.session_state.current_name = station['name']
                    st.session_state.current_url = url
                    st.rerun()
                else:
                    st.error(f"Brak działającego streamu dla {station['name']}. Spróbuj wyszukać!")

    st.markdown("---")
    st.markdown("<h3 style='text-align: center; font-size: 32px;'>🔍 Wyszukaj stację (widoczny input z listą)</h3>", unsafe_allow_html=True)
    
    query = st.text_input("Szukaj stacji (np. RMF, ZET, Trójka):", key="radio_search", placeholder="Wpisz nazwę i wybierz z listy poniżej...", help="Wpisz i wybierz stację – proste dla starszych osób!")
    
    stations = None
    if query:
        mirror_list = ["https://de1.api.radio-browser.info", "https://de2.api.radio-browser.info"]
        for mirror in mirror_list:
            try:
                rb = RadioBrowser(base_url=mirror)
                results = rb.search(name=query, country="Poland", limit=30, order="clickcount", reverse=True)
                stations = [r for r in results if r['url_resolved'].startswith('https://')]  # Tylko HTTPS dla bezpieczeństwa
                if stations:
                    st.success("Znaleziono stacje z API! Wybierz z listy.")
                    break
            except Exception as e:
                st.warning(f"Problem z API: {str(e)}. Używam fallbacków.")
                # Fallback search w lokalnych listach
                all_fallbacks = fallback_public + fallback_commercial
                stations = [s for s in all_fallbacks if query.lower() in s['name'].lower()]
                for s in stations:
                    s['url_resolved'] = get_working_url(s['urls'])
                    s['tags'] = 'fallback'
                    s['bitrate'] = 128
    else:
        stations = []  # Pusta lista jeśli brak query

    if stations:
        station_names = [f"{s['name']} ({s.get('tags', 'brak')} | {s.get('bitrate', '?')} kbps)" for s in stations]
        selected_idx = st.selectbox("Wybierz stację z listy:", range(len(station_names)), format_func=lambda i: station_names[i], help="Duża lista do wyboru – dotknij i gra!")
        
        if selected_idx is not None:
            selected = stations[selected_idx]
            url = selected['url_resolved']
            if url:
                st.session_state.current_name = selected['name']
                st.session_state.current_url = url
                st.rerun()

    # Player – duży i centralny
    selected_url = st.session_state.get('current_url')
    current_name = st.session_state.get('current_name')
    if selected_url and current_name:
        st.markdown(f"<h2 style='text-align: center; font-size: 45px;'>🔊 Gra: <strong>{current_name}</strong></h2>", unsafe_allow_html=True)
        unique = f"<!-- PLAYING: {current_name} -->"
        st.components.v1.html(f"""
            {unique}
            <audio controls autoplay style="width:100%; height:120px;">
                <source src="{selected_url}" type="audio/mpeg">
                Przeglądarka nie obsługuje radia.
            </audio>
        """, height=180)
        if st.button("⏹ ZATRZYMAJ RADIO", use_container_width=True, type="primary"):
            for key in ['current_url', 'current_name', 'radio_search']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    else:
        st.info("Kliknij ulubioną lub wyszukaj – radio zacznie grać od razu! Duże przyciski dla łatwości.")

# Zakładka Gazetki – bez zmian, ale z większymi fontami dla UX
with tab2:
    st.header("🛒 Gazetki Promocyjne – grudzień 2025")
    st.markdown("<p style='text-align: center; font-size: 30px;'>Kliknij kafelek – otwiera stronę!</p>", unsafe_allow_html=True)
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
                <div style="text-align: center; margin-bottom: 30px;">
                    <a href="{promo['url']}" target="_blank">
                        <img src="{promo['thumbnail']}" width="220" style="border-radius: 15px; box-shadow: 0 6px 15px rgba(0,0,0,0.2);">
                        <p style="margin: 15px 0 0; font-weight: bold; font-size: 30px;">{promo['name']}</p>
                    </a>
                </div>
            """, unsafe_allow_html=True)

st.sidebar.success("Appka dla starszych – duże przyciski, proste wyszukiwanie! 🚀❤️")
