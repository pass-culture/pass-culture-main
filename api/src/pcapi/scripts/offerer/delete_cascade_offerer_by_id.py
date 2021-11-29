import logging

from pcapi.core import search
from pcapi.core.bookings.exceptions import CannotDeleteOffererWithBookingsException
from pcapi.core.bookings.models import Booking
from pcapi.core.finance.models import BusinessUnit
from pcapi.core.offerers.models import ApiKey
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Mediation
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.providers.models import AllocineVenueProvider
from pcapi.core.providers.models import AllocineVenueProviderPriceRule
from pcapi.core.providers.models import VenueProvider
from pcapi.core.users.models import Favorite
from pcapi.models import db
from pcapi.models.bank_information import BankInformation
from pcapi.models.offer_criterion import OfferCriterion
from pcapi.models.product import Product
from pcapi.models.user_offerer import UserOfferer


logger = logging.getLogger(__name__)


def delete_cascade_offerer_by_id(offerer_id: int) -> None:
    offerer_has_bookings = db.session.query(Booking.query.filter(Booking.offererId == offerer_id).exists()).scalar()

    if offerer_has_bookings:
        raise CannotDeleteOffererWithBookingsException()

    deleted_stocks_count = Stock.query.filter(
        Stock.offerId == Offer.id, Offer.venueId == Venue.id, Venue.managingOffererId == offerer_id
    ).delete(synchronize_session=False)

    deleted_favorites_count = Favorite.query.filter(
        Favorite.offerId == Offer.id, Offer.venueId == Venue.id, Venue.managingOffererId == offerer_id
    ).delete(synchronize_session=False)

    deleted_offer_criteria_count = OfferCriterion.query.filter(
        OfferCriterion.offerId == Offer.id, Offer.venueId == Venue.id, Venue.managingOffererId == offerer_id
    ).delete(synchronize_session=False)

    deleted_mediations_count = Mediation.query.filter(
        Mediation.offerId == Offer.id, Offer.venueId == Venue.id, Venue.managingOffererId == offerer_id
    ).delete(synchronize_session=False)

    AllocineVenueProviderPriceRule.query.filter(
        AllocineVenueProviderPriceRule.allocineVenueProviderId == AllocineVenueProvider.id,
        AllocineVenueProvider.id == VenueProvider.id,
        VenueProvider.venueId == Venue.id,
        Venue.managingOffererId == offerer_id,
    ).delete(synchronize_session=False)
    deleted_allocine_venue_providers_count = AllocineVenueProvider.query.filter(
        AllocineVenueProvider.id == VenueProvider.id,
        VenueProvider.venueId == Venue.id,
        Venue.managingOffererId == offerer_id,
    ).delete(synchronize_session=False)

    offer_ids_to_delete = [
        id[0]
        for id in db.session.query(Offer.id)
        .filter(Offer.venueId == Venue.id, Venue.managingOffererId == offerer_id)
        .all()
    ]

    deleted_offers_count = Offer.query.filter(Offer.venueId == Venue.id, Venue.managingOffererId == offerer_id).delete(
        synchronize_session=False
    )

    deleted_venue_providers_count = VenueProvider.query.filter(
        VenueProvider.venueId == Venue.id, Venue.managingOffererId == offerer_id
    ).delete(synchronize_session=False)

    # Handle relationship loop: Venue->BusinessUnit->BankInformation->Venue.
    business_unit_ids_to_delete = {
        id_ for id_, in Venue.query.filter_by(managingOffererId=offerer_id).with_entities(Venue.businessUnitId)
    }
    Venue.query.filter_by(managingOffererId=offerer_id).update({"businessUnitId": None}, synchronize_session=False)
    bank_information_ids_to_delete = {
        id_
        for id_, in BusinessUnit.query.filter(BusinessUnit.id.in_(business_unit_ids_to_delete)).with_entities(
            BusinessUnit.bankAccountId
        )
    }
    deleted_business_unit_count = BusinessUnit.query.filter(BusinessUnit.id.in_(business_unit_ids_to_delete)).delete(
        synchronize_session=False
    )

    deleted_bank_informations_count = 0
    deleted_bank_informations_count += BankInformation.query.filter(
        BankInformation.venueId == Venue.id, Venue.managingOffererId == offerer_id
    ).delete(synchronize_session=False)
    deleted_bank_informations_count += BankInformation.query.filter(BankInformation.offererId == offerer_id).delete(
        synchronize_session=False
    )
    deleted_bank_informations_count += BankInformation.query.filter(
        BankInformation.id.in_(bank_information_ids_to_delete)
    ).delete(synchronize_session=False)

    deleted_venues_count = Venue.query.filter(Venue.managingOffererId == offerer_id).delete(synchronize_session=False)

    deleted_user_offerers_count = UserOfferer.query.filter(UserOfferer.offererId == offerer_id).delete(
        synchronize_session=False
    )

    deleted_product_count = Product.query.filter(Product.owningOffererId == offerer_id).delete(
        synchronize_session=False
    )

    deleted_api_key_count = ApiKey.query.filter(ApiKey.offererId == offerer_id).delete(synchronize_session=False)

    Offerer.query.filter(Offerer.id == offerer_id).delete()

    db.session.commit()
    search.unindex_offer_ids(offer_ids_to_delete)

    recap_data = {
        "offer_ids_to_unindex": offer_ids_to_delete,
        "offerer_id": offerer_id,
        "deleted_api_key_count": deleted_api_key_count,
        "deleted_user_offerers_count": deleted_user_offerers_count,
        "deleted_bank_informations_count": deleted_bank_informations_count,
        "deleted_business_unit_count": deleted_business_unit_count,
        "deleted_product_count": deleted_product_count,
        "deleted_venues_count": deleted_venues_count,
        "deleted_venue_providers_count": deleted_venue_providers_count,
        "deleted_allocine_venue_providers_count": deleted_allocine_venue_providers_count,
        "deleted_offers_count": deleted_offers_count,
        "deleted_mediations_count": deleted_mediations_count,
        "deleted_favorites_count": deleted_favorites_count,
        "deleted_offer_criteria_count": deleted_offer_criteria_count,
        "deleted_stocks_count": deleted_stocks_count,
    }

    logger.info("Deleted offerer", extra=recap_data)

    return recap_data
