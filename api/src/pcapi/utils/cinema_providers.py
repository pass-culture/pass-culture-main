from re import search as re_search


def get_cds_show_id_from_uuid(uuid: str | None) -> int | None:
    """
    Parses the uuid with this pattern: "<movie.id>%<venue.id>#<show.id>/<showtime>"
    and returns the show_id as int, or None if it cannot
    """
    if uuid:
        # TODO (dramelet, 2024-02-09): In a few months, we will be able to drop the name group `show_id_with_showtime`
        # as we won't have any up-to-date stocks with an old idAtProviders construct
        match = re_search(r"#(?P<show_id_with_showtime>\d*)/|#(?P<show_id_without_showtime>\d*)$", uuid)
        if match and match["show_id_with_showtime"]:
            return int(match["show_id_with_showtime"])
        if match and match["show_id_without_showtime"]:
            return int(match["show_id_without_showtime"])

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


def get_cgr_showtime_id_from_uuid(stock_uuid: str | None) -> int | None:
    """
    Parses the uuid with this pattern: uuid pattern: <allocine_movie_id>%<venue.id>%CGR#<showtime_id>
    and returns the show_id as int, or None if it cannot
    """
    if stock_uuid:
        match = re_search(r"#(.*?)$", stock_uuid)
        if match and match.group(1).isdigit():
            return int(match.group(1))
    return None


def get_ems_showtime_id_from_uuid(stock_uuid: str | None) -> int | None:
    """
    Parses the uuid with this pattern: <movie_id>%<venue.id>%EMS#<showtime.id>
    Return the show_id as int or None
    """
    if stock_uuid:
        match = re_search(r"#(?P<showtime_id>\d+)?", stock_uuid)
        if match and (showtime_id := match["showtime_id"]):
            return int(showtime_id)
    return None


def get_showtime_id_from_uuid(stock_uuid: str | None, provider_name: str | None) -> int | None:
    match provider_name:
        case "CDSStocks":
            return get_cds_show_id_from_uuid(stock_uuid)
        case "BoostStocks":
            return get_boost_showtime_id_from_uuid(stock_uuid)
        case "CGRStocks":
            return get_cgr_showtime_id_from_uuid(stock_uuid)
        case "EMSStocks":
            return get_ems_showtime_id_from_uuid(stock_uuid)
        case _:
            return None


def get_boost_or_cgr_or_ems_film_id_from_uuid(offer_uuid: str | None) -> str | None:
    """
    Parses the uuid with this pattern: uuid pattern: <film_id>%<venue.id>%<Boost|CGR|EMS>
    and returns the film_id as int, or None if it cannot
    """
    if offer_uuid:
        match = re_search(r"(.*?)%", offer_uuid)
        if match and match.group(1).isalnum():
            return match.group(1)
    return None
