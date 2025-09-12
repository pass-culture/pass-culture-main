import datetime
import difflib
import logging

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

import pcapi.core.providers.models as providers_models
from pcapi.connectors.titelive import get_new_product_from_ean13
from pcapi.core import search
from pcapi.core.categories import subcategories
from pcapi.core.chronicles import models as chronicles_models
from pcapi.core.offers import models as offers_models
from pcapi.core.products import models as products_models
from pcapi.core.products import repository as products_repository
from pcapi.core.providers.allocine import get_allocine_products_provider
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.reactions import models as reactions_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.utils.repository import transaction

from . import exceptions
from . import models


logger = logging.getLogger(__name__)


def whitelist_product(idAtProviders: str) -> products_models.Product:
    titelive_product = get_new_product_from_ean13(idAtProviders)

    product = fetch_or_update_product_with_titelive_data(titelive_product)

    product.gcuCompatibilityType = models.GcuCompatibilityType.COMPATIBLE

    db.session.add(product)
    db.session.flush()
    return product


def fetch_or_update_product_with_titelive_data(titelive_product: products_models.Product) -> products_models.Product:
    product = db.session.query(products_models.Product).filter_by(ean=titelive_product.ean).one_or_none()
    if not product:
        return titelive_product

    product.name = titelive_product.name
    product.description = titelive_product.description
    product.subcategoryId = titelive_product.subcategoryId
    product.thumbCount = titelive_product.thumbCount
    old_extra_data = product.extraData
    if old_extra_data is None:
        old_extra_data = {}

    if titelive_product.extraData:
        product.extraData = {**old_extra_data, **titelive_product.extraData}
        product.extraData.pop("ean", None)

    return product


def _str_are_similar(str_1: str, str_2: str) -> bool:
    return (str_1 in str_2) or (str_2 in str_1) or (difflib.SequenceMatcher(None, str_1, str_2).ratio() >= 0.6)


def _should_merge_product(
    product_with_allocine_id: products_models.Product,
    product_with_visa: products_models.Product,
) -> bool:
    """
    Check that the 2 products are actually similar.

    Similarity checks are performed on their names, and, if defined, on their descriptions.
    """
    allocine_name = product_with_allocine_id.name.lower()
    visa_name = product_with_visa.name.lower()

    names_are_similar = _str_are_similar(visa_name, allocine_name)

    descriptions_are_similar = None
    if product_with_visa.description and product_with_allocine_id.description:
        allocine_description = product_with_allocine_id.description.lower()
        visa_description = product_with_visa.description.lower()

        descriptions_are_similar = _str_are_similar(visa_description, allocine_description)

    if descriptions_are_similar is not None:
        return names_are_similar and descriptions_are_similar

    return names_are_similar


def _select_matching_product(
    movie: products_models.Movie,
    product_with_allocine_id: products_models.Product,
    product_with_visa: products_models.Product,
) -> products_models.Product:
    """
    Return the most coherent product based on two comparisons :
        - on the movie title
        - on the movie description (if defined)
    """
    movie_name = movie.title.lower()
    allocine_name = product_with_allocine_id.name.lower()
    visa_name = product_with_visa.name.lower()

    similarity_ratio_to_allocine_product = difflib.SequenceMatcher(None, movie_name, allocine_name).ratio()
    similarity_ratio_to_visa_product = difflib.SequenceMatcher(None, movie_name, visa_name).ratio()

    if movie.description:
        movie_description = movie.description.lower()
        allocine_description = (product_with_allocine_id.description or "").lower()
        visa_description = (product_with_visa.description or "").lower()
        similarity_ratio_to_allocine_product = (
            similarity_ratio_to_allocine_product
            + difflib.SequenceMatcher(None, movie_description, allocine_description).ratio()
        ) / 2
        similarity_ratio_to_visa_product = (
            similarity_ratio_to_visa_product
            + difflib.SequenceMatcher(None, movie_description, visa_description).ratio()
        ) / 2

    if similarity_ratio_to_allocine_product < similarity_ratio_to_visa_product:
        return product_with_visa

    return product_with_allocine_id


