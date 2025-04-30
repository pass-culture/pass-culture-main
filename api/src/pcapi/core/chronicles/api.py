from datetime import datetime
import logging
from re import search

from dateutil.relativedelta import relativedelta
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.connectors import typeform
from pcapi.core.offers import models as offers_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.repository.session_management import atomic
from pcapi.repository.session_management import mark_transaction_as_invalid

from . import constants
from . import models


logger = logging.getLogger(__name__)

EMPTY_ANSWER = typeform.TypeformAnswer(field_id="")


def anonymize_unlinked_chronicles() -> None:
    db.session.query(models.Chronicle).filter(
        models.Chronicle.userId.is_(None),
        models.Chronicle.email != constants.ANONYMIZED_EMAIL,
        models.Chronicle.dateCreated < datetime.utcnow() - relativedelta(years=2),
    ).update({"email": constants.ANONYMIZED_EMAIL}, synchronize_session=False)


def import_book_club_chronicles() -> None:
    form_id = constants.BOOK_CLUB_FORM_ID
    for form in typeform.get_responses_generator(_get_last_chronicle_date, form_id):
        save_book_club_chronicle(form)


def _get_last_chronicle_date() -> datetime | None:
    return (
        db.session.query(models.Chronicle.dateCreated).order_by(models.Chronicle.dateCreated.desc()).limit(1).scalar()
    )


def _extract_book_club_ean(answer: typeform.TypeformAnswer) -> str | None:
    ean = None
    if not answer.choice_id:
        return None
    if answer.text and (match := search(pattern=r"(^|[^\d])([0-9]{13})([^\d]|$)", string=answer.text)):
        ean = match.group(2)
        return ean
    # Try to find the ean in db by its choice id.
    # This case could happen if the answer was deleted by an admin in typeform.
    ean = (
        db.session.query(models.Chronicle.ean)
        .filter(models.Chronicle.eanChoiceId == answer.choice_id)
        .limit(1)
        .scalar()
    )
    return ean


@atomic()
def save_book_club_chronicle(form: typeform.TypeformResponse) -> None:
    logger.info(
        "Import chronicle for book club: starting",
        extra={
            "response_id": form.response_id,
        },
    )
    answer_dict: dict = {}
    for answer in form.answers:
        answer_dict[answer.field_id] = answer

    try:
        age = int(answer_dict.get(constants.BookClub.AGE_ID.value, EMPTY_ANSWER).text)
    except (TypeError, ValueError):
        age = None

    is_identity_diffusible = (
        answer_dict.get(constants.BookClub.DIFFUSIBLE_PERSONAL_DATA_QUESTION_ID.value, EMPTY_ANSWER).choice_id
        == constants.BookClub.DIFFUSIBLE_PERSONAL_DATA_ANSWER_ID.value
    )
    is_social_media_diffusible = (
        answer_dict.get(constants.BookClub.SOCIAL_MEDIA_QUESTION_ID.value, EMPTY_ANSWER).choice_id
        == constants.BookClub.SOCIAL_MEDIA_ANSWER_ID.value
    )
    content = answer_dict.get(constants.BookClub.CHRONICLE_ID.value, EMPTY_ANSWER).text
    user_id = None
    if form.email:
        user_id = (
            db.session.query(
                users_models.User.id,
            )
            .filter(
                users_models.User.email == form.email,
            )
            .limit(1)
            .scalar()
        )

    ean = _extract_book_club_ean(answer_dict.get(constants.BookClub.BOOK_EAN_ID.value, EMPTY_ANSWER))
    ean_choice_id = answer_dict.get(constants.BookClub.BOOK_EAN_ID.value, EMPTY_ANSWER).choice_id

    products: list[offers_models.Product] = []
    if ean:
        products = db.session.query(offers_models.Product).filter(offers_models.Product.ean == ean).all()

    try:
        if all((content, ean, form.email)):
            chronicle = models.Chronicle(
                age=age,
                city=answer_dict.get(constants.BookClub.CITY_ID.value, EMPTY_ANSWER).text,
                content=content,
                dateCreated=form.date_submitted,
                ean=ean,
                eanChoiceId=ean_choice_id,
                email=form.email,
                firstName=answer_dict.get(constants.BookClub.NAME_ID.value, EMPTY_ANSWER).text,
                externalId=form.response_id,
                isIdentityDiffusible=is_identity_diffusible,
                isSocialMediaDiffusible=is_social_media_diffusible,
                products=products,  # type: ignore[arg-type]
                userId=user_id,
                isActive=False,
            )
            db.session.add(chronicle)
            db.session.flush()
            logger.info(
                "Import chronicle for book club: success",
                extra={
                    "response_id": form.response_id,
                },
            )
        else:
            logger.info(
                "Import chronicle for book club: ignored",
                extra={
                    "response_id": form.response_id,
                    "has_ean": bool(ean),
                    "has_content": bool(content),
                    "has_email": bool(form.email),
                },
            )
    except sa.exc.IntegrityError:
        # the chronicle is already in db
        mark_transaction_as_invalid()


def get_offer_published_chronicles(offer: offers_models.Offer) -> list[models.Chronicle]:
    if offer.productId:
        chronicles_query = (
            db.session.query(models.Chronicle)
            .join(models.Chronicle.products)
            .filter(offers_models.Product.id == offer.productId)
        )
    else:
        chronicles_query = (
            db.session.query(models.Chronicle).join(models.Chronicle.offers).filter(offers_models.Offer.id == offer.id)
        )

    return chronicles_query.filter(models.Chronicle.isPublished).order_by(models.Chronicle.id.desc()).all()
