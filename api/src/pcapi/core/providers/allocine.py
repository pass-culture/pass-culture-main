import logging
from typing import Iterator

from pcapi.connectors import api_allocine
from pcapi.connectors.serialization import allocine_serializers
from pcapi.core.offers.models import Movie
from pcapi.core.offers.models import OfferExtraData
from pcapi.core.providers import constants as providers_constants
from pcapi.core.providers.models import Provider
from pcapi.repository import transaction


logger = logging.getLogger(__name__)

MOVIE_SPECIAL_EVENT = "SPECIAL_EVENT"


def synchronize_products() -> None:
    from pcapi.core.offers.api import upsert_movie_product_from_provider

    movies = get_movie_list()
    allocine_products_provider = get_allocine_products_provider()
    with transaction():
        for movie in movies:
            id_at_providers = build_movie_id_at_providers(allocine_products_provider.id, movie.internalId)
            generic_movie = create_generic_movie(movie)
            upsert_movie_product_from_provider(generic_movie, allocine_products_provider, id_at_providers)


def create_generic_movie(movie: allocine_serializers.AllocineMovie) -> Movie:
    movie_data = build_movie_data(movie)
    return Movie(
        allocine_id=str(movie.internalId),
        description=build_description(movie),
        duration=movie.runtime,
        extra_data=movie_data,
        poster_url=movie_data["posterUrl"],
        title=movie.title,
        visa=movie_data["visa"],
    )


def create_product(movie: allocine_serializers.AllocineMovie, provider_id: int | None = None) -> Product:
    if not provider_id:
        provider_id = get_allocine_products_provider_id()

    allocine_id = movie.internalId
    movie_data = build_movie_data(movie)
    id_at_providers = build_movie_id_at_providers(provider_id, allocine_id)
    product = Product(
        description=build_description(movie),
        durationMinutes=movie.runtime,
        extraData=movie_data,
        idAtProviders=id_at_providers,
        lastProviderId=provider_id,
        name=movie.title,
        subcategoryId=SEANCE_CINE.id,
    )
    return product


def get_movie_list() -> list[allocine_serializers.AllocineMovie]:
    movie_list = []
    has_next_page = True
    end_cursor = ""
    while has_next_page:
        try:
            response = api_allocine.get_movie_list_page(end_cursor)
        except api_allocine.AllocineException as exc:
            logger.exception("Could not get movies page at cursor '%s'. Error: '%s'", end_cursor, exc)
            break

        movie_list += response.movieList.movies
        end_cursor = response.movieList.pageInfo.endCursor
        has_next_page = response.movieList.pageInfo.hasNextPage

    return movie_list


def get_movies_showtimes(theater_id: str) -> Iterator[allocine_serializers.AllocineMovieShowtime]:
    try:
        movie_showtime_list_response = api_allocine.get_movies_showtimes_from_allocine(theater_id)
    except api_allocine.AllocineException as exc:
        logger.error("Could not get movies showtimes for theater %s. Error: '%s'", theater_id, str(exc))
        return iter([])

    movie_showtime_list = movie_showtime_list_response.movieShowtimeList
    movies_number = movie_showtime_list.totalCount
    filtered_movies_showtimes = _exclude_empty_movies_and_special_events(movie_showtime_list.moviesShowtimes)

    logger.info("[ALLOCINE] Total : %s movies", movies_number)

    return iter(filtered_movies_showtimes)


def get_movie_poster(poster_url: str) -> bytes:
    try:
        return api_allocine.get_movie_poster_from_allocine(poster_url)
    except api_allocine.AllocineException:
        logger.info(
            "Could not fetch movie poster",
            extra={
                "provider": "allociné",
                "url": poster_url,
            },
        )
        return bytes()


def _exclude_empty_movies_and_special_events(
    movies_showtimes: list[allocine_serializers.AllocineMovieShowtime],
) -> list[allocine_serializers.AllocineMovieShowtime]:
    return [
        movie_showtimes
        for movie_showtimes in movies_showtimes
        if movie_showtimes.movie and movie_showtimes.movie.type != MOVIE_SPECIAL_EVENT
    ]


def get_allocine_products_provider() -> Provider:
    return Provider.query.filter(Provider.name == providers_constants.ALLOCINE_PRODUCTS_PROVIDER_NAME).one()


def build_movie_data(movie: allocine_serializers.AllocineMovie) -> OfferExtraData:
    return OfferExtraData(
        allocineId=movie.internalId,
        backlink=str(movie.backlink.url),
        cast=[build_full_name(item.actor) for item in movie.cast.items if item.actor],
        companies=[company.model_dump() for company in movie.companies],
        countries=[country.name for country in movie.countries],
        credits=[credit.model_dump() for credit in movie.credits],
        eidr=movie.data.eidr,
        genres=[genre.name for genre in movie.genres],
        originalTitle=movie.originalTitle,
        posterUrl=str(movie.poster.url) if movie.poster else None,
        productionYear=movie.data.productionYear,
        releaseDate=get_most_recent_release_date(movie.releases),
        runtime=movie.runtime,
        stageDirector=build_full_name(movie.credits[0].person) if movie.credits else None,
        synopsis=movie.synopsis,
        title=movie.title,
        type=movie.type,
        visa=movie.releases[0].data.visa_number if movie.releases else None,
    )


def build_movie_id_at_providers(provider_id: int, allocine_id: int) -> str:
    return f"{provider_id}:{allocine_id}"


def get_most_recent_release_date(releases: list[allocine_serializers.AllocineMovieRelease]) -> str | None:
    sorted_releases = sorted(
        [release.releaseDate.date.isoformat() for release in releases if release.releaseDate], reverse=True
    )
    return sorted_releases[0] if sorted_releases else None


def build_description(movie: allocine_serializers.AllocineMovie) -> str:
    return f"{movie.synopsis}\n{movie.backlink.label}: {movie.backlink.url}"


def build_full_name(person: allocine_serializers.AllocineMoviePerson) -> str:
    return f"{person.firstName or ''} {person.lastName or ''}".strip()