def upsert_movie_product_from_provider(
    movie: products_models.Movie, provider: providers_models.Provider, id_at_providers: str
) -> products_models.Product | None:
    if not movie.allocine_id and not movie.visa:
        logger.warning("Cannot create a movie product without allocineId nor visa")
        return None

    # (tcoudray-pass, 04/07/25) TODO: Move truncation outside this function
    if len(movie.title) > 140:
        movie.title = movie.title[0:139] + "…"

    products = products_repository.get_movie_products_matching_allocine_id_or_film_visa(movie.allocine_id, movie.visa)

    # Case 1: Creation of a new a product
    if not products:
        with transaction():
            product = products_models.Product(
                description=movie.description,
                durationMinutes=movie.duration,
                extraData=None,
                lastProviderId=provider.id,
                name=movie.title,
                subcategoryId=subcategories.SEANCE_CINE.id,
            )
            _update_product_extra_data(product, movie)
            db.session.add(product)
        return product

    # Case 2: Update of one existing product
    if len(products) == 1:
        product = products[0]
        if _is_allocine(provider.id) or provider.id == product.lastProviderId:
            with transaction():
                _update_movie_product(product, movie, provider.id, id_at_providers)
        return product

    # Case 3: 2 products were returned
    if products[0].extraData and products[0].extraData.get("allocineId"):  # mypy does not know extraData cannot be None
        product_with_allocine_id, product_with_visa = products
    else:
        product_with_visa, product_with_allocine_id = products

    with transaction():
        if _should_merge_product(product_with_visa, product_with_allocine_id):
            # Case 3.1: the 2 products should be merged into one
            logger.info(
                "Merging movie products %d (to keep) and %d (to delete)",
                product_with_allocine_id.id,
                product_with_visa.id,
                extra={
                    "allocine_id": movie.allocine_id,
                    "visa": movie.visa,
                    "provider_id": provider.id,
                    "deleted": {
                        "name": product_with_visa.name,
                        "description": product_with_visa.description,
                    },
                    "kept": {
                        "name": product_with_allocine_id.name,
                        "description": product_with_allocine_id.description,
                    },
                },
            )
            product = products_repository.merge_products(product_with_allocine_id, product_with_visa)
            if _is_allocine(provider.id) or provider.id == product.lastProviderId:
                _update_movie_product(product, movie, provider.id, id_at_providers)
        else:
            # Case 3.2: the 2 products are DIFFERENT -> selection of the most coherent one
            # we do NOT update the product because if we reached this step, it means
            # the provider has sent us incoherent visa and allocineId
            product = _select_matching_product(movie, product_with_allocine_id, product_with_visa)
            logger.warning(
                "Provider sent incoherent visa and allocineId",
                extra={
                    "movie": {
                        "allocine_id": movie.allocine_id,
                        "visa": movie.visa,
                        "title": movie.title,
                        "description": movie.description,
                    },
                    "provider_id": provider.id,
                    "product_id": product.id,
                },
            )

    return product


def _is_allocine(provider_id: int) -> bool:
    allocine_products_provider_id = get_allocine_products_provider().id
    allocine_stocks_provider_id = get_provider_by_local_class("AllocineStocks").id
    return provider_id in (allocine_products_provider_id, allocine_stocks_provider_id)


def _update_movie_product(
    product: products_models.Product, movie: products_models.Movie, provider_id: int, id_at_providers: str
) -> None:
    product.description = movie.description
    product.durationMinutes = movie.duration
    product.lastProviderId = provider_id
    product.name = movie.title
    _update_product_extra_data(product, movie)


def _update_product_extra_data(product: products_models.Product, movie: products_models.Movie) -> None:
    product.extraData = product.extraData or offers_models.OfferExtraData()
    extra_data = movie.extra_data or offers_models.OfferExtraData()
    if movie.allocine_id:
        extra_data["allocineId"] = int(movie.allocine_id)
    if movie.visa:
        extra_data["visa"] = movie.visa

    product.extraData.update((key, value) for key, value in extra_data.items() if value is not None)  # type: ignore[typeddict-item]


def _chronicles_count_query(start: int, end: int) -> sa.sql.expression.Select:
    return (
        sa.select(
            chronicles_models.ProductChronicle.productId.label("product_id"),
            sa.func.count(chronicles_models.ProductChronicle.productId).label("total"),
        )
        .where(
            chronicles_models.ProductChronicle.productId >= start, chronicles_models.ProductChronicle.productId < end
        )
        .group_by(chronicles_models.ProductChronicle.productId)
    )


