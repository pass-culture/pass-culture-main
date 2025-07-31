import re

from pcapi.core.artist import models as artist_models


def sanitize_author_html(html: str | None) -> str | None:
    if not html:
        return None
    # If we have an href in the html, we want to keep the link
    if "<a href=" in html:
        author_url = re.search(r"href=\"([^\"]+)\"", html)
    else:
        author_url = None

    # The rest of the html is useless, we want to remove it

    html = re.sub(r"<[^>]*>", "", html)

    if author_url:
        html = f'<a href="{author_url.group(1)}">{html}</a>'

    return html


def get_artist_type(artist_type: str | None) -> artist_models.ArtistType | None:
    if not artist_type:
        return None
    try:
        return artist_models.ArtistType(artist_type)
    except ValueError:
        return None
