from pcapi.core.educational import models as educational_models
from pcapi.repository import repository


def add_offer_to_favories_adage(
    uai: str,
    offerId: int,
) -> educational_models.AdageFavoriteOffer:
    favorite_offer = educational_models.AdageFavoriteOffer(educationalRedactor=uai, offerId=offerId)
    repository.save(favorite_offer)
    return favorite_offer


def add_offer_template_to_favories_adage(
    uai: str,
    offerId: int,
) -> educational_models.AdageFavoriteOffer:
    favorite_offer = educational_models.AdageFavoriteOfferTemplate(educationalRedactor=uai, offerTemplateId=offerId)
    repository.save(favorite_offer)
    return favorite_offer
