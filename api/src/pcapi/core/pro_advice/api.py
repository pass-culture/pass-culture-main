import logging

import pcapi.core.offers.models as models
import pcapi.core.users.models as users_models
import pcapi.utils.date as date_utils
from pcapi.core.pro_advice.exceptions import ProAdviceException
from pcapi.models import db


logger = logging.getLogger(__name__)


def create_pro_advice(
    offer: models.Offer,
    content: str,
    author: str | None,
    current_user: users_models.User,
) -> models.ProAdvice:
    if offer.validation != models.OfferValidationStatus.APPROVED:
        raise ProAdviceException({"global": ["Impossible de créer une recommandation sur cette offre"]})

    if offer.proAdvice is not None:
        raise ProAdviceException({"global": ["Une recommandation existe déjà pour cette offre"]})

    pro_advice = models.ProAdvice(
        offerId=offer.id,
        venueId=offer.venueId,
        content=content,
        author=author,
        updatedAt=date_utils.get_naive_utc_now(),
    )

    db.session.add(pro_advice)
    db.session.flush()

    logger.info(
        "Pro advice created",
        extra={"offer_id": offer.id, "venue_id": offer.venueId, "user_id": current_user.id},
        technical_message_id="pro_advice.created",
    )
    return pro_advice


def update_pro_advice(
    offer: models.Offer,
    content: str,
    author: str | None,
    current_user: users_models.User,
) -> models.ProAdvice:
    if offer.validation != models.OfferValidationStatus.APPROVED:
        raise ProAdviceException({"global": ["Impossible de modifier une recommandation sur cette offre"]})

    if offer.proAdvice is None:
        raise ProAdviceException({"global": ["Aucune recommandation n'existe pour cette offre"]})

    pro_advice = offer.proAdvice
    pro_advice.content = content
    pro_advice.author = author
    pro_advice.updatedAt = date_utils.get_naive_utc_now()

    db.session.flush()

    logger.info(
        "Pro advice updated",
        extra={"offer_id": pro_advice.offerId, "venue_id": offer.venueId, "user_id": current_user.id},
        technical_message_id="pro_advice.updated",
    )
    return pro_advice
