from contextlib import suppress
import logging
import typing

import pydantic

from pcapi import settings
from pcapi.connectors.serialization import allocine_serializers
from pcapi.utils import requests


class AllocineException(Exception):
    pass


logger = logging.getLogger(__name__)

ALLOCINE_API_URL = "https://graph-api-proxy.allocine.fr/api/query"


def _extract_allocine_id_from_allocine_movie_list(movie_list: dict, path: tuple[int | str, ...]) -> str | None:
    try:
        # If the validation error comes from a movie, the path should be
        # ["movieList", "edges", movie_index, ...]
        # Otherwise, there is no allocine id to retrieve.
        obj = movie_list
        for field in path[:3]:
            obj = obj[field]
        allocine_id = obj["node"]["internalId"]
    except (KeyError, IndexError):
        logger.exception("Error extracting allocine id from movie list")
        allocine_id = None

    return allocine_id


def get_movie_list_page(after: str = "") -> allocine_serializers.AllocineMovieListResponse:
    url = f"{ALLOCINE_API_URL}/movieList?after={after}"
    try:
        response = requests.get(url, headers={"Authorization": "Bearer " + settings.ALLOCINE_API_KEY})
    except Exception:
        raise AllocineException("Error connecting Allocine API to get movie list")

    if not response.ok:
        raise AllocineException(f"Error getting API Allocine data to get movie list, error={response.status_code}")

    try:
        validated_response = allocine_serializers.AllocineMovieListResponse.model_validate(response.json())
    except pydantic.ValidationError as exc:
        allocine_id = _extract_allocine_id_from_allocine_movie_list(response.json(), exc.errors()[0]["loc"])
        raise AllocineException(f"Error parsing Allocine response, error: {exc}. Allocine Id: {allocine_id}")

    return validated_response


def _filter_invalid_edge(json_data: dict, loc: int, theater_id: str) -> dict:
    invalid_edge = json_data["movieShowtimeList"]["edges"].pop(loc)

    logger.error(
        "One allocine show time edge removed (invalid)",
        extra={"theater": theater_id, "location": loc, "edge": invalid_edge},
    )

    return json_data


def _get_error_loc(err: typing.Mapping) -> int | None:
    with suppress(KeyError, IndexError, ValueError):
        return int(err["loc"][2])
    return None


def _has_valid_error_loc(err: typing.Mapping) -> bool:
    try:
        return bool(err["loc"] is not None and set(err["loc"][:2]) == {"movieShowtimeList", "edges"})
    except (KeyError, TypeError):
        return False


def parse_movie_showtimes(
    json_data: dict, theater_id: str, try_count: int = 0
) -> allocine_serializers.AllocineMovieShowtimeListResponse:
    try:
        return allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(json_data)
    except pydantic.ValidationError as exc:
        if try_count > 1:
            # try two times, in case some errors were hidden
            raise

        data = json_data

        # warning: the reversed sort is very import here. Without it, two (bad)
        # things could happen:
        #   1. IndexError because the json data has lost edges and the error
        #      location index is out of range or
        #   2. a valid showtime might be ignored (same problem as above but
        #      with not-out-of-bound index).
        # Starting from the highest index means that each other index is still
        # valid after the filter call: eg, indexes are 1, 3, 5; after the 5th
        # edge has been removed, the 3d will still be at the 3d index, same for
        # the first one. Which would not be the case without the reversed sort.
        filtered_locs = [_get_error_loc(err) for err in exc.errors() if _has_valid_error_loc(err)]
        locs = sorted([loc for loc in filtered_locs if loc is not None], reverse=True)

        for loc in locs:
            data = _filter_invalid_edge(data, loc, theater_id)

        return parse_movie_showtimes(data, theater_id, try_count + 1)


def get_movies_showtimes_from_allocine(theater_id: str) -> allocine_serializers.AllocineMovieShowtimeListResponse:
    url = f"{ALLOCINE_API_URL}/movieShowtimeList?theater={theater_id}"

    try:
        response = requests.get(url, headers={"Authorization": "Bearer " + settings.ALLOCINE_API_KEY})
    except Exception:
        raise AllocineException(f"Error connecting Allocine API for theater {theater_id}")

    if response.status_code != 200:
        raise AllocineException(f"Error getting API Allocine DATA for theater {theater_id}")

    try:
        validated_response = parse_movie_showtimes(response.json(), theater_id)
    except Exception as exc:
        raise AllocineException(f"Error validating Allocine response. Error: {str(exc)}")

    return validated_response


def get_movie_poster_from_allocine(poster_url: str) -> bytes:
    response = requests.get(poster_url)

    if response.status_code != 200:
        raise AllocineException(
            f"Error getting API Allocine movie poster {poster_url} with code {response.status_code}"
        )

    return response.content
