import logging

import sqlalchemy as sa

from pcapi.core.external.compliance_backends import compliance_backend
from pcapi.core.offers import models as offers_models
from pcapi.domain import music_types
from pcapi.domain import show_types
from pcapi.models import db
from pcapi.tasks import compliance_tasks
from pcapi.tasks.serialization.compliance_tasks import GetComplianceScoreRequest


logger = logging.getLogger(__name__)


def update_offer_compliance_score(offer: offers_models.Offer, is_primary: bool) -> None:
    payload = _get_payload_for_compliance_api(offer)
    if is_primary:
        compliance_tasks.update_offer_compliance_score_primary_task.delay(payload)
    else:
        compliance_tasks.update_offer_compliance_score_secondary_task.delay(payload)


def make_update_offer_compliance_score(payload: GetComplianceScoreRequest) -> None:
    data_score, data_reasons = compliance_backend.get_score_from_compliance_api(payload)

    if data_score:
        offer = offers_models.Offer.query.with_for_update().filter_by(id=payload.offer_id).one_or_none()
        if offer is None:  # if offer is deleted before the task is run
            return
        offer.extraData = offer.extraData or {}
        offer.extraData["complianceScore"] = data_score
        offer.extraData["complianceReasons"] = data_reasons
        db.session.add(offer)
        db.session.commit()


def _get_payload_for_compliance_api(offer: offers_models.Offer) -> GetComplianceScoreRequest:
    extra_data = offer.extraData or {}
    rayon = extra_data.get("rayon")
    macro_rayon = (
        (
            offers_models.BookMacroSection.query.filter(sa.func.lower(offers_models.BookMacroSection.section) == rayon)
            .with_entities(offers_models.BookMacroSection.macroSection)
            .one_or_none()
        )
        if rayon
        else None
    )

    offer_type_label = None
    if show_type := extra_data.get("showType"):
        offer_type_label = show_types.SHOW_TYPES_LABEL_BY_CODE[int(show_type)]
    elif music_type := extra_data.get("musicType"):
        offer_type_label = music_types.MUSIC_TYPES_LABEL_BY_CODE[int(music_type)]

    offer_sub_type_label = None
    if show_sub_type := extra_data.get("showSubType"):
        offer_sub_type_label = show_types.SHOW_SUB_TYPES_LABEL_BY_CODE[int(show_sub_type)]
    elif music_sub_type := extra_data.get("musicSubType"):
        offer_sub_type_label = music_types.MUSIC_SUB_TYPES_LABEL_BY_CODE[int(music_sub_type)]

    payload = GetComplianceScoreRequest(
        offer_id=str(offer.id),
        offer_name=offer.name,
        offer_description=offer.description,
        offer_subcategoryid=offer.subcategoryId,
        rayon=rayon,
        macro_rayon=macro_rayon,
        stock_price=float(offer.max_price),
        thumb_url=offer.thumbUrl,
        offer_type_label=offer_type_label,
        offer_sub_type_label=offer_sub_type_label,
        author=extra_data.get("author"),
        performer=extra_data.get("performer"),
    )
    return payload
