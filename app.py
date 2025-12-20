import streamlit as st
from pyradios import RadioBrowser
import requests
import sqlite3  # Dodajemy prostą bazę danych SQLite do przechowywania ulubionych stacji (dla "starej bazy danych")

# Konfiguracja aplikacji – prosty, duży UI dla starszych osób na tablecie/telefonie
st.set_page_config(page_title="Proste Radio + Gazetki", layout="wide", initial_sidebar_state="collapsed")
st.markdown("<h1 style='text-align: center; font-size: 60px; color: #FF4500;'>🎵 Radio i Gazetki 🛒</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 40px; color: #333;'>Dotknij przycisku – gra od razu! 😊</p>", unsafe_allow_html=True)

# Zakładki – proste nawigacja
tab1, tab2 = st.tabs(["🎵 Radio", "🛒 Gazetki"])

# Inicjalizacja bazy danych SQLite (lokalna, prosta "stara baza" do ulubionych – zapisuje zmiany)
conn = sqlite3.connect('favorites.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS favorites (name TEXT PRIMARY KEY, url TEXT, emoji TEXT)''')
conn.commit()

# Fallbacki – podzielone na grupy dla stabilności (publiczne Polskie Radio często zmienia, komercyjne stabilniejsze)
fallback_public = [
    {"name": "Polskie Radio Jedynka", "urls": ["https://stream3.polskieradio.pl:8900/pr1_mp3", "http://stream1.polskieradio.pl:8900/;stream.mp3", "https://stream1.polskieradio.pl/pr1"], "emoji": "📰"},
    {"name": "Polskie Radio Dwójka", "urls": ["https://stream3.polskieradio.pl:8902/pr2_mp3", "http://stream1.polskieradio.pl:8902/;stream.mp3", "https://stream1.polskieradio.pl/pr2"], "emoji": "🎼"},
    {"name": "Polskie Radio Trójka", "urls": ["https://stream3.polskieradio.pl:8904/pr3_mp3", "http://stream1.polskieradio.pl:8904/;stream.mp3", "https://stream1.polskieradio.pl/pr3"], "emoji": "🎸"},
]

fallback_commercial = [
    {"name": "RMF FM", "urls": ["https://rs101-krk.rmfstream.pl/rmf_fm", "https://rs201-krk.rmfstream.pl/rmf_fm"], "emoji": "🔥"},
    {"name": "RMF Classic", "urls": ["https://rs201-krk.rmfstream.pl/rmf_classic", "https://rs101-krk.rmfstream.pl/rmf_classic"], "emoji": "🎻"},
    {"name": "Radio ZET", "urls": ["https://n-15-21.dcs.redcdn.pl/sc/o2/Eurozet/live/audio.livx", "https://n-15-21.dcs.redcdn.pl/sc/o2/Eurozet/live/radiozet.livx"], "emoji": "💥"},
    {"name": "VOX FM", "urls": ["https://ic2.smcdn.pl/3990-1.mp3", "https://stream.rcs.revma.com/ypen1wqcm0hvv"], "emoji": "🎉"},
    {"name": "Eska", "urls": ["https://stream.open.fm/1", "https://stream.open.fm/10"], "emoji": "🥳"},
    {"name": "Antyradio", "urls": ["https://n-15-21.dcs.redcdn.pl/sc/o2/Eurozet/live/antyradio.livx"], "emoji": "🤘"},
    {"name": "Złote Przeboje", "urls": ["https://stream.open.fm/74", "https://stream.open.fm/20"], "emoji": "🕺"},
]

all_fallbacks = fallback_public + fallback_commercial

# Funkcja do wyboru działającego URL (test HEAD)
def get_working_url(urls):
    for url in urls:
        try:
            if requests.head(url, timeout=3).status_code == 200:
                return url
        except:
            pass
    return None

# Ładujemy ulubione z bazy (jeśli pusta, dodajemy domyślne)
c.execute("SELECT COUNT(*) FROM favorites")
if c.fetchone()[0] == 0:
    for station in all_fallbacks:
        url = get_working_url(station['urls'])
        if url:
            c.execute("INSERT INTO favorites VALUES (?, ?, ?)", (station['name'], url, station['emoji']))
    conn.commit()

favorites = c.execute("SELECT * FROM favorites").fetchall()

