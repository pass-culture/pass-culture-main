import logging
import typing

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert

from pcapi import settings
from pcapi.core.categories.genres import music
from pcapi.core.categories.genres import show
from pcapi.core.external.compliance import serialization
from pcapi.core.external.compliance import tasks
from pcapi.core.external.compliance.backends.compliance import ComplianceBackend
from pcapi.core.external.compliance.backends.development import DevelopmentBackend
from pcapi.core.external.compliance.backends.test import TestBackend
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.utils.transaction_manager import is_managed_transaction


logger = logging.getLogger(__name__)


type Backend = ComplianceBackend | DevelopmentBackend | TestBackend

BACKEND_BY_KEY: typing.Final[dict[str, type[Backend]]] = {
    "ComplianceBackend": ComplianceBackend,
    "DevelopmentBackend": DevelopmentBackend,
    "TestBackend": TestBackend,
}

logger = logging.getLogger(__name__)


def _get_backend() -> Backend:
    return BACKEND_BY_KEY[settings.COMPLIANCE_BACKEND]()


def search_offers(payload: serialization.SearchOffersRequest) -> serialization.SearchOffersResponse | None:
    return _get_backend().search_offers(payload)


def update_offer_compliance_score(offer: offers_models.Offer, is_primary: bool) -> None:
    payload = _get_payload_for_compliance_api(offer)
    if is_primary:
        tasks.update_offer_compliance_score_primary_task.delay(payload.model_dump())
    else:
        tasks.update_offer_compliance_score_secondary_task.delay(payload.model_dump())


def make_update_offer_compliance_score(
    payload: serialization.UpdateOfferComplianceScorePayload,
) -> None:
    compliance_data = _get_backend().get_score_from_compliance_api(payload)

    if compliance_data and compliance_data.probability_validated is not None:
        offer = db.session.query(offers_models.Offer).with_for_update().filter_by(id=payload.offer_id).one_or_none()
        if offer is None:  # if offer is deleted before the task is run
            return

        values_to_update = {
            "compliance_score": compliance_data.probability_validated,
            "compliance_reasons": compliance_data.rejection_main_features,
            "validation_status_prediction": compliance_data.validation_status_prediction,
            "validation_status_prediction_reason": compliance_data.validation_status_prediction_reason,
        }
        statement = insert(offers_models.OfferCompliance).values(offerId=offer.id, **values_to_update)
        statement = statement.on_conflict_do_update(
            index_elements=["offerId"],  # Colonne causant le conflit
            set_=values_to_update,
        )

        db.session.execute(statement)

        if is_managed_transaction():
            db.session.flush()
        else:
            db.session.commit()


def _get_payload_for_compliance_api(offer: offers_models.Offer) -> serialization.UpdateOfferComplianceScorePayload:
    extra_data = offer.extraData or {}
    rayon = extra_data.get("rayon")
    macro_rayon = (
        (
            db.session.query(offers_models.BookMacroSection)
            .filter(sa.func.lower(offers_models.BookMacroSection.section) == rayon)
            .with_entities(offers_models.BookMacroSection.macroSection)
            .one_or_none()
        )
        if rayon
        else None
    )

    offer_type_label = None
    if show_type := extra_data.get("showType"):
        offer_type_label = show.SHOW_TYPES_LABEL_BY_CODE[int(show_type)]
    elif music_type := extra_data.get("musicType"):
        offer_type_label = music.MUSIC_TYPES_LABEL_BY_CODE[int(music_type)]

    offer_sub_type_label = None
    if show_sub_type := extra_data.get("showSubType"):
        offer_sub_type_label = show.SHOW_SUB_TYPES_LABEL_BY_CODE[int(show_sub_type)]
    elif music_sub_type := extra_data.get("musicSubType"):
        offer_sub_type_label = music.MUSIC_SUB_TYPES_LABEL_BY_CODE[int(music_sub_type)]

    return serialization.UpdateOfferComplianceScorePayload(
        offer_id=str(offer.id),
        offer_name=offer.name,
        offer_description=offer.description,
        offer_subcategory_id=offer.subcategoryId,
        rayon=rayon,
        macro_rayon=macro_rayon,
        stock_price=float(offer.max_price),
        image_url=offer.thumbUrl,
        offer_type_label=offer_type_label,
        offer_sub_type_label=offer_sub_type_label,
        author=extra_data.get("author"),
        performer=extra_data.get("performer"),
    )
