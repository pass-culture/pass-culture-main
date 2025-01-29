import datetime
import logging

import sqlalchemy as sa

from pcapi.connectors import typeform
from pcapi.core.offerers import models as offerers_models
from pcapi.core.subscription.phone_validation.exceptions import InvalidPhoneNumber
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.repository import atomic
from pcapi.repository import mark_transaction_as_invalid
from pcapi.utils.phone_number import ParsedPhoneNumber

from . import models


logger = logging.getLogger(__name__)


def create_special_event_from_typeform(
    form_id: str,
    *,
    event_date: datetime.date,
    offerer_id: int | None = None,
    venue_id: int | None = None,
) -> models.SpecialEvent:
    if venue_id:
        venue = offerers_models.Venue.query.filter_by(id=venue_id).one_or_none()
        if not venue:
            raise ValueError(f"Le lieu {venue_id} n'existe pas")
        if offerer_id and offerer_id != venue.managingOffererId:
            raise ValueError(f"Le lieu {venue_id} n'appartient pas à la structure {offerer_id}")
        if not offerer_id:
            offerer_id = venue.managingOffererId
    elif offerer_id:
        offerer = offerers_models.Venue.query.filter_by(id=venue_id).one_or_none()
        if not offerer:
            raise ValueError(f"La structure {offerer_id} n'existe pas")

    data = typeform.get_form(form_id)

    special_event = models.SpecialEvent(
        externalId=data.form_id,
        title=data.title,
        eventDate=event_date,
        offererId=offerer_id,
        venueId=venue_id,
    )
    db.session.add(special_event)
    db.session.flush()

    for field in data.fields:
        db.session.add(
            models.SpecialEventQuestion(eventId=special_event.id, externalId=field.field_id, title=field.title)
        )

    db.session.flush()

    return special_event


@atomic()
def reject_response_on_expired_operation() -> None:
    models.SpecialEventResponse.query.filter(
        models.SpecialEventResponse.eventId.in_(
            models.SpecialEvent.query.filter(
                models.SpecialEvent.eventDate < datetime.date.today() - datetime.timedelta(days=7),
                models.SpecialEvent.eventDate > datetime.date.today() - datetime.timedelta(days=10),
            ).with_entities(models.SpecialEvent.id),
        ),
        models.SpecialEventResponse.status == models.SpecialEventResponseStatus.NEW,
    ).update(
        {
            "status": models.SpecialEventResponseStatus.REJECTED,
        },
        synchronize_session=False,
    )


def retrieve_data_from_typeform() -> None:
    events = models.SpecialEvent.query.filter(
        models.SpecialEvent.eventDate >= datetime.date.today() - datetime.timedelta(days=7),
    )
    for event in events:
        try:
            form = typeform.get_form(form_id=event.externalId)
            update_form_title_from_typeform(event=event, form=form)
            questions = update_form_questions_from_typeform(event=event, form=form)
            download_responses_from_typeform(event=event, questions=questions)
        except Exception as exc:  # pylint: disable=broad-except
            logger.error(
                "An error happened while retrieving special event",
                extra={
                    "event_id": event.id,
                    "exc": str(exc),
                    "external_id": event.externalId,
                },
            )


@atomic()
def update_form_title_from_typeform(event: models.SpecialEvent, form: typeform.TypeformForm) -> None:
    if form.title != event.title:
        event.title = form.title
        db.session.add(event)
        db.session.flush()


@atomic()
def update_form_questions_from_typeform(
    event: models.SpecialEvent, form: typeform.TypeformForm
) -> dict[str, models.SpecialEventQuestion]:
    old_questions = models.SpecialEventQuestion.query.filter(models.SpecialEventQuestion.eventId == event.id).all()

    questions = {q.externalId: q for q in old_questions}

    for question in form.fields:
        if question.field_id not in questions:
            questions[question.field_id] = models.SpecialEventQuestion(
                eventId=event.id, externalId=question.field_id, title=question.title
            )
            db.session.add(questions[question.field_id])
            db.session.flush()
        elif question.title != questions[question.field_id].title:
            questions[question.field_id].title = question.title
            db.session.add(questions[question.field_id])
            db.session.flush()
    return questions


def download_responses_from_typeform(
    event: models.SpecialEvent, questions: dict[str, models.SpecialEventQuestion]
) -> None:

    def get_last_date_for_event() -> datetime.datetime | None:
        result = (
            models.SpecialEventResponse.query.with_entities(models.SpecialEventResponse.dateSubmitted)
            .filter(models.SpecialEventResponse.eventId == event.id)
            .order_by(models.SpecialEventResponse.dateSubmitted.desc())
            .limit(1)
            .scalar()
        )
        return result

    for response in typeform.get_responses_generator(get_last_date_for_event, event.externalId):
        save_response(
            event=event,
            form=response,
            questions=questions,
        )


from contextlib import suppress


def _get_user_for_form(form: typeform.TypeformResponse) -> users_models.User | None:
    user = None
    if form.email:
        user = users_models.User.query.filter(users_models.User.email == form.email).one_or_none()
    if form.phone_number and not user:
        with suppress(InvalidPhoneNumber):
            parsed_phone_number = ParsedPhoneNumber(form.phone_number)
            with suppress(sa.exc.MultipleResultsFound):
                user = (
                    users_models.User.query.filter(
                        users_models.User._phoneNumber == parsed_phone_number.phone_number,
                    )
                    .limit(2)
                    .one_or_none()
                )
    return user


@atomic()
def save_response(
    event: models.SpecialEvent, form: typeform.TypeformResponse, questions: dict[str, models.SpecialEventQuestion]
) -> None:
    try:
        response = models.SpecialEventResponse(
            eventId=event.id,
            externalId=form.response_id,
            dateSubmitted=form.date_submitted,
            phoneNumber=form.phone_number,
            email=form.email,
            user=_get_user_for_form(form),
        )
        db.session.add(response)
        db.session.flush()
    except sa.exc.IntegrityError:
        mark_transaction_as_invalid()
        return

    for answer in form.answers:
        if answer.field_id not in questions:
            continue
        if answer.text is not None:
            db.session.add(
                models.SpecialEventAnswer(
                    responseId=response.id,
                    questionId=questions[answer.field_id].id,
                    text=answer.text,
                )
            )
    db.session.flush()
