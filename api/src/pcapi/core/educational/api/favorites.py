import sqlalchemy.orm as sa_orm

from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


def get_redactor_favorites_count(redactor_id: int) -> int:
    """
    Note: Non-eligible for search templates are ignored.
    """
    # TODO(jeremieb): make CollectiveOfferTemplate's is_eligible_for_search
    # a hybrid_property to allow filtering (not sure this is possible however)
    # lots of joinedload because of is_eligible_for_search
    redactor = (
        db.session.query(educational_models.EducationalRedactor)
        .filter_by(id=redactor_id)
        .options(
            sa_orm.joinedload(educational_models.EducationalRedactor.favoriteCollectiveOfferTemplates)
            .load_only(
                educational_models.CollectiveOfferTemplate.id,
                educational_models.CollectiveOfferTemplate.venueId,
                educational_models.CollectiveOfferTemplate.validation,
                educational_models.CollectiveOfferTemplate.isActive,
            )
            .joinedload(educational_models.CollectiveOfferTemplate.venue)
            .load_only(
                offerers_models.Venue.managingOffererId,
                offerers_models.Venue.isVirtual,
            )
            .joinedload(offerers_models.Venue.managingOfferer)
            .load_only(offerers_models.Offerer.isActive, offerers_models.Offerer.validationStatus)
        )
        .one()
    )

    favorite_offer_templates = [
        template for template in redactor.favoriteCollectiveOfferTemplates if template.is_eligible_for_search
    ]

    return len(favorite_offer_templates)
