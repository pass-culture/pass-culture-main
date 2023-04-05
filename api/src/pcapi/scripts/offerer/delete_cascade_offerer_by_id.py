import logging

import sqlalchemy as sqla

from pcapi.core import search
import pcapi.core.bookings.models as booking_models
import pcapi.core.criteria.models as criteria_models
import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.exceptions as offerers_exceptions
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.models as providers_models
import pcapi.core.users.models as users_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def delete_cascade_offerer_by_id(offerer_id: int) -> None:
    offerer_has_bookings = db.session.query(
        booking_models.Booking.query.filter(booking_models.Booking.offererId == offerer_id).exists()
    ).scalar()

    if offerer_has_bookings:
        raise offerers_exceptions.CannotDeleteOffererWithBookingsException()

    venue_ids = offerers_models.Venue.query.filter_by(managingOffererId=offerer_id).with_entities(
        offerers_models.Venue.id
    )

    deleted_activation_codes_count = offers_models.ActivationCode.query.filter(
        offers_models.ActivationCode.stockId == offers_models.Stock.id,
        offers_models.Stock.offerId == offers_models.Offer.id,
        offers_models.Offer.venueId == offerers_models.Venue.id,
        offerers_models.Venue.managingOffererId == offerer_id,
        # All bookingId should be None if offerer_has_bookings is False, keep condition to get an exception otherwise
        offers_models.ActivationCode.bookingId.is_(None),
    ).delete(synchronize_session=False)

    deleted_stocks_count = offers_models.Stock.query.filter(
        offers_models.Stock.offerId == offers_models.Offer.id,
        offers_models.Offer.venueId == offerers_models.Venue.id,
        offerers_models.Venue.managingOffererId == offerer_id,
    ).delete(synchronize_session=False)

    deleted_favorites_count = users_models.Favorite.query.filter(
        users_models.Favorite.offerId == offers_models.Offer.id,
        offers_models.Offer.venueId == offerers_models.Venue.id,
        offerers_models.Venue.managingOffererId == offerer_id,
    ).delete(synchronize_session=False)

    deleted_offer_criteria_count = criteria_models.OfferCriterion.query.filter(
        criteria_models.OfferCriterion.offerId == offers_models.Offer.id,
        offers_models.Offer.venueId == offerers_models.Venue.id,
        offerers_models.Venue.managingOffererId == offerer_id,
    ).delete(synchronize_session=False)

    deleted_mediations_count = offers_models.Mediation.query.filter(
        offers_models.Mediation.offerId == offers_models.Offer.id,
        offers_models.Offer.venueId == offerers_models.Venue.id,
        offerers_models.Venue.managingOffererId == offerer_id,
    ).delete(synchronize_session=False)

    providers_models.AllocineVenueProviderPriceRule.query.filter(
        providers_models.AllocineVenueProviderPriceRule.allocineVenueProviderId
        == providers_models.AllocineVenueProvider.id,
        providers_models.AllocineVenueProvider.id == providers_models.VenueProvider.id,
        providers_models.VenueProvider.venueId == offerers_models.Venue.id,
        offerers_models.Venue.managingOffererId == offerer_id,
    ).delete(synchronize_session=False)
    deleted_allocine_venue_providers_count = providers_models.AllocineVenueProvider.query.filter(
        providers_models.AllocineVenueProvider.id == providers_models.VenueProvider.id,
        providers_models.VenueProvider.venueId == offerers_models.Venue.id,
        offerers_models.Venue.managingOffererId == offerer_id,
    ).delete(synchronize_session=False)
    deleted_allocine_pivot_count = providers_models.AllocinePivot.query.filter(
        providers_models.AllocinePivot.venueId == offerers_models.Venue.id,
        offerers_models.Venue.managingOffererId == offerer_id,
    ).delete(synchronize_session=False)

    offer_ids_to_delete = [
        id[0]
        for id in db.session.query(offers_models.Offer.id)
        .filter(
            offers_models.Offer.venueId == offerers_models.Venue.id,
            offerers_models.Venue.managingOffererId == offerer_id,
        )
        .all()
    ]

    deleted_offers_count = offers_models.Offer.query.filter(
        offers_models.Offer.venueId == offerers_models.Venue.id, offerers_models.Venue.managingOffererId == offerer_id
    ).delete(synchronize_session=False)

    deleted_venue_providers_count = providers_models.VenueProvider.query.filter(
        providers_models.VenueProvider.venueId == offerers_models.Venue.id,
        offerers_models.Venue.managingOffererId == offerer_id,
    ).delete(synchronize_session=False)

    # Handle relationship loop: Venue->BusinessUnit->BankInformation->Venue.
    business_unit_ids_to_delete = {
        id_
        for id_, in offerers_models.Venue.query.filter_by(managingOffererId=offerer_id).with_entities(
            offerers_models.Venue.businessUnitId
        )
    }
    offerers_models.Venue.query.filter_by(managingOffererId=offerer_id).update(
        {"businessUnitId": None}, synchronize_session=False
    )
    bank_information_ids_to_delete = {
        id_
        for id_, in finance_models.BusinessUnit.query.filter(
            finance_models.BusinessUnit.id.in_(business_unit_ids_to_delete)
        ).with_entities(finance_models.BusinessUnit.bankAccountId)
    } | {  # handle old-style BankInformation that are linked to the
        # offerer or one of its venues, where one of the
        # Venue.businessUnit has been cleared.
        id_
        for id_, in finance_models.BankInformation.query.outerjoin(finance_models.BankInformation.venue)
        .filter(
            sqla.or_(
                finance_models.BankInformation.offererId == offerer_id,
                offerers_models.Venue.managingOffererId == offerer_id,
            )
        )
        .with_entities(finance_models.BankInformation.id)
    }
    deleted_business_unit_count = finance_models.BusinessUnit.query.filter(
        finance_models.BusinessUnit.id.in_(business_unit_ids_to_delete)
    ).delete(synchronize_session=False)

    deleted_bank_informations_count = 0
    deleted_bank_informations_count += finance_models.BankInformation.query.filter(
        finance_models.BankInformation.venueId == offerers_models.Venue.id,
        offerers_models.Venue.managingOffererId == offerer_id,
    ).delete(synchronize_session=False)
    deleted_bank_informations_count += finance_models.BankInformation.query.filter(
        finance_models.BankInformation.offererId == offerer_id
    ).delete(synchronize_session=False)
    deleted_bank_informations_count += finance_models.BankInformation.query.filter(
        finance_models.BankInformation.id.in_(bank_information_ids_to_delete)
    ).delete(synchronize_session=False)

    deleted_pricing_point_links_count = offerers_models.VenuePricingPointLink.query.filter(
        offerers_models.VenuePricingPointLink.venueId.in_(venue_ids)
        | offerers_models.VenuePricingPointLink.pricingPointId.in_(venue_ids),
    ).delete(synchronize_session=False)
    deleted_reimbursement_point_links_count = offerers_models.VenueReimbursementPointLink.query.filter(
        offerers_models.VenueReimbursementPointLink.venueId.in_(venue_ids)
        | offerers_models.VenueReimbursementPointLink.reimbursementPointId.in_(venue_ids),
    ).delete(synchronize_session=False)
    deleted_venues_count = offerers_models.Venue.query.filter(
        offerers_models.Venue.managingOffererId == offerer_id
    ).delete(synchronize_session=False)

    deleted_user_offerers_count = offerers_models.UserOfferer.query.filter(
        offerers_models.UserOfferer.offererId == offerer_id
    ).delete(synchronize_session=False)

    deleted_product_count = offers_models.Product.query.filter(
        offers_models.Product.owningOffererId == offerer_id
    ).delete(synchronize_session=False)

    deleted_api_key_count = offerers_models.ApiKey.query.filter(offerers_models.ApiKey.offererId == offerer_id).delete(
        synchronize_session=False
    )

    offerers_models.Offerer.query.filter(offerers_models.Offerer.id == offerer_id).delete()

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
        "deleted_allocine_pivot_count": deleted_allocine_pivot_count,
        "deleted_offers_count": deleted_offers_count,
        "deleted_mediations_count": deleted_mediations_count,
        "deleted_favorites_count": deleted_favorites_count,
        "deleted_offer_criteria_count": deleted_offer_criteria_count,
        "deleted_pricing_point_links_count": deleted_pricing_point_links_count,
        "deleted_reimbursement_point_links_count": deleted_reimbursement_point_links_count,
        "deleted_stocks_count": deleted_stocks_count,
        "deleted_activation_codes_count": deleted_activation_codes_count,
    }

    logger.info("Deleted offerer", extra=recap_data)

    return recap_data  # type: ignore [return-value]
