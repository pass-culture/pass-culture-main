import datetime
from unittest.mock import patch

import pytest

from pcapi.connectors import typeform
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.operations import api as operations_api
from pcapi.core.operations import factories as operations_factories
from pcapi.core.operations import models as operations_models
from pcapi.core.users import factories as users_factories
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


class CreateSpecialEventFromTypeformTest:
    @patch(
        "pcapi.connectors.typeform.get_form",
        return_value=typeform.TypeformForm(
            form_id="test",
            title="Mon questionnaire",
            date_created=datetime.datetime.utcnow() - datetime.timedelta(days=3),
            fields=[
                typeform.TypeformQuestion(field_id="question1", title="Quel est ton prénom ?"),
                typeform.TypeformQuestion(field_id="question2", title="Que penses-tu de ce test ?"),
            ],
        ),
    )
    def test_create_special_event_from_typeform(self, mock_get_form):
        venue = offerers_factories.VenueFactory()
        event_date = datetime.date.today() + datetime.timedelta(days=15)

        special_event_id = operations_api.create_special_event_from_typeform(
            "test", event_date=event_date, venue_id=venue.id
        ).id

        special_event = db.session.query(operations_models.SpecialEvent).one()
        assert special_event.id == special_event_id
        assert special_event.externalId == "test"
        assert special_event.title == "Mon questionnaire"
        assert special_event.eventDate == event_date
        assert special_event.offererId == venue.managingOffererId
        assert special_event.venueId == venue.id

        questions = (
            db.session.query(operations_models.SpecialEventQuestion)
            .order_by(operations_models.SpecialEventQuestion.externalId)
            .all()
        )
        assert len(questions) == 2
        assert questions[0].externalId == "question1"
        assert questions[0].title == "Quel est ton prénom ?"
        assert questions[1].externalId == "question2"
        assert questions[1].title == "Que penses-tu de ce test ?"

    def test_check_offerer_and_venue_consistency(self):
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory()

        with pytest.raises(ValueError) as err:
            operations_api.create_special_event_from_typeform(
                "test",
                event_date=datetime.date.today(),
                offerer_id=offerer.id,
                venue_id=venue.id,
            )
        assert "n'appartient pas à la structure" in str(err.value)

    def test_check_offerer_exists(self):
        with pytest.raises(ValueError) as err:
            operations_api.create_special_event_from_typeform(
                "test",
                event_date=datetime.date.today(),
                offerer_id=999999,
            )
        assert "n'existe pas" in str(err.value)

    def test_check_venue_exists(self):
        with pytest.raises(ValueError) as err:
            operations_api.create_special_event_from_typeform(
                "test",
                event_date=datetime.date.today(),
                venue_id=999999,
            )
        assert "n'existe pas" in str(err.value)


class UpdateFormTitleFromTypeformTest:
    def test_update_title(self):
        expected_title = "new_title"
        event = operations_factories.SpecialEventFactory()
        form = typeform.TypeformForm(
            form_id=event.externalId,
            title=expected_title,
            date_created=datetime.datetime(2020, 1, 1),
            fields=[],
        )

        operations_api.update_form_title_from_typeform(event_id=event.id, event_title=event.title, form=form)

        db.session.refresh(event)
        assert event.title == expected_title


