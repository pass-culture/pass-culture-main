from re import search as re_search
from typing import Optional


def get_cds_show_id_from_uuid(uuid: Optional[str]) -> str:
    """uuid pattern: "<movie.id>%<venue.siret>#<show.id>/<showtime>" return show_id"""
    if not uuid:
        return ""

    match = re_search(r"\#(.*?)\/", uuid)
    if match:
        return match.group(1)
    return ""
