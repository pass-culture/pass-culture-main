from pcapi.core.educational import models as educational_models
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