def _headlines_count_query(start: int, end: int) -> sa.sql.expression.Select:
    return (
        sa.select(
            offers_models.Offer.productId.label("product_id"),
            sa.func.count(offers_models.Offer.productId).label("total"),
        )
        .select_from(offers_models.HeadlineOffer)
        .join(offers_models.Offer, offers_models.HeadlineOffer.offerId == offers_models.Offer.id)
        .where(offers_models.Offer.productId >= start, offers_models.Offer.productId < end)
        .group_by(offers_models.Offer.productId)
    )


def _likes_count_query(start: int, end: int) -> sa.sql.expression.Select:
    return (
        sa.select(
            reactions_models.Reaction.productId.label("product_id"),
            sa.func.count(reactions_models.Reaction.productId).label("total"),
        )
        .where(reactions_models.Reaction.reactionType == reactions_models.ReactionTypeEnum.LIKE)
        .where(reactions_models.Reaction.productId >= start, reactions_models.Reaction.productId < end)
        .group_by(reactions_models.Reaction.productId)
    )


def fetch_inconsistent_products(batch_size: int = 10_000) -> set[int]:
    product_ids = set()
    start = 0
    product_max_id = db.session.execute(sa.select(sa.func.max(models.Product.id))).scalar()
    while start < product_max_id:
        end = start + batch_size
        batch_result = fetch_inconsistent_products_on_column(_chronicles_count_query(start, end), "chroniclesCount")
        batch_result += fetch_inconsistent_products_on_column(_headlines_count_query(start, end), "headlinesCount")
        batch_result += fetch_inconsistent_products_on_column(_likes_count_query(start, end), "likesCount")

        product_ids.update(batch_result)
        start += batch_size

    return product_ids


def fetch_inconsistent_products_on_column(count_query: sa.sql.expression.Select, col_name: str) -> list[int]:
    subquery = count_query.subquery()
    query = (
        sa.select(models.Product.id)
        .where(models.Product.id == subquery.c.product_id)
        .where(getattr(models.Product, col_name) != subquery.c.total)
    )
    product_ids = db.session.execute(query).scalars().all()
    return product_ids


def approves_provider_product_and_rejected_offers(ean: str) -> None:
    product = (
        db.session.query(products_models.Product)
        .filter(
            products_models.Product.gcuCompatibilityType == products_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
            products_models.Product.ean == ean,
        )
        .one_or_none()
    )

    if not product:
        raise exceptions.ProductNotFound()

    offer_ids = []
    try:
        with transaction():
            product.gcuCompatibilityType = products_models.GcuCompatibilityType.COMPATIBLE
            db.session.add(product)

            offers_query = (
                db.session.query(offers_models.Offer)
                .filter(
                    offers_models.Offer.productId == product.id,
                    offers_models.Offer.validation == offers_models.OfferValidationStatus.REJECTED,
                    offers_models.Offer.lastValidationType == OfferValidationType.CGU_INCOMPATIBLE_PRODUCT,
                )
                .options(sa_orm.load_only(offers_models.Offer.id))
            )

            offers = offers_query.all()

            offer_updated_counts = offers_query.update(
                values={
                    "validation": offers_models.OfferValidationStatus.APPROVED,
                    "lastValidationDate": datetime.datetime.utcnow(),
                    "lastValidationType": OfferValidationType.AUTO,
                },
                synchronize_session=False,
            )

            offer_ids = [offer.id for offer in offers]

            logger.info(
                "Approve product and rejected offers",
                extra={
                    "ean": ean,
                    "product": product.id,
                    "offers": offer_ids,
                    "offer_updated_counts": offer_updated_counts,
                },
            )

        if offer_ids:
            search.async_index_offer_ids(
                set(offer_ids),
                reason=search.IndexationReason.CINEMA_STOCK_QUANTITY_UPDATE,
            )

    except Exception as exception:
        logger.exception(
            "Could not approve product and rejected offers: %s",
            extra={"ean": ean, "product": product.id, "offers": offer_ids, "exc": str(exception)},
        )
        raise exceptions.NotUpdateProductOrOffers(exception)
