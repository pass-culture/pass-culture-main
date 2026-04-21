import pcapi.core.offerers.models as offerers_models
from pcapi.models import offer_mixin


CULTURAL_OUTREACH_ALLOWED_ACTIVITIES = {
    offerers_models.Activity.PRODUCTION_OR_PROMOTION_COMPANY,
    offerers_models.Activity.ARTISTIC_COMPANY,
    offerers_models.Activity.PERFORMANCE_HALL,
    offerers_models.Activity.MUSEUM,
    offerers_models.Activity.HERITAGE_SITE,
    offerers_models.Activity.LIBRARY,
    offerers_models.Activity.CULTURAL_MEDIATION,
}

CULTURAL_OUTREACH_ALLOWED_VALIDATION_STATUSES = {
    offer_mixin.OfferValidationStatus.DRAFT,
    offer_mixin.OfferValidationStatus.APPROVED,
}
