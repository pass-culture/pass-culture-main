import logging
from typing import Iterator

from sqlalchemy import Integer

from pcapi.connectors import api_allocine
from pcapi.connectors.serialization import allocine_serializers
from pcapi.core.categories.subcategories_v2 import SEANCE_CINE
from pcapi.core.offers.models import OfferExtraData
from pcapi.core.offers.models import Product
from pcapi.core.providers import constants as providers_constants
from pcapi.core.providers.models import Provider
from pcapi.models import db
from pcapi.repository import transaction


logger = logging.getLogger(__name__)

MOVIE_SPECIAL_EVENT = "SPECIAL_EVENT"


def synchronize_products() -> None:
    movies = get_movie_list()
    allocine_ids = [movie.internalId for movie in movies]
    products_query = Product.query.filter(Product.extraData["allocineId"].cast(Integer).in_(allocine_ids))
    products_by_allocine_id = {product.extraData["allocineId"]: product for product in products_query}
    allocine_products_provider_id = _get_allocine_products_provider_id()
    with transaction():
        for movie in movies:
            _upsert_product(products_by_allocine_id, movie, allocine_products_provider_id)


def _upsert_product(
    products_by_allocine_id: dict[int, Product], movie: allocine_serializers.AllocineMovie, provider_id: int
) -> None:
    allocine_id = movie.internalId
    product = products_by_allocine_id.get(allocine_id)
    if not product:
        product = create_product(movie, provider_id)
    else:
        update_product(product, movie)

    db.session.add(product)


def create_product(movie: allocine_serializers.AllocineMovie, provider_id: int | None = None) -> Product:
    if not provider_id:
        provider_id = _get_allocine_products_provider_id()

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


def update_product(product: Product, movie: allocine_serializers.AllocineMovie) -> None:
    if product.extraData is None:
        product.extraData = OfferExtraData()

    movie_data = build_movie_data(movie)
    product.extraData.update(movie_data)


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


def _get_allocine_products_provider_id() -> int:
    return (
        Provider.query.filter(Provider.name == providers_constants.ALLOCINE_PRODUCTS_PROVIDER_NAME)
        .with_entities(Provider.id)
        .scalar()
    )


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
