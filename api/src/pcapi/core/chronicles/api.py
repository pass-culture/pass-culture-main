import logging
import re
from datetime import datetime
from functools import partial
from re import search
from typing import Type

import sqlalchemy as sa
from dateutil.relativedelta import relativedelta

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
    get_last_chronicle_date = partial(_get_last_chronicle_date, models.ChronicleClubType.BOOK_CLUB)
    for form in typeform.get_responses_generator(get_last_chronicle_date, form_id):
        save_book_club_chronicle(form)


def import_cine_club_chronicles() -> None:
    form_id = constants.CINE_CLUB_FORM_ID
    get_last_chronicle_date = partial(_get_last_chronicle_date, models.ChronicleClubType.CINE_CLUB)
    for form in typeform.get_responses_generator(get_last_chronicle_date, form_id):
        save_cine_club_chronicle(form)


def _get_last_chronicle_date(club_type: models.ChronicleClubType) -> datetime | None:
    return (
        db.session.query(models.Chronicle.dateCreated)
        .filter(models.Chronicle.clubType == club_type)
        .order_by(models.Chronicle.dateCreated.desc())
        .limit(1)
        .scalar()
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
        db.session.query(models.Chronicle.productIdentifier)
        .filter(models.Chronicle.identifierChoiceId == answer.choice_id)
        .limit(1)
        .scalar()
    )
    return ean


def _extract_cine_club_movie_identifier(answer: typeform.TypeformAnswer) -> str | None:
    if not answer.choice_id:
        return None
    if answer.text:
        match = re.search(r"-\s+(\d+)", answer.text)
        if match:
            movie_id = match.group(1)
            return movie_id
    movie_id = (
        db.session.query(models.Chronicle.productIdentifier)
        .filter(models.Chronicle.identifierChoiceId == answer.choice_id)
        .limit(1)
        .scalar()
    )
    return movie_id


@atomic()
def save_chronicle(
    form: typeform.TypeformResponse,
    club_constants: Type[constants.BookClub] | Type[constants.CineClub],
    club_type: models.ChronicleClubType,
    chronicle_type_id: models.ChronicleProductIdentifierType,
) -> None:
    club_name = "Book Club" if club_constants == constants.BookClub else "Cine Club"

    if club_type == models.ChronicleClubType.BOOK_CLUB:
        product_identifier_field = constants.BookClub.BOOK_EAN_ID.value
    else:
        product_identifier_field = constants.CineClub.MOVIE_ID.value

    logger.info(
        "Import chronicle: starting",
        extra={
            "club_name": club_name,
            "response_id": form.response_id,
        },
    )
    answer_dict: dict = {}
    for answer in form.answers:
        answer_dict[answer.field_id] = answer

    age = None
    if hasattr(club_constants, "AGE_ID"):
        try:
            age = int(answer_dict.get(club_constants.AGE_ID.value, EMPTY_ANSWER).text)
        except (TypeError, ValueError):
            age = None

    is_identity_diffusible = (
        answer_dict.get(club_constants.DIFFUSIBLE_PERSONAL_DATA_QUESTION_ID.value, EMPTY_ANSWER).choice_id
        == club_constants.DIFFUSIBLE_PERSONAL_DATA_ANSWER_ID.value
    )
    is_social_media_diffusible = (
        answer_dict.get(club_constants.SOCIAL_MEDIA_QUESTION_ID.value, EMPTY_ANSWER).choice_id
        == club_constants.SOCIAL_MEDIA_ANSWER_ID.value
    )
    content = answer_dict.get(club_constants.CHRONICLE_ID.value, EMPTY_ANSWER).text
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

    product_choice_id = answer_dict.get(product_identifier_field, EMPTY_ANSWER).choice_id
    products: list[offers_models.Product] = []
    product_identifier = None
    if chronicle_type_id == models.ChronicleProductIdentifierType.EAN:
        product_identifier = _extract_book_club_ean(answer_dict.get(product_identifier_field, EMPTY_ANSWER))
        if product_identifier:
            products = (
                db.session.query(offers_models.Product).filter(offers_models.Product.ean == product_identifier).all()
            )
    elif chronicle_type_id == models.ChronicleProductIdentifierType.ALLOCINE_ID:
        product_identifier = _extract_cine_club_movie_identifier(
            answer_dict.get(product_identifier_field, EMPTY_ANSWER)
        )
        if product_identifier:
            products = (
                db.session.query(offers_models.Product)
                .filter(offers_models.Product.extraData["allocineId"].astext == product_identifier)
                .all()
            )

    try:
        city = None
        if hasattr(club_constants, "CITY_ID"):
            city = answer_dict.get(club_constants.CITY_ID.value, EMPTY_ANSWER).text

        if all((content, product_identifier, form.email)):
            chronicle = models.Chronicle(
                age=age,
                city=city,
                content=content,
                dateCreated=form.date_submitted,
                identifierChoiceId=product_choice_id,
                email=form.email,
                firstName=answer_dict.get(club_constants.NAME_ID.value, EMPTY_ANSWER).text,
                externalId=form.response_id,
                isIdentityDiffusible=is_identity_diffusible,
                isSocialMediaDiffusible=is_social_media_diffusible,
                products=products,
                userId=user_id,
                isActive=False,
                productIdentifierType=chronicle_type_id,
                productIdentifier=product_identifier,
                clubType=club_type,
            )
            db.session.add(chronicle)
            db.session.flush()
            logger.info(
                "Import chronicle: success",
                extra={
                    "club_name": club_name,
                    "response_id": form.response_id,
                },
            )
        else:
            logger.info(
                "Import chronicle: ignored",
                extra={
                    "club_name": club_name,
                    "response_id": form.response_id,
                    "has_product_identifier": bool(product_identifier),
                    "has_content": bool(content),
                    "has_email": bool(form.email),
                },
            )
    except sa.exc.IntegrityError:
        # the chronicle is already in db
        mark_transaction_as_invalid()


def save_book_club_chronicle(form: typeform.TypeformResponse) -> None:
    save_chronicle(
        form, constants.BookClub, models.ChronicleClubType.BOOK_CLUB, models.ChronicleProductIdentifierType.EAN
    )


def save_cine_club_chronicle(form: typeform.TypeformResponse) -> None:
    save_chronicle(
        form, constants.CineClub, models.ChronicleClubType.CINE_CLUB, models.ChronicleProductIdentifierType.ALLOCINE_ID
    )


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


def get_product_identifier(chronicle: models.Chronicle, product: offers_models.Product) -> str | None:
    match chronicle.productIdentifierType:
        case models.ChronicleProductIdentifierType.ALLOCINE_ID:
            return str(product.extraData.get("allocineId")) if product.extraData else None
        case models.ChronicleProductIdentifierType.EAN:
            return product.ean
        case models.ChronicleProductIdentifierType.VISA:
            return product.extraData.get("visa") if product.extraData else None
        case _:
            raise ValueError()
