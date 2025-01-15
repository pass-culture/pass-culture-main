from datetime import datetime
import logging
from re import search
import typing

from dateutil.relativedelta import relativedelta
from sqlalchemy import orm as sa_orm

from pcapi.connectors import typeform
from pcapi.core.offers import models as offers_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.repository import atomic

from . import constants
from . import models


logger = logging.getLogger(__name__)

EMPTY_ANSWER = typeform.TypeformAnswer(field_id="")


def anonymize_unlinked_chronicles() -> None:
    models.Chronicle.query.filter(
        models.Chronicle.userId.is_(None),
        models.Chronicle.email != constants.ANONYMIZED_EMAIL,
        models.Chronicle.dateCreated < datetime.utcnow() - relativedelta(years=2),
    ).update({"email": constants.ANONYMIZED_EMAIL}, synchronize_session=False)


def import_book_club_chronicles() -> None:
    for form in _book_club_forms_generator():
        save_book_club_chronicle(form)


def _book_club_forms_generator() -> typing.Iterator[typeform.TypeformResponse]:
    previous_last_chronicle = object()
    while True:
        last_chronicle = models.Chronicle.query.order_by(models.Chronicle.dateCreated.desc()).first()

        if last_chronicle == previous_last_chronicle:
            logger.error(
                "Import chronicle for book club: error: infinite loop detected",
                extra={
                    "last_chronicle_id": last_chronicle.id if last_chronicle else None,
                },
            )
            break

        forms = typeform.get_responses(
            form_id=constants.BOOK_CLUB_FORM_ID,
            num_results=constants.IMPORT_CHUNK_SIZE,
            sort="submitted_at,asc",
            since=last_chronicle.dateCreated if last_chronicle else None,
        )
        yield from forms

        if len(forms) < constants.IMPORT_CHUNK_SIZE:
            break
        previous_last_chronicle = last_chronicle


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

    products: list[sa_orm.Mapped[offers_models.Product]] = []
    if ean:
        products = offers_models.Product.query.filter(offers_models.Product.extraData["ean"].astext == ean).all()

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
            formId=form.response_id,
            isIdentityDiffusible=is_identity_diffusible,
            isSocialMediaDiffusible=is_social_media_diffusible,
            products=products,
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