with tab1:
    st.markdown("<h2 style='text-align: center; font-size: 50px;'>🇵🇱 Ulubione Stacje</h2>", unsafe_allow_html=True)
    
    # Duże przyciski w kolumnach (2 na wiersz dla tabletu/telefonu)
    cols = st.columns(2)
    for idx, (name, url, emoji) in enumerate(favorites):
        with cols[idx % 2]:
            is_active = st.session_state.get('current_name') == name
            button_style = "primary" if is_active else "secondary"
            if st.button(f"{emoji} {name}", key=f"fav_{idx}", use_container_width=True, type=button_style, help=f"Dotknij, by słuchać {name}!"):
                working_url = get_working_url([url]) or url  # Sprawdź czy nadal działa
                if working_url:
                    st.session_state.current_name = name
                    st.session_state.current_url = working_url
                    st.rerun()
                else:
                    st.error(f"Stream dla {name} nie działa. Spróbuj wyszukać nowy!")

    st.markdown("---")
    st.markdown("<h3 style='text-align: center; font-size: 40px;'>🔍 Szukaj Stacji</h3>", unsafe_allow_html=True)
    
    # Widoczny input z selectbox – prosty dla UX
    query = st.text_input("", placeholder="Wpisz np. RMF, ZET, Trójka... i wybierz poniżej", key="radio_search", label_visibility="collapsed", help="Wpisz nazwę – lista pojawi się automatycznie!")
    
    stations = []
    if query:
        try:
            rb = RadioBrowser()
            results = rb.search(name=query, country="Poland", limit=50, order="clickcount", reverse=True)
            stations = [r for r in results if r['url_resolved'].startswith('https://')]
            if stations:
                st.success("Znaleziono stacje! Wybierz z listy poniżej.")
        except:
            st.warning("Problem z API – używam lokalnych fallbacków.")
            stations = [s for s in all_fallbacks if query.lower() in s['name'].lower()]
            for s in stations:
                s['url_resolved'] = get_working_url(s['urls'])
                s['name'] = s['name']
                s['tags'] = 'lokalne'
                s['bitrate'] = 128
    
    if stations:
        station_names = [f"{s['name']} ({s.get('tags', 'brak')} | {s.get('bitrate', '?')} kbps)" for s in stations]
        selected_idx = st.selectbox("", range(len(station_names)), format_func=lambda i: station_names[i], label_visibility="collapsed", help="Dotknij stację – zacznie grać!")
        if selected_idx is not None:
            selected = stations[selected_idx]
            url = selected['url_resolved']
            name = selected['name']
            emoji = next((s['emoji'] for s in all_fallbacks if s['name'] == name), "🎵")  # Domyślny emoji
            # Dodaj do ulubionych jeśli nie ma
            c.execute("INSERT OR IGNORE INTO favorites VALUES (?, ?, ?)", (name, url, emoji))
            conn.commit()
            st.session_state.current_name = name
            st.session_state.current_url = url
            st.rerun()

    # Duży player centralny
    if 'current_url' in st.session_state and 'current_name' in st.session_state:
        st.markdown(f"<h2 style='text-align: center; font-size: 50px; color: #00FF00;'>🔊 Gra: {st.session_state.current_name}</h2>", unsafe_allow_html=True)
        st.components.v1.html(f"""
            <audio controls autoplay style="width:100%; height:150px; background-color: #f0f0f0; border-radius: 20px;">
                <source src="{st.session_state.current_url}" type="audio/mpeg">
                Brak obsługi audio.
            </audio>
        """, height=200)
        if st.button("⏹ Zatrzymaj", use_container_width=True, type="primary", help="Dotknij, by zatrzymać radio"):
            del st.session_state['current_url']
            del st.session_state['current_name']
            if 'radio_search' in st.session_state:
                del st.session_state['radio_search']
            st.rerun()
    else:
        st.info("Dotknij ulubionej lub wyszukaj – duże przyciski dla łatwości!", icon="ℹ️")

with tab2:
    st.markdown("<h2 style='text-align: center; font-size: 50px;'>🛒 Gazetki Promocyjne</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 40px;'>Dotknij kafelka – otwiera stronę!</p>", unsafe_allow_html=True)
    
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
                <div style="text-align: center; margin: 20px; padding: 20px; background-color: #fff; border-radius: 20px; box-shadow: 0 8px 20px rgba(0,0,0,0.15);">
                    <a href="{promo['url']}" target="_blank">
                        <img src="{promo['thumbnail']}" width="300" style="border-radius: 15px;">
                        <p style="margin-top: 20px; font-size: 40px; font-weight: bold; color: #333;">{promo['name']}</p>
                    </a>
                </div>
            """, unsafe_allow_html=True)

# Sidebar – proste info
st.sidebar.markdown("<h3 style='font-size: 30px;'>Appka dla Ciebie! ❤️</h3>", unsafe_allow_html=True)
st.sidebar.info("Duże przyciski, prosta obsługa. Ulubione zapisane w bazie – nie znikną!", icon="🚀")

# Zamknij połączenie z bazą na końcu
conn.close()
