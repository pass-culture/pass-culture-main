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
    allocine_products_provider = Provider.query.filter(
        Provider.name == providers_constants.ALLOCINE_PRODUCTS_PROVIDER_NAME
    ).one()
    with transaction():
        for movie in movies:
            _upsert_product(products_by_allocine_id, movie, allocine_products_provider)


def _upsert_product(
    products_by_allocine_id: dict[int, Product], movie: allocine_serializers.AllocineMovie, provider: Provider
) -> None:
    allocine_id = movie.internalId
    product = products_by_allocine_id.get(allocine_id)
    movie_data = _build_movie_data(movie)
    if not product:
        product = Product(
            description=movie.synopsis,
            extraData=movie_data,
            idAtProviders=str(allocine_id),
            lastProviderId=provider.id,
            name=movie.title,
            subcategoryId=SEANCE_CINE.id,
        )
    else:
        if product.extraData is None:
            product.extraData = OfferExtraData()
        product.extraData.update(movie_data)

    db.session.add(product)


def _build_movie_data(movie: allocine_serializers.AllocineMovie) -> OfferExtraData:
    return OfferExtraData(
        allocineId=movie.internalId,
        backlink=str(movie.backlink.url),
        cast=[f"{item.actor.firstName} {item.actor.lastName}" for item in movie.cast.items if item.actor],
        companies=[company.model_dump() for company in movie.companies],
        countries=[country.name for country in movie.countries],
        credits=[credit.model_dump() for credit in movie.credits],
        eidr=movie.data.eidr,
        genres=[genre.name for genre in movie.genres],
        originalTitle=movie.originalTitle,
        posterUrl=str(movie.poster.url) if movie.poster else None,
        productionYear=movie.data.productionYear,
        releases=[release.model_dump() for release in movie.releases],
        runtime=movie.runtime,
        synopsis=movie.synopsis,
        title=movie.title,
        type=movie.type,
    )
