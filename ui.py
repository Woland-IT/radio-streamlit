from components.tiles import render_station_tile, render_promo_tile

def clickable_tile_html(name: str, color: str, tags: str, bitrate, url: str, station: dict, idx: int):
    # backward-compatible wrapper that renders via components
    return render_station_tile(name, color, tags, bitrate, url, station, idx)


def promotion_tile_html(promo: dict):
    return render_promo_tile(promo)
