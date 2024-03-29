from sqlalchemy import Integer

from pcapi.connectors.serialization import allocine_serializers
from pcapi.core.categories.subcategories_v2 import SEANCE_CINE
from pcapi.core.offers.models import OfferExtraData
from pcapi.core.offers.models import Product
from pcapi.core.providers import constants as providers_constants
from pcapi.core.providers.models import Provider
from pcapi.domain import allocine as allocine_domain
from pcapi.models import db
from pcapi.repository import transaction


def synchronize_products() -> None:
    movies = allocine_domain.get_movie_list()
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
    movie_data = _build_movie_data(movie)
    id_at_providers = _build_movie_id_at_providers(provider_id, allocine_id)
    product = Product(
        description=_build_description(movie),
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

    movie_data = _build_movie_data(movie)
    product.extraData.update(movie_data)


def _get_allocine_products_provider_id() -> int:
    return (
        Provider.query.filter(Provider.name == providers_constants.ALLOCINE_PRODUCTS_PROVIDER_NAME)
        .with_entities(Provider.id)
        .scalar()
    )


def _build_movie_data(movie: allocine_serializers.AllocineMovie) -> OfferExtraData:
    return OfferExtraData(
        allocineId=movie.internalId,
        backlink=str(movie.backlink.url),
        cast=[_build_full_name(item.actor) for item in movie.cast.items if item.actor],
        companies=[company.model_dump() for company in movie.companies],
        countries=[country.name for country in movie.countries],
        credits=[credit.model_dump() for credit in movie.credits],
        eidr=movie.data.eidr,
        genres=[genre.name for genre in movie.genres],
        originalTitle=movie.originalTitle,
        posterUrl=str(movie.poster.url) if movie.poster else None,
        productionYear=movie.data.productionYear,
        releaseDate=_get_most_recent_release_date(movie.releases),
        runtime=movie.runtime,
        stageDirector=_build_full_name(movie.credits[0].person) if movie.credits else None,
        synopsis=movie.synopsis,
        title=movie.title,
        type=movie.type,
        visa=movie.releases[0].data.visa_number if movie.releases else None,
    )


def _build_movie_id_at_providers(provider_id: int, allocine_id: int) -> str:
    return f"{provider_id}:{allocine_id}"


def _get_most_recent_release_date(releases: list[allocine_serializers.AllocineMovieRelease]) -> str | None:
    sorted_releases = sorted(
        [release.releaseDate.date.isoformat() for release in releases if release.releaseDate], reverse=True
    )
    return sorted_releases[0] if sorted_releases else None


def _build_description(movie: allocine_serializers.AllocineMovie) -> str:
    return f"{movie.synopsis}\n{movie.backlink.label}: {movie.backlink.url}"


def _build_full_name(person: allocine_serializers.AllocineMoviePerson) -> str:
    return f"{person.firstName or ''} {person.lastName or ''}".strip()
