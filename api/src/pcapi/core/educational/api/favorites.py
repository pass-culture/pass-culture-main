import sqlalchemy as sa

from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import models as offerers_models
from pcapi.repository import repository


def add_offer_to_favorite_adage(
    redactorId: int,
    offerId: int,
) -> educational_models.CollectiveOfferEducationalRedactor:
    favorite_offer = educational_models.CollectiveOfferEducationalRedactor(
        educationalRedactorId=redactorId, collectiveOfferId=offerId
    )
    repository.save(favorite_offer)
    return favorite_offer


def add_offer_template_to_favorite_adage(
    redactorId: int,
    offerId: int,
) -> educational_models.CollectiveOfferTemplateEducationalRedactor:
    favorite_offer = educational_models.CollectiveOfferTemplateEducationalRedactor(
        educationalRedactorId=redactorId, collectiveOfferTemplateId=offerId
    )
    repository.save(favorite_offer)
    return favorite_offer


def get_redactor_all_favorites_count(redactor_id: int) -> int:
    """Return the redactor's total favorite count: collective offers
    and collective offer templates.

    Note:
        Non-eligible for search offers (and templates) are ignored.
    """
    return _offer_favorites_count(redactor_id) + _offer_template_favorites_count(redactor_id)


def _offer_favorites_count(redactor_id: int) -> int:
    # TODO(jeremieb): make CollectiveOffer's is_eligible_for_search
    # a hybrid_property to allow filtering (not sure this is possible however)
    # lots of joinedload because of is_eligible_for_search
    favorite_offers_query = (
        educational_models.CollectiveOfferEducationalRedactor.query.filter_by(educationalRedactorId=redactor_id)
        .options(
            # load the favorite's collective offer...
            sa.orm.joinedload(educational_models.CollectiveOfferEducationalRedactor.collectiveOffer)
            .load_only(
                educational_models.CollectiveOffer.id,
                educational_models.CollectiveOffer.venueId,
                educational_models.CollectiveOffer.validation,
                educational_models.CollectiveOffer.isActive,
            )
            # ... to fetch its venue...
            .joinedload(educational_models.CollectiveOffer.venue)
            .load_only(offerers_models.Venue.managingOffererId)
            # ... to fetch its managing offerer...
            .joinedload(offerers_models.Venue.managingOfferer)
            .load_only(offerers_models.Offerer.isActive, offerers_models.Offerer.validationStatus)
        )
        .options(
            # load the favorite's collective offer...
            sa.orm.joinedload(educational_models.CollectiveOfferEducationalRedactor.collectiveOffer)
            .load_only(
                educational_models.CollectiveOffer.id,
            )
            # ... to fetch its stock...
            .joinedload(educational_models.CollectiveOffer.collectiveStock)
            .load_only(
                educational_models.CollectiveStock.beginningDatetime,
                educational_models.CollectiveStock.bookingLimitDatetime,
                educational_models.CollectiveStock.collectiveOfferId,
            )
            # ... to fetch its booking...
            .joinedload(educational_models.CollectiveStock.collectiveBookings)
            .load_only(educational_models.CollectiveBooking.status)
        )
    )

    favorite_offers = [
        favorite for favorite in favorite_offers_query if favorite.collectiveOffer.is_eligible_for_search
    ]

    return len(favorite_offers)


def _offer_template_favorites_count(redactor_id: int) -> int:
    # TODO(jeremieb): make CollectiveOfferTemplate's is_eligible_for_search
    # a hybrid_property to allow filtering (not sure this is possible however)
    # lots of joinedload because of is_eligible_for_search
    favorite_offer_templates_query = educational_models.CollectiveOfferTemplateEducationalRedactor.query.filter_by(
        educationalRedactorId=redactor_id
    ).options(
        # load the favorite's collective offer template...
        sa.orm.joinedload(educational_models.CollectiveOfferTemplateEducationalRedactor.collectiveOfferTemplate)
        .load_only(
            educational_models.CollectiveOfferTemplate.id,
            educational_models.CollectiveOfferTemplate.venueId,
            educational_models.CollectiveOfferTemplate.validation,
            educational_models.CollectiveOfferTemplate.isActive,
        )
        # ... to fetch its venue...
        .joinedload(educational_models.CollectiveOfferTemplate.venue)
        .load_only(offerers_models.Venue.managingOffererId)
        # ... to fetch its managing offerer...
        .joinedload(offerers_models.Venue.managingOfferer)
        .load_only(offerers_models.Offerer.isActive, offerers_models.Offerer.validationStatus)
    )

    favorite_offer_templates = [
        favorite
        for favorite in favorite_offer_templates_query
        if favorite.collectiveOfferTemplate.is_eligible_for_search
    ]

    return len(favorite_offer_templates)
