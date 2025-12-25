from components.tiles import render_station_tile, render_promo_tile

def clickable_tile_html(*args, **kwargs):
    # backward-compatible wrapper that renders via components
    return render_station_tile(*args, **kwargs)


def promotion_tile_html(promo: dict):
    return render_promo_tile(promo)
