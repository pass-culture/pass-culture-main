import pcapi.core.educational.models as educational_models
from pcapi.models import db


def is_offer_a_redactor_favorite(offer_id: int, redactor_id: int) -> bool:
    query = educational_models.CollectiveOfferEducationalRedactor.query.filter_by(
        collectiveOfferId=offer_id,
        educationalRedactorId=redactor_id,
    )
    return db.session.query(query.exists()).scalar()


def is_offer_template_a_redactor_favorite(offer_id: int, redactor_id: int) -> bool:
    query = educational_models.CollectiveOfferTemplateEducationalRedactor.query.filter_by(
        collectiveOfferTemplateId=offer_id,
        educationalRedactorId=redactor_id,
    )
    return db.session.query(query.exists()).scalar()