class UpdateFormQuestionsFromTypeformTest:
    def test_update_question_title(self):
        event = operations_factories.SpecialEventFactory()
        question = operations_factories.SpecialEventQuestionFactory(
            event=event,
            title="old_title",
        )
        untouched_question = operations_factories.SpecialEventQuestionFactory(event=event, title="still title")

        form = typeform.TypeformForm(
            form_id=event.externalId,
            title="Questions on plouf",
            date_created=datetime.datetime(2020, 1, 1),
            fields=[
                typeform.TypeformQuestion(
                    field_id=question.externalId,
                    title="How many plouf do you need to build a tower ?",
                ),
                typeform.TypeformQuestion(
                    field_id=untouched_question.externalId,
                    title=untouched_question.title,
                ),
            ],
        )

        result = operations_api.update_form_questions_from_typeform(event_id=event.id, form=form)

        db.session.refresh(question)
        db.session.refresh(untouched_question)

        assert untouched_question.title == "still title"
        assert question.title == form.fields[0].title
        assert result == {
            question.externalId: question.id,
            untouched_question.externalId: untouched_question.id,
        }

    def test_create_new_question(self):
        event = operations_factories.SpecialEventFactory()
        question = operations_factories.SpecialEventQuestionFactory(
            event=event,
        )
        form = typeform.TypeformForm(
            form_id=event.externalId,
            title="Questions on plouf",
            date_created=datetime.datetime(2020, 1, 1),
            fields=[
                typeform.TypeformQuestion(
                    field_id="qwerty123",
                    title="How much does a plouf weight ?",
                ),
            ],
        )

        result = operations_api.update_form_questions_from_typeform(event_id=event.id, form=form)

        db.session.refresh(question)
        assert db.session.query(operations_models.SpecialEventQuestion).count() == 2
        new_question = (
            db.session.query(operations_models.SpecialEventQuestion)
            .filter(operations_models.SpecialEventQuestion.externalId == "qwerty123")
            .one()
        )
        assert new_question.title == form.fields[0].title
        assert new_question.eventId == event.id
        assert result == {
            question.externalId: question.id,
            new_question.externalId: new_question.id,
        }

    def test_complete_list_of_questions(self):
        event = operations_factories.SpecialEventFactory()
        question = operations_factories.SpecialEventQuestionFactory(
            event=event,
        )
        form = typeform.TypeformForm(
            form_id=event.externalId,
            title="Questions on plouf",
            date_created=datetime.datetime(2020, 1, 1),
            fields=[
                typeform.TypeformQuestion(
                    field_id="qwerty123",
                    title="How much does a plouf weight ?",
                ),
            ],
        )

        result = operations_api.update_form_questions_from_typeform(event_id=event.id, form=form)

        db.session.refresh(question)
        new_question = (
            db.session.query(operations_models.SpecialEventQuestion)
            .filter(operations_models.SpecialEventQuestion.externalId == "qwerty123")
            .one()
        )
        assert result == {
            question.externalId: question.id,
            new_question.externalId: new_question.id,
        }


