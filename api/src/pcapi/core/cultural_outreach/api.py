import datetime
import functools
import logging

import sqlalchemy.exc as sa_exc
from sqlalchemy.dialects.postgresql import insert

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
            {"global": ["L'activité principale de la structure ne permet pas de déclarer une action de médiation"]}
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


def update_cultural_outreach_claim(
    claim_datetime: datetime.datetime | None,
    offer: offers_models.Offer,
) -> models.CulturalOutreach:
    _check_can_claim_cultural_outreach(offer)

    cultural_outreach = offer.culturalOutreach

    if cultural_outreach is None:
        raise CulturalOutreachException({"global": ["Aucune action de médiation n'a été déclarée pour cette offre"]})

    # we do not want to update the claim datetime if it is already set
    if cultural_outreach.claimedDatetime is not None and claim_datetime is not None:
        return cultural_outreach

    cultural_outreach.claimedDatetime = claim_datetime

    db.session.flush()

    on_commit(
        functools.partial(
            logger.info,
            "Update cultural outreach claim",
            extra={"offer_id": offer.id, "venue_id": offer.venueId, "claim_datetime": claim_datetime},
            technical_message_id="cultural_outreach.claim_updated",
        )
    )
    return cultural_outreach


def batch_qualify_cultural_outreach(offer_ids: list[int]) -> None:
    """
    This method will qualify cultural outreach as following
    - if the offer has a claimed cultural outreach, it will update the CulturalOutreachStatus to QUALIFIED
    - if the offer has no claimed cultural outreach yet, it will create a cultural outreach for
    this offer, with a None as claimedDatetime and a CulturalOutreachStatus set to QUALIFIED
    """
    values_to_update = [
        {
            "offerId": offer_id,
            "claimedDatetime": None,
            "status": models.CulturalOutreachStatus.QUALIFIED,
        }
        for offer_id in offer_ids
    ]
    stmt = insert(models.CulturalOutreach).values(values_to_update)

    upsert_stmt = stmt.on_conflict_do_update(
        index_elements=["offerId"],  # if offer already has a cultural outreach
        set_={"status": stmt.excluded.status},  # fallback to the excluded row's status (always QUALIFIED here)
    )

    db.session.execute(upsert_stmt)
    db.session.flush()


def batch_disqualify_cultural_outreach(offer_ids: list[int]) -> bool:
    """
    This method will disqualify cultural outreach as following
    - if the offer(s) has a claimed cultural outreach, it will update the CulturalOutreachStatus to DISQUALIFIED
    - if the offer(s) has no claimed cultural outreach, it will do nothing
    - returns False if no update have been made
    """
    count = (
        db.session.query(models.CulturalOutreach)
        .filter(models.CulturalOutreach.offerId.in_(offer_ids))
        .update(
            {"status": models.CulturalOutreachStatus.DISQUALIFIED},
            synchronize_session=False,
        )
    )
    db.session.flush()
    return bool(count)
