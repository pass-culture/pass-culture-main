import logging

from pcapi.core import search
import pcapi.core.bookings.models as booking_models
import pcapi.core.criteria.models as criteria_models
from pcapi.core.educational import models as educational_models
import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.exceptions as offerers_exceptions
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.models as providers_models
import pcapi.core.users.models as users_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def delete_cascade_venue_by_id(venue_id: int) -> None:
    venue_has_bookings = db.session.query(
        booking_models.Booking.query.filter(booking_models.Booking.venueId == venue_id).exists()
    ).scalar()
    venue_has_collective_bookings = db.session.query(
        educational_models.CollectiveBooking.query.filter(
            educational_models.CollectiveBooking.venueId == venue_id
        ).exists()
    ).scalar()

    if venue_has_bookings or venue_has_collective_bookings:
        raise offerers_exceptions.CannotDeleteVenueWithBookingsException()

    venue_used_as_pricing_point = db.session.query(
        offerers_models.VenuePricingPointLink.query.filter(
            offerers_models.VenuePricingPointLink.venueId != venue_id,
            offerers_models.VenuePricingPointLink.pricingPointId == venue_id,
        ).exists()
    ).scalar()

    if venue_used_as_pricing_point:
        raise offerers_exceptions.CannotDeleteVenueUsedAsPricingPointException()

    venue_used_as_reimbursement_point = db.session.query(
        offerers_models.VenueReimbursementPointLink.query.filter(
            offerers_models.VenueReimbursementPointLink.venueId != venue_id,
            offerers_models.VenueReimbursementPointLink.reimbursementPointId == venue_id,
        ).exists()
    ).scalar()

    if venue_used_as_reimbursement_point:
        raise offerers_exceptions.CannotDeleteVenueUsedAsReimbursementPointException()

    deleted_activation_codes_count = offers_models.ActivationCode.query.filter(
        offers_models.ActivationCode.stockId == offers_models.Stock.id,
        offers_models.Stock.offerId == offers_models.Offer.id,
        offers_models.Offer.venueId == venue_id,
        # All bookingId should be None if venue_has_bookings is False, keep condition to get an exception otherwise
        offers_models.ActivationCode.bookingId.is_(None),
    ).delete(synchronize_session=False)

    deleted_stocks_count = offers_models.Stock.query.filter(
        offers_models.Stock.offerId == offers_models.Offer.id, offers_models.Offer.venueId == venue_id
    ).delete(synchronize_session=False)
    deleted_collective_stocks_count = educational_models.CollectiveStock.query.filter(
        educational_models.CollectiveStock.collectiveOfferId == educational_models.CollectiveOffer.id,
        educational_models.CollectiveOffer.venueId == venue_id,
    ).delete(synchronize_session=False)

    deleted_favorites_count = users_models.Favorite.query.filter(
        users_models.Favorite.offerId == offers_models.Offer.id, offers_models.Offer.venueId == venue_id
    ).delete(synchronize_session=False)

    deleted_offer_criteria_count = criteria_models.OfferCriterion.query.filter(
        criteria_models.OfferCriterion.offerId == offers_models.Offer.id, offers_models.Offer.venueId == venue_id
    ).delete(synchronize_session=False)

    deleted_mediations_count = offers_models.Mediation.query.filter(
        offers_models.Mediation.offerId == offers_models.Offer.id, offers_models.Offer.venueId == venue_id
    ).delete(synchronize_session=False)

    providers_models.AllocineVenueProviderPriceRule.query.filter(
        providers_models.AllocineVenueProviderPriceRule.allocineVenueProviderId
        == providers_models.AllocineVenueProvider.id,
        providers_models.AllocineVenueProvider.id == providers_models.VenueProvider.id,
        providers_models.VenueProvider.venueId == venue_id,
        offerers_models.Venue.id == venue_id,
    ).delete(synchronize_session=False)
    deleted_allocine_venue_providers_count = providers_models.AllocineVenueProvider.query.filter(
        providers_models.AllocineVenueProvider.id == providers_models.VenueProvider.id,
        providers_models.VenueProvider.venueId == venue_id,
        offerers_models.Venue.id == venue_id,
    ).delete(synchronize_session=False)
    deleted_allocine_pivot_count = providers_models.AllocinePivot.query.filter_by(venueId=venue_id).delete(
        synchronize_session=False
    )

    offer_ids_to_delete = [
        id[0] for id in db.session.query(offers_models.Offer.id).filter(offers_models.Offer.venueId == venue_id).all()
    ]
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

    deleted_offers_count = offers_models.Offer.query.filter(offers_models.Offer.venueId == venue_id).delete(
        synchronize_session=False
    )

    deleted_collective_offers_count = educational_models.CollectiveOffer.query.filter(
        educational_models.CollectiveOffer.venueId == venue_id
    ).delete(synchronize_session=False)

    collective_offer_template_link_deleted = educational_models.CollectiveOffer.query.filter(
        educational_models.CollectiveOffer.id.in_(
            db.session.query(educational_models.CollectiveOffer.id)
            .join(educational_models.CollectiveOfferTemplate, educational_models.CollectiveOffer.template)
            .filter(educational_models.CollectiveOfferTemplate.venueId == venue_id)
        )
    ).update({"templateId": None}, synchronize_session=False)

    deleted_collective_offer_templates_count = educational_models.CollectiveOfferTemplate.query.filter(
        educational_models.CollectiveOfferTemplate.venueId == venue_id
    ).delete(synchronize_session=False)

    deleted_venue_providers_count = providers_models.VenueProvider.query.filter(
        providers_models.VenueProvider.venueId == venue_id
    ).delete(synchronize_session=False)

    deleted_bank_informations_count = finance_models.BankInformation.query.filter(
        finance_models.BankInformation.venueId == venue_id
    ).delete(synchronize_session=False)

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

    deleted_venues_count = offerers_models.Venue.query.filter(offerers_models.Venue.id == venue_id).delete(
        synchronize_session=False
    )

    db.session.commit()

    search.unindex_offer_ids(offer_ids_to_delete)
    search.unindex_collective_offer_ids(collective_offer_ids_to_delete)
    search.unindex_collective_offer_template_ids(collective_offer_template_ids_to_delete)
    search.unindex_venue_ids([venue_id])

    recap_data = {
        "offer_ids_to_unindex": offer_ids_to_delete,
        "collective_offer_ids_to_unindex": collective_offer_ids_to_delete,
        "collective_offer_template_ids_to_unindex": collective_offer_template_ids_to_delete,
        "collective_offer_template_link_deleted": collective_offer_template_link_deleted,
        "venue_id": venue_id,
        "deleted_bank_informations_count": deleted_bank_informations_count,
        "deleted_venues_count": deleted_venues_count,
        "deleted_venue_providers_count": deleted_venue_providers_count,
        "deleted_allocine_venue_providers_count": deleted_allocine_venue_providers_count,
        "deleted_allocine_pivot_count": deleted_allocine_pivot_count,
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
