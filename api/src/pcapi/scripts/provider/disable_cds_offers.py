import datetime
import logging

from pcapi.core import search
import pcapi.core.offers.models as offers_models
import pcapi.core.offers.repository as offers_repository
import pcapi.core.providers.models as providers_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus


logger = logging.getLogger(__name__)


def batch_update_offers(query, update_fields):  # type: ignore [no-untyped-def]
    raw_results = (
        query.filter(offers_models.Offer.validation == OfferValidationStatus.APPROVED)
        .with_entities(offers_models.Offer.id, offers_models.Offer.venueId)
        .all()
    )
    offer_ids, venue_ids = [], []
    if raw_results:
        offer_ids, venue_ids = zip(*raw_results)
    venue_ids = sorted(set(venue_ids))
    logger.info(
        "Batch update of offers",
        extra={"updated_fields": update_fields, "nb_offers": len(offer_ids), "venue_ids": venue_ids},
    )
    if "isActive" in update_fields.keys():
        if update_fields["isActive"]:
            logger.info(
                "Offers has been activated",
                extra={"offer_ids": offer_ids, "venue_id": venue_ids},
                technical_message_id="offers.activated",
            )
        else:
            logger.info(
                "Offers has been deactivated",
                extra={"offer_ids": offer_ids, "venue_id": venue_ids},
                technical_message_id="offers.deactivated",
            )
    script_date = datetime.datetime.utcnow()
    number_of_offers_to_update = len(offer_ids)
    batch_size = 1000
    for current_start_index in range(0, number_of_offers_to_update, batch_size):
        offer_ids_batch = offer_ids[
            current_start_index : min(current_start_index + batch_size, number_of_offers_to_update)
        ]
        for offer_id in offer_ids_batch:
            stocks = (
                offers_models.Stock.query.filter(offers_models.Stock.offerId == offer_id)
                .filter(offers_models.Stock.beginningDatetime > script_date)
                .all()
            )
            stock_ids = [stock.id for stock in stocks]
            for stock_id in stock_ids:
                offers_models.Stock.query.filter(offers_models.Stock.id == stock_id).update(
                    {"quantity": offers_models.Stock.dnBookedQuantity}
                )

        query_to_update = offers_models.Offer.query.filter(offers_models.Offer.id.in_(offer_ids_batch))
        query_to_update.update(update_fields, synchronize_session=False)
        db.session.commit()

        search.async_index_offer_ids(offer_ids_batch)


def update_offers_to_disabled_and_sold_out():
    CDS_PROVIDER_ID = 70

    venue_providers = providers_models.VenueProvider.query.filter(
        providers_models.VenueProvider.providerId == CDS_PROVIDER_ID
    ).all()
    venue_ids = [venue_provider.venueId for venue_provider in venue_providers]
    print(venue_ids)

    for venue_id in venue_ids:
        venue_synchronized_offers_query = offers_repository.get_synchronized_offers_with_provider_for_venue(
            venue_id, CDS_PROVIDER_ID
        ).filter(~offers_models.Offer.idAtProvider.contains("%CDS"))

        batch_update_offers(venue_synchronized_offers_query, {"isActive": False})
