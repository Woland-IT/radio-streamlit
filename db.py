import sqlite3
import hashlib
import streamlit as st


@st.cache_resource
def get_conn(db_path: str = 'favorites.db'):
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS favorites
                 (name TEXT PRIMARY KEY, url TEXT, tags TEXT, bitrate INTEGER)''')
    conn.commit()
    return conn


def _row_to_tuple(row):
    # return (name, url, tags, bitrate)
    return (row[1], row[2], row[3], row[4])


def get_favorites():
    c = get_conn().cursor()
    c.execute("SELECT * FROM favorites")
    rows = c.fetchall()
    print(f"DB: Pobrano {len(rows)} ulubionych z bazy")
    return [(r[0], r[1], r[2], r[3]) for r in rows]


def add_favorite(station: dict) -> bool:
    try:
        url = station.get('url_resolved') or station.get('url') or ''
        name = station.get('name')
        tags = station.get('tags', 'brak')
        bitrate = int(station.get('bitrate', 0) or 0)
        print(f"DB: Dodaję do bazy: name={name}, url={url}")
        c = get_conn().cursor()
        c.execute("INSERT OR REPLACE INTO favorites VALUES (?, ?, ?, ?)",
                  (name, url, tags, bitrate))
        get_conn().commit()
        print(f"DB: Dodano pomyślnie, commit wykonany")
        return True
    except sqlite3.Error as e:
        print(f"DB ERROR: {e}")
        return False


def remove_favorite(name: str):
    c = get_conn().cursor()
    c.execute("DELETE FROM favorites WHERE name=?", (name,))
    get_conn().commit()
