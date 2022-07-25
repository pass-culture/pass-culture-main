import logging

from pcapi.core import search
from pcapi.core.bookings.exceptions import CannotDeleteVenueWithBookingsException
from pcapi.core.bookings.models import Booking
import pcapi.core.criteria.models as criteria_models
from pcapi.core.educational import models as educational_models
import pcapi.core.finance.models as finance_models
from pcapi.core.finance.models import BankInformation
import pcapi.core.offerers.models as offerers_models
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import ActivationCode
from pcapi.core.offers.models import Mediation
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.providers.models import AllocineVenueProvider
from pcapi.core.providers.models import AllocineVenueProviderPriceRule
from pcapi.core.providers.models import VenueProvider
from pcapi.core.users.models import Favorite
from pcapi.models import db


logger = logging.getLogger(__name__)


def delete_cascade_venue_by_id(venue_id: int) -> None:
    venue_has_bookings = db.session.query(Booking.query.filter(Booking.venueId == venue_id).exists()).scalar()
    venue_has_collective_bookings = db.session.query(
        educational_models.CollectiveBooking.query.filter(
            educational_models.CollectiveBooking.venueId == venue_id
        ).exists()
    ).scalar()

    if venue_has_bookings or venue_has_collective_bookings:
        raise CannotDeleteVenueWithBookingsException()

    deleted_activation_codes_count = ActivationCode.query.filter(
        ActivationCode.stockId == Stock.id,
        Stock.offerId == Offer.id,
        Offer.venueId == venue_id,
        # All bookingId should be None if venue_has_bookings is False, keep condition to get an exception otherwise
        ActivationCode.bookingId.is_(None),
    ).delete(synchronize_session=False)

    deleted_stocks_count = Stock.query.filter(Stock.offerId == Offer.id, Offer.venueId == venue_id).delete(
        synchronize_session=False
    )
    deleted_collective_stocks_count = educational_models.CollectiveStock.query.filter(
        educational_models.CollectiveStock.collectiveOfferId == educational_models.CollectiveOffer.id,
        educational_models.CollectiveOffer.venueId == venue_id,
    ).delete(synchronize_session=False)

    deleted_favorites_count = Favorite.query.filter(Favorite.offerId == Offer.id, Offer.venueId == venue_id).delete(
        synchronize_session=False
    )

    deleted_offer_criteria_count = criteria_models.OfferCriterion.query.filter(
        criteria_models.OfferCriterion.offerId == Offer.id, Offer.venueId == venue_id
    ).delete(synchronize_session=False)

    deleted_mediations_count = Mediation.query.filter(Mediation.offerId == Offer.id, Offer.venueId == venue_id).delete(
        synchronize_session=False
    )

    AllocineVenueProviderPriceRule.query.filter(
        AllocineVenueProviderPriceRule.allocineVenueProviderId == AllocineVenueProvider.id,
        AllocineVenueProvider.id == VenueProvider.id,
        VenueProvider.venueId == venue_id,
        Venue.id == venue_id,
    ).delete(synchronize_session=False)
    deleted_allocine_venue_providers_count = AllocineVenueProvider.query.filter(
        AllocineVenueProvider.id == VenueProvider.id,
        VenueProvider.venueId == venue_id,
        Venue.id == venue_id,
    ).delete(synchronize_session=False)

    offer_ids_to_delete = [id[0] for id in db.session.query(Offer.id).filter(Offer.venueId == venue_id).all()]
    collective_offer_ids_to_delete = [
        id[0]
        for id in db.session.query(educational_models.CollectiveOffer.id)
        .filter(educational_models.CollectiveOffer.venueId == venue_id)
        .all()
    ]
    collective_offer_template_ids_to_delete = [
        id[0]
        for id in db.session.query(educational_models.CollectiveOfferTemplate.id)
        .filter(educational_models.CollectiveOfferTemplate.venueId == venue_id)
        .all()
    ]

    deleted_offers_count = Offer.query.filter(Offer.venueId == venue_id).delete(synchronize_session=False)
    deleted_collective_offers_count = educational_models.CollectiveOffer.query.filter(
        educational_models.CollectiveOffer.venueId == venue_id
    ).delete(synchronize_session=False)
    deleted_collective_offer_templates_count = educational_models.CollectiveOfferTemplate.query.filter(
        educational_models.CollectiveOfferTemplate.venueId == venue_id
    ).delete(synchronize_session=False)

    deleted_venue_providers_count = VenueProvider.query.filter(VenueProvider.venueId == venue_id).delete(
        synchronize_session=False
    )

    deleted_business_unit_venue_links_count = finance_models.BusinessUnitVenueLink.query.filter_by(
        venueId=venue_id
    ).delete(synchronize_session=False)

    deleted_bank_informations_count = BankInformation.query.filter(BankInformation.venueId == venue_id).delete(
        synchronize_session=False
    )

    # Warning: we should only delete rows where the "venueId" is the
    # venue to delete. We should NOT delete rows where the
    # "pricingPointId" or the "reimbursementId" is the venue to
    # delete. If other venues still have the "venue to delete" as
    # their pricing/reimbursement point, the database will rightfully
    # raise an error. Either these venues should be deleted first, or
    # the "venue to delete" should not be deleted.
    deleted_pricing_point_links_count = offerers_models.VenuePricingPointLink.query.filter_by(
        venueId=venue_id,
    ).delete(synchronize_session=False)
    deleted_reimbursement_point_links_count = offerers_models.VenueReimbursementPointLink.query.filter_by(
        venueId=venue_id
    ).delete(synchronize_session=False)

    deleted_venues_count = Venue.query.filter(Venue.id == venue_id).delete(synchronize_session=False)

    db.session.commit()

    search.unindex_offer_ids(offer_ids_to_delete)
    search.unindex_collective_offer_ids(collective_offer_ids_to_delete)
    search.unindex_collective_offer_template_ids(collective_offer_template_ids_to_delete)
    search.unindex_venue_ids([venue_id])

    recap_data = {
        "offer_ids_to_unindex": offer_ids_to_delete,
        "collective_offer_ids_to_unindex": collective_offer_ids_to_delete,
        "collective_offer_template_ids_to_unindex": collective_offer_template_ids_to_delete,
        "venue_id": venue_id,
        "deleted_bank_informations_count": deleted_bank_informations_count,
        "deleted_venues_count": deleted_venues_count,
        "deleted_venue_providers_count": deleted_venue_providers_count,
        "deleted_allocine_venue_providers_count": deleted_allocine_venue_providers_count,
        "deleted_business_unit_venue_links": deleted_business_unit_venue_links_count,
        "deleted_offers_count": deleted_offers_count,
        "deleted_collective_offers_count": deleted_collective_offers_count,
        "deleted_collective_offer_templates_count": deleted_collective_offer_templates_count,
        "deleted_mediations_count": deleted_mediations_count,
        "deleted_favorites_count": deleted_favorites_count,
        "deleted_offer_criteria_count": deleted_offer_criteria_count,
        "deleted_pricing_point_links_count": deleted_pricing_point_links_count,
        "deleted_reimbursement_point_links_count": deleted_reimbursement_point_links_count,
        "deleted_stocks_count": deleted_stocks_count,
        "deleted_collective_stocks_count": deleted_collective_stocks_count,
        "deleted_activation_codes_count": deleted_activation_codes_count,
    }
    logger.info("Deleted venue", extra=recap_data)

    return recap_data  # type: ignore [return-value]