class SaveResponseTest:
    def test_nominal(self):
        user = users_factories.UserFactory(
            email="valid.email@example.com",
        )
        event = operations_factories.SpecialEventFactory()
        question1 = operations_factories.SpecialEventQuestionFactory(
            event=event,
        )
        question2 = operations_factories.SpecialEventQuestionFactory(
            event=event,
        )
        questions = {
            question1.externalId: question1.id,
            question2.externalId: question2.id,
        }
        form = typeform.TypeformResponse(
            response_id="qwerty123",
            date_submitted=datetime.datetime(2020, 1, 1),
            phone_number="0123456789",
            email="valid.email@example.com",
            answers=[
                typeform.TypeformAnswer(
                    field_id=question1.externalId,
                    choice_id=None,
                    text="text1",
                ),
                typeform.TypeformAnswer(
                    field_id=question2.externalId,
                    choice_id=None,
                    text="text2",
                ),
            ],
        )

        operations_api.save_response(event_id=event.id, form=form, questions=questions)

        response = db.session.query(operations_models.SpecialEventResponse).one()
        answers = db.session.query(operations_models.SpecialEventAnswer).order_by("text").all()

        assert response.eventId == event.id
        assert response.externalId == form.response_id
        assert response.dateSubmitted == form.date_submitted
        assert response.phoneNumber == form.phone_number
        assert response.email == form.email
        assert response.status == operations_models.SpecialEventResponseStatus.NEW
        assert response.user == user

        assert len(answers) == 2
        assert answers[0].responseId == response.id
        assert answers[0].questionId == question1.id
        assert answers[0].text == "text1"

        assert answers[1].responseId == response.id
        assert answers[1].questionId == question2.id
        assert answers[1].text == "text2"

    def test_response_already_exists(self):
        question = operations_factories.SpecialEventQuestionFactory()
        questions = {question.externalId: question.id}
        response = operations_factories.SpecialEventResponseFactory()

        form = typeform.TypeformResponse(
            response_id=response.externalId,
            date_submitted=datetime.datetime(2020, 1, 1),
            phone_number="0123456789",
            email="valid.email@example.com",
            answers=[
                typeform.TypeformAnswer(
                    field_id=question.externalId,
                    choice_id=None,
                    text="text1",
                ),
            ],
        )

        operations_api.save_response(event_id=question.event.id, form=form, questions=questions)

        assert db.session.query(operations_models.SpecialEventResponse).count() == 1
        assert db.session.query(operations_models.SpecialEventAnswer).count() == 0

    def test_question_does_not_exist(self):
        question = operations_factories.SpecialEventQuestionFactory()
        questions = {question.externalId: question.id}
        form = typeform.TypeformResponse(
            response_id="qwerty123",
            date_submitted=datetime.datetime(2020, 1, 1),
            phone_number="0123456789",
            email="valid.email@example.com",
            answers=[
                typeform.TypeformAnswer(
                    field_id=question.externalId,
                    choice_id=None,
                    text="text1",
                ),
                typeform.TypeformAnswer(
                    field_id="field_id",
                    choice_id=None,
                    text="text2",
                ),
            ],
        )

        operations_api.save_response(event_id=question.event.id, form=form, questions=questions)

        response = db.session.query(operations_models.SpecialEventResponse).one()
        answer = db.session.query(operations_models.SpecialEventAnswer).one()

        assert response.eventId == question.event.id
        assert response.externalId == form.response_id
        assert response.dateSubmitted == form.date_submitted
        assert response.phoneNumber == form.phone_number
        assert response.email == form.email
        assert response.status == operations_models.SpecialEventResponseStatus.NEW

        assert answer.responseId == response.id
        assert answer.questionId == question.id
        assert answer.text == "text1"

    def test_ignore_answer_without_text(self):
        question = operations_factories.SpecialEventQuestionFactory()
        questions = {question.externalId: question.id}
        form = typeform.TypeformResponse(
            response_id="qwerty123",
            date_submitted=datetime.datetime(2020, 1, 1),
            phone_number="0123456789",
            email="valid.email@example.com",
            answers=[
                typeform.TypeformAnswer(
                    field_id=question.externalId,
                    choice_id=None,
                    text="text1",
                ),
                typeform.TypeformAnswer(
                    field_id="field_id",
                    choice_id="123",
                    text=None,
                ),
            ],
        )

        operations_api.save_response(event_id=question.event.id, form=form, questions=questions)

        assert db.session.query(operations_models.SpecialEventResponse).count() == 1
        assert db.session.query(operations_models.SpecialEventAnswer).count() == 1


