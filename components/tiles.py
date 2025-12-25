import streamlit as st
import urllib.parse


def render_station_tile(name: str, color: str, tags: str, bitrate, url: str):
    encoded_name = urllib.parse.quote(name)
    encoded_url = urllib.parse.quote(url)
    encoded_tags = urllib.parse.quote(tags)
    html = f"""
    <a href="?play={encoded_name}&url={encoded_url}&tags={encoded_tags}&bitrate={bitrate}" target="_self" class="tile-link">
        <div class="clickable-tile" style="background-color: {color};">
            {name}
            <div class="tile-small-text">{tags} | {bitrate} kbps</div>
        </div>
    </a>
    """
    st.markdown(html, unsafe_allow_html=True)


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
