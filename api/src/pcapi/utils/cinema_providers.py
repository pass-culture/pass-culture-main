from re import search as re_search


def get_cds_show_id_from_uuid(uuid: str | None) -> int | None:
    """
    Parses the uuid with this pattern: "<movie.id>%<venue.siret>#<show.id>/<showtime>"
    and returns the show_id as int, or None if it cannot
    """
    if uuid:
        match = re_search(r"#(.*?)/", uuid)
        if match and match.group(1).isdigit():
            return int(match.group(1))
    return None


def get_boost_showtime_id_from_uuid(stock_uuid: str | None) -> int | None:
    """
    Parses the uuid with this pattern: uuid pattern: <film_id>%<venue.id>#<showtime_id>
    and returns the show_id as int, or None if it cannot
    """
    if stock_uuid:
        match = re_search(r"#(.*?)$", stock_uuid)
        if match and match.group(1).isdigit():
            return int(match.group(1))
    return None


def get_showtime_id_from_uuid(stock_uuid: str | None, provider_name: str) -> int | None:
    match provider_name:
        case "CDSStocks":
            return get_cds_show_id_from_uuid(stock_uuid)
        case "BoostStocks":
            return get_boost_showtime_id_from_uuid(stock_uuid)
        case _:
            return None


def get_boost_film_id_from_uuid(offer_uuid: str | None) -> int | None:
    """
    Parses the uuid with this pattern: uuid pattern: <film_id>%<venue.id>%Boost
    and returns the show_id as int, or None if it cannot
    """
    if offer_uuid:
        match = re_search(r"(.*?)%", offer_uuid)
        if match and match.group(1).isdigit():
            return int(match.group(1))
    return None