class GetUserForFormTest:
    def test_no_user_match(self):
        form = typeform.TypeformResponse(
            response_id="qwerty123",
            date_submitted=datetime.datetime(2020, 1, 1),
            phone_number="0123456789",
            email="valid.email@example.com",
            answers=[],
        )
        result = operations_api._get_user_for_form(form=form)

        assert result is None

    def test_email_match(self):
        form = typeform.TypeformResponse(
            response_id="qwerty123",
            date_submitted=datetime.datetime(2020, 1, 1),
            phone_number="0123456789",
            email="valid.email@example.com",
            answers=[],
        )
        user = users_factories.UserFactory(email="valid.email@example.com")
        result = operations_api._get_user_for_form(form=form)

        assert result == user

    def test_phone_match(self):
        user = users_factories.BeneficiaryFactory()
        form = typeform.TypeformResponse(
            response_id="qwerty123",
            date_submitted=datetime.datetime(2020, 1, 1),
            phone_number=user.phoneNumber.replace("+33", "0"),
            email="valid.email@example.com",
            answers=[],
        )
        result = operations_api._get_user_for_form(form=form)

        assert result == user

    def test_invalid_phone_number(self):
        form = typeform.TypeformResponse(
            response_id="qwerty123",
            date_submitted=datetime.datetime(2020, 1, 1),
            phone_number="plouf",
            email="valid.email@example.com",
            answers=[],
        )
        result = operations_api._get_user_for_form(form=form)

        assert result == None

    def test_multiple_phone_matches(self):
        form = typeform.TypeformResponse(
            response_id="qwerty123",
            date_submitted=datetime.datetime(2020, 1, 1),
            phone_number="0123456789",
            email="valid.email@example.com",
            answers=[],
        )
        user = users_factories.BeneficiaryFactory()
        users_factories.UserFactory(_phoneNumber=user.phoneNumber)
        users_factories.UserFactory(_phoneNumber=user.phoneNumber)
        result = operations_api._get_user_for_form(form=form)

        assert result is None

    def test_phone_and_email_matches(self):
        form = typeform.TypeformResponse(
            response_id="qwerty123",
            date_submitted=datetime.datetime(2020, 1, 1),
            phone_number="0123456789",
            email="valid.email@example.com",
            answers=[],
        )
        user = users_factories.UserFactory(
            email="valid.email@example.com",
        )
        users_factories.UserFactory(_phoneNumber="+33123456789")
        users_factories.UserFactory(_phoneNumber="+33123456789")
        result = operations_api._get_user_for_form(form=form)

        assert result == user


class RejectResponseOnExpiredOperationTest:
    def test_selected_offer(self):
        event = operations_factories.SpecialEventFactory(
            eventDate=datetime.datetime.utcnow() - datetime.timedelta(days=8),
        )
        operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.NEW,
        )
        operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.VALIDATED,
        )
        operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.REJECTED,
        )
        operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.PRESELECTED,
        )

        operations_api.reject_response_on_expired_operation()

        responses = (
            db.session.query(operations_models.SpecialEventResponse)
            .filter(
                operations_models.SpecialEventResponse.event == event,
            )
            .order_by(
                operations_models.SpecialEventResponse.id,
            )
            .all()
        )

        assert responses[0].status == operations_models.SpecialEventResponseStatus.REJECTED
        assert responses[1].status == operations_models.SpecialEventResponseStatus.VALIDATED
        assert responses[2].status == operations_models.SpecialEventResponseStatus.REJECTED
        assert responses[3].status == operations_models.SpecialEventResponseStatus.PRESELECTED

    def test_ignore_newer_operations(self):
        event = operations_factories.SpecialEventFactory(
            eventDate=datetime.datetime.utcnow() - datetime.timedelta(days=6),
        )
        operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.NEW,
        )
        operations_api.reject_response_on_expired_operation()

        response = (
            db.session.query(operations_models.SpecialEventResponse)
            .filter(
                operations_models.SpecialEventResponse.event == event,
            )
            .order_by(
                operations_models.SpecialEventResponse.id,
            )
            .one()
        )

        assert response.status == operations_models.SpecialEventResponseStatus.NEW

    def test_ignore_older_operations(self):
        event = operations_factories.SpecialEventFactory(
            eventDate=datetime.datetime.utcnow() - datetime.timedelta(days=11),
        )
        operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.NEW,
        )
        operations_api.reject_response_on_expired_operation()

        response = (
            db.session.query(operations_models.SpecialEventResponse)
            .filter(
                operations_models.SpecialEventResponse.event == event,
            )
            .order_by(
                operations_models.SpecialEventResponse.id,
            )
            .one()
        )

        assert response.status == operations_models.SpecialEventResponseStatus.NEW
