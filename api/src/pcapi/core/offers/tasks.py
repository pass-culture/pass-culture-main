import datetime
import sqlalchemy as sa
import logging


from pcapi import repository
from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.core import search
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import constants as offers_constants
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import schemas as offers_schemas
from pcapi.core.providers import models as providers_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.routes.public.individual_offers.v1 import serialization as individual_offers_serialization
from pcapi.routes.public.individual_offers.v1 import utils as individual_offers_utils
from pcapi.workers import worker
from pcapi.workers.decorators import job

logger = logging.getLogger(__name__)


@job(worker.low_queue)
def create_or_update_ean_offers(
    *,
    serialized_products_stocks: dict,
    venue_id: int,
    provider_id: int,
    address_id: int | None = None,
    address_label: str | None = None,
) -> None:
    provider = db.session.query(providers_models.Provider).filter_by(id=provider_id).one()
    venue = db.session.query(offerers_models.Venue).filter_by(id=venue_id).one()

    ean_to_create_or_update = set(serialized_products_stocks.keys())

    offers_to_update = offers_api.get_existing_offers(ean_to_create_or_update, venue)
    offer_to_update_by_ean = {}
    ean_list_to_update = set()
    for offer in offers_to_update:
        offer_ean = offer.ean
        ean_list_to_update.add(offer_ean)
        offer_to_update_by_ean[offer_ean] = offer

    ean_list_to_create = ean_to_create_or_update - ean_list_to_update
    offers_to_index = []
    with repository.transaction():
        offerer_address = venue.offererAddress  # default offerer_address

        if address_id:
            offerer_address = offerers_api.get_or_create_offerer_address(
                offerer_id=venue.managingOffererId,
                address_id=address_id,
                label=address_label,
            )

        if ean_list_to_create:
            created_offers = []
            existing_products = offers_api.get_existing_products(ean_list_to_create)
            product_by_ean = {product.ean: product for product in existing_products}
            not_found_eans = [ean for ean in ean_list_to_create if ean not in product_by_ean.keys()]
            if not_found_eans:
                logger.warning(
                    "Some provided eans were not found",
                    extra={"eans": ",".join(not_found_eans), "venue": venue_id},
                    technical_message_id="ean.not_found",
                )
            for product in existing_products:
                try:
                    ean = product.ean
                    stock_data = serialized_products_stocks[ean]
                    created_offer = offers_api.create_offer_from_product(
                        venue,
                        product_by_ean[ean],
                        provider,
                        offererAddress=offerer_address,
                    )
                    created_offers.append(created_offer)

                except offers_exceptions.OfferException as exc:
                    logger.info(
                        "Error while creating offer by ean",
                        extra={
                            "ean": ean,
                            "venue_id": venue_id,
                            "provider_id": provider_id,
                            "exc": exc.__class__.__name__,
                        },
                    )

            db.session.bulk_save_objects(created_offers)

            reloaded_offers = offers_api.get_existing_offers(ean_list_to_create, venue)
            for offer in reloaded_offers:
                try:
                    ean = offer.ean
                    stock_data = serialized_products_stocks[ean]

                    # No need to create empty stock
                    if stock_data["quantity"] == 0:
                        continue

                    # FIXME (mageoffray, 2023-05-26): stock saving optimisation
                    # Stocks are inserted one by one for now, we need to improve create_stock to remove the repository.session.add()
                    # It will be done before the release of this API
                    offers_api.create_stock(
                        offer=offer,
                        price=finance_utils.cents_to_full_unit(stock_data["price"]),
                        quantity=individual_offers_serialization.deserialize_quantity(stock_data["quantity"]),
                        booking_limit_datetime=stock_data["booking_limit_datetime"],
                        creating_provider=provider,
                    )
                except offers_exceptions.OfferException as exc:
                    logger.info(
                        "Error while creating offer by ean",
                        extra={
                            "ean": ean,
                            "venue_id": venue_id,
                            "provider_id": provider_id,
                            "exc": exc.__class__.__name__,
                        },
                    )

        for offer in offers_to_update:
            try:
                offer.lastProvider = provider
                offer.isActive = True
                offer.offererAddress = offerer_address

                ean = offer.ean
                stock_data = serialized_products_stocks[ean]
                # FIXME (mageoffray, 2023-05-26): stock upserting optimisation
                # Stocks are edited one by one for now, we need to improve edit_stock to remove the repository.session.add()
                # It will be done before the release of this API

                # TODO(jbaudet-pass): remove call to .replace(): it should not
                # be needed.
                # Why? Because input checks remove the timezone information as
                # it is not expected after... but StockEdition needs a
                # timezone-aware datetime object.
                # -> datetimes are not always handleded the same way.
                # -> it can be messy.
                booking_limit = stock_data["booking_limit_datetime"]
                booking_limit = booking_limit.replace(tzinfo=datetime.timezone.utc) if booking_limit else None

                offers_api.upsert_product_stock(
                    offer_to_update_by_ean[ean],
                    individual_offers_serialization.StockEdition(
                        **{
                            "price": stock_data["price"],
                            "quantity": stock_data["quantity"],
                            "booking_limit_datetime": booking_limit,
                        }
                    ),
                    provider,
                )
                offers_to_index.append(offer_to_update_by_ean[ean].id)

            except offers_exceptions.OfferException as exc:
                logger.info(
                    "Error while creating offer by ean",
                    extra={
                        "ean": ean,
                        "venue_id": venue_id,
                        "provider_id": provider_id,
                        "exc": exc.__class__.__name__,
                    },
                )

    search.async_index_offer_ids(
        offers_to_index,
        reason=search.IndexationReason.OFFER_UPDATE,
        log_extra={"venue_id": venue_id, "source": "offers_public_api"},
    )
