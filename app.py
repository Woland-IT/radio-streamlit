import streamlit as st
from pyradios import RadioBrowser
import sqlite3

# Konfiguracja
st.set_page_config(page_title="Radio + Gazetki dla Seniorów", layout="wide")

# Inicjalizacja bazy danych dla ulubionych stacji
conn = sqlite3.connect('favorites.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS favorites
             (name TEXT PRIMARY KEY, url TEXT, tags TEXT, bitrate INTEGER)''')
conn.commit()

def get_favorites():
    c.execute("SELECT * FROM favorites")
    return c.fetchall()

def add_favorite(station):
    try:
        c.execute("INSERT OR REPLACE INTO favorites VALUES (?, ?, ?, ?)",
                  (station['name'], station['url_resolved'], station.get('tags', 'brak'), station.get('bitrate', 0)))
        conn.commit()
        return True
    except:
        return False

def remove_favorite(name):
    c.execute("DELETE FROM favorites WHERE name=?", (name,))
    conn.commit()

# Zakładki
tab1, tab2 = st.tabs(["🎵 Radio Online", "🛒 Gazetki Promocyjne"])

# Fallback – statyczna lista popularnych polskich stacji
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
    st.header("🇵🇱 Polskie Radio Online – Proste i Przyjazne")
    st.markdown("Wybierz z ulubionych lub wyszukaj nową stację. Dodaj do ulubionych, by szybko wracać!")

    # Sekcja Ulubione – NAPRAWIONA
    st.subheader("❤️ Moje Ulubione Stacje")
    favorites = get_favorites()
    
    if favorites:
        # Bezpieczne rozpakowanie – na wypadek starych rekordów z mniejszą liczbą pól
        favorite_display = []
        favorite_dicts = []
        
        for row in favorites:
            # row może mieć 3 lub 4 elementy (stare rekordy miały tylko name, url, tags)
            name = row[0]
            url = row[1]
            tags = row[2] if len(row) > 2 else "brak"
            bitrate = row[3] if len(row) > 3 else 128  # domyślna wartość
            favorite_display.append(f"{name} ({tags} | {bitrate} kbps)")
            favorite_dicts.append({"name": name, "url_resolved": url, "tags": tags, "bitrate": bitrate})
        
        selected_fav_idx = st.selectbox(
            "Wybierz ulubioną stację:",
            range(len(favorite_display)),
            format_func=lambda i: favorite_display[i],
            key="fav_select"
        )
        
        selected_fav = favorite_dicts[selected_fav_idx]
        url = selected_fav["url_resolved"]
        
        st.markdown(f"### 🎶 Słuchasz: **{selected_fav['name']}**")
        st.markdown(f"Tagi: {selected_fav['tags']} • Bitrate: {selected_fav['bitrate']} kbps")
        
        # Odtwarzacz audio – prosty, działa na wszystkich urządzeniach
        st.audio(url, format="audio/mpeg", start_time=0)
        
        # Opcjonalnie: duży, wyraźny komunikat dla seniora
        st.markdown("### 🔊 Odtwarzanie trwa... Jeśli nie słychać, naciśnij przycisk play powyżej 🔊")
        
        if st.button("Usuń z ulubionych", key=f"remove_{selected_fav['name']}"):
            remove_favorite(selected_fav['name'])
            st.success("Usunięto z ulubionych!")
            st.experimental_rerun()
    else:
        st.info("Brak ulubionych stacji. Znajdź stację poniżej i dodaj do ulubionych ❤️")


with tab2:
    st.header("🛒 Gazetki Promocyjne – Łatwy Dostęp")
    st.markdown("Kliknij na logo sklepu, by zobaczyć aktualne promocje!")

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

st.sidebar.success("Aplikacja dla seniorów – prosta i zawsze działa! 🚀")
