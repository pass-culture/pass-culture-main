from contextlib import suppress
import datetime
from functools import partial
import logging
from traceback import format_exc

import sqlalchemy as sa

from pcapi.connectors import typeform
from pcapi.core.offerers import models as offerers_models
from pcapi.core.subscription.phone_validation.exceptions import InvalidPhoneNumber
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.repository.session_management import atomic
from pcapi.repository.session_management import mark_transaction_as_invalid
from pcapi.repository.session_management import on_commit
from pcapi.utils.phone_number import ParsedPhoneNumber
from pcapi.workers.operations_jobs import retrieve_special_event_from_typeform_job

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
        venue = db.session.query(offerers_models.Venue).filter_by(id=venue_id).one_or_none()
        if not venue:
            raise ValueError(f"Le lieu {venue_id} n'existe pas")
        if offerer_id and offerer_id != venue.managingOffererId:
            raise ValueError(f"Le lieu {venue_id} n'appartient pas à la structure {offerer_id}")
        if not offerer_id:
            offerer_id = venue.managingOffererId
    elif offerer_id:
        offerer = db.session.query(offerers_models.Venue).filter_by(id=venue_id).one_or_none()
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

    on_commit(partial(retrieve_special_event_from_typeform_job.delay, special_event.id))
    return special_event


@atomic()
def reject_response_on_expired_operation() -> None:
    db.session.query(models.SpecialEventResponse).filter(
        models.SpecialEventResponse.eventId.in_(
            db.session.query(models.SpecialEvent)
            .filter(
                models.SpecialEvent.eventDate < datetime.date.today() - datetime.timedelta(days=7),
                # limit to 10 days to avoid checking all events until the end of time.
                models.SpecialEvent.eventDate >= datetime.date.today() - datetime.timedelta(days=10),
            )
            .with_entities(models.SpecialEvent.id),
        ),
        models.SpecialEventResponse.status == models.SpecialEventResponseStatus.NEW,
    ).update(
        {
            "status": models.SpecialEventResponseStatus.REJECTED,
        },
        synchronize_session=False,
    )


def retrieve_data_from_typeform() -> None:
    events = db.session.query(models.SpecialEvent).filter(
        models.SpecialEvent.eventDate >= datetime.date.today() - datetime.timedelta(days=7),
    )
    for event in events:
        retrieve_special_event_from_typeform(event)


def retrieve_special_event_from_typeform(event: models.SpecialEvent) -> None:
    try:
        event_id = event.id
        event_external_id = event.externalId
        form = typeform.get_form(form_id=event_external_id)
        update_form_title_from_typeform(event_id=event_id, event_title=event.title, form=form)
        questions = update_form_questions_from_typeform(event_id=event_id, form=form)
        download_responses_from_typeform(event_id=event_id, event_external_id=event_external_id, questions=questions)
    except typeform.NotFoundException:
        # form does no longer exist, ignore
        pass
    except Exception:  # pylint: disable=broad-except
        logger.error(
            "An error happened while retrieving special event",
            extra={
                "event_id": event.id,
                "exc": format_exc(),
                "external_id": event.externalId,
            },
        )


@atomic()
def update_form_title_from_typeform(event_id: int, event_title: str, form: typeform.TypeformForm) -> None:
    if form.title != event_title:
        db.session.query(models.SpecialEvent).filter(models.SpecialEvent.id == event_id).update(
            {
                "title": form.title,
            },
            synchronize_session=False,
        )


@atomic()
def update_form_questions_from_typeform(event_id: int, form: typeform.TypeformForm) -> dict[str, int]:
    old_questions = (
        db.session.query(models.SpecialEventQuestion).filter(models.SpecialEventQuestion.eventId == event_id).all()
    )

    questions = {q.externalId: q for q in old_questions}

    for question in form.fields:
        if question.field_id not in questions:
            questions[question.field_id] = models.SpecialEventQuestion(
                eventId=event_id, externalId=question.field_id, title=question.title
            )
            db.session.add(questions[question.field_id])
        elif question.title != questions[question.field_id].title:
            questions[question.field_id].title = question.title
            db.session.add(questions[question.field_id])
    db.session.flush()
    return {q.externalId: q.id for q in questions.values()}


def download_responses_from_typeform(event_id: int, event_external_id: str, questions: dict[str, int]) -> None:
    def get_last_date_for_event() -> datetime.datetime | None:
        result = (
            db.session.query(models.SpecialEventResponse)
            .with_entities(models.SpecialEventResponse.dateSubmitted)
            .filter(models.SpecialEventResponse.eventId == event_id)
            .order_by(models.SpecialEventResponse.dateSubmitted.desc())
            .limit(1)
            .scalar()
        )
        return result

    for response in typeform.get_responses_generator(get_last_date_for_event, event_external_id):
        save_response(
            event_id=event_id,
            form=response,
            questions=questions,
        )


def _get_user_for_form(form: typeform.TypeformResponse) -> users_models.User | None:
    user = None
    if form.email:
        user = db.session.query(users_models.User).filter(users_models.User.email == form.email).one_or_none()
    if form.phone_number and not user:
        with suppress(InvalidPhoneNumber):
            parsed_phone_number = ParsedPhoneNumber(form.phone_number)
            with suppress(sa.exc.MultipleResultsFound):
                user = (
                    db.session.query(users_models.User)
                    .filter(
                        users_models.User._phoneNumber == parsed_phone_number.phone_number,
                    )
                    .limit(2)
                    .one_or_none()
                )
    return user


@atomic()
def save_response(event_id: int, form: typeform.TypeformResponse, questions: dict[str, int]) -> None:
    try:
        response = models.SpecialEventResponse(
            eventId=event_id,
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
                    questionId=questions[answer.field_id],
                    text=answer.text,
                )
            )
    db.session.flush()
