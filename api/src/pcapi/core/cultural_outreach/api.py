import datetime
import functools
import logging

import sqlalchemy.exc as sa_exc

import pcapi.core.offers.models as offers_models
from pcapi.models import db
from pcapi.utils.transaction_manager import on_commit

from . import models
from .constants import CULTURAL_OUTREACH_ALLOWED_ACTIVITIES
from .constants import CULTURAL_OUTREACH_ALLOWED_VALIDATION_STATUSES
from .exceptions import CulturalOutreachException


logger = logging.getLogger(__name__)


def _check_can_claim_cultural_outreach(offer: offers_models.Offer) -> bool:
    if offer.venue.activity not in CULTURAL_OUTREACH_ALLOWED_ACTIVITIES:
        raise CulturalOutreachException(
            {"global": ["Le secteur d'activité de la structure ne permet pas de déclarer une action de médiation"]}
        )

    if offer.validation not in CULTURAL_OUTREACH_ALLOWED_VALIDATION_STATUSES:
        raise CulturalOutreachException(
            {"global": ["Le statut de l'offre ne permet pas de déclarer une action de médiation"]}
        )
    return True


def create_cultural_outreach_claim(
    offer: offers_models.Offer,
) -> models.CulturalOutreach:
    _check_can_claim_cultural_outreach(offer)

    cultural_outreach = models.CulturalOutreach(
        offer=offer,
        claimedDatetime=datetime.datetime.now(),
    )

    db.session.add(cultural_outreach)
    try:
        db.session.flush()
    except sa_exc.IntegrityError:
        raise CulturalOutreachException({"global": ["Une action de médiation a déjà été déclarée pour cette offre"]})

    on_commit(
        functools.partial(
            logger.info,
            "Create cultural outreach claim",
            extra={"offer_id": offer.id, "venue_id": offer.venueId},
            technical_message_id="cultural_outreach.claim_created",
        )
    )
    return cultural_outreach
