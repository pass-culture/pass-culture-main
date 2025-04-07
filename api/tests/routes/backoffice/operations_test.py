import datetime
from unittest.mock import patch

from flask import url_for
import pytest

from pcapi.connectors import typeform
from pcapi.core.finance import models as finance_models
from pcapi.core.operations import factories as operations_factories
from pcapi.core.operations import models as operations_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.routes.backoffice.filters import format_date

from .helpers import button as button_helpers
from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


@pytest.fixture(name="special_events")
def special_events_fixture() -> list[operations_models.SpecialEvent]:
    return [
        operations_factories.SpecialEventFactory(externalId="abCd1234", title="Première opération spéciale"),
        operations_factories.SpecialEventFactory(externalId="eFgh5678", title="Jeu concours"),
    ]


class ListEventsTest(GetEndpointHelper):
    endpoint = "backoffice_web.operations.list_events"
    needed_permission = perm_models.Permissions.READ_SPECIAL_EVENTS

    # authenticated user + user session + list of special events + count
    expected_num_queries = 4

    def test_list_events(self, authenticated_client, special_events):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        assert rows[0]["Id. Typeform"] == "eFgh5678"
        assert rows[0]["Titre"] == "Jeu concours"
        assert rows[1]["Id. Typeform"] == "abCd1234"
        assert rows[1]["Titre"] == "Première opération spéciale"

    def test_list_events_filtered_by_external_id(self, authenticated_client, special_events):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="abCd1234"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["Id. Typeform"] == "abCd1234"
        assert rows[0]["Titre"] == "Première opération spéciale"

    def test_list_events_filtered_by_title(self, authenticated_client, special_events):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="concours"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["Id. Typeform"] == "eFgh5678"
        assert rows[0]["Titre"] == "Jeu concours"


class CreateEventButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.MANAGE_SPECIAL_EVENTS
    button_label = "Importer une opération spéciale"

    @property
    def path(self):
        return url_for("backoffice_web.operations.list_events")


class CreateEventTest(PostEndpointHelper):
    endpoint = "backoffice_web.operations.create_event"
    needed_permission = perm_models.Permissions.MANAGE_SPECIAL_EVENTS

    # - authenticated user
    # - user session
    # - insert into special_event or rollback
    expected_num_queries = 3
    # - get special event
    # - get special event questions
    # - insert into special_event_questions
    # - reload responses for special event
    # - fail to retrieve the user by email
    # - fail to retrieve the user by phone number
    # - insert response
    # - insert answers
    expected_num_queries_with_job = expected_num_queries + 8

    def test_create_event(self, authenticated_client):
        # Data come from TestingBackend
        typeform_id = "1a2b3c4d5"

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "typeform_id": typeform_id,
                "event_date": datetime.date.today().isoformat(),
            },
            expected_num_queries=self.expected_num_queries_with_job,
        )
        assert response.status_code == 303

        response = authenticated_client.get(response.location)
        assert html_parser.extract_alert(response.data) == "L'opération spéciale Jeu concours 1a2b3c4d5 a été importée."
        special_event = operations_models.SpecialEvent.query.one()
        assert special_event.eventDate == datetime.date.today()
        assert special_event.externalId == typeform_id
        assert operations_models.SpecialEventQuestion.query.count() == 3
        assert operations_models.SpecialEventResponse.query.count() == 1
        assert operations_models.SpecialEventAnswer.query.count() == 3

    def test_create_event_already_exists(self, authenticated_client, special_events):
        # Data come from TestingBackend
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "typeform_id": "abCd1234",
                "event_date": datetime.date.today().isoformat(),
            },
            expected_num_queries=self.expected_num_queries,
        )
        assert response.status_code == 303

        response = authenticated_client.get(response.location)
        assert html_parser.extract_alert(response.data) == "Cette opération spéciale a déjà été importée."

        assert operations_models.SpecialEvent.query.count() == len(special_events)

    @patch("pcapi.connectors.typeform.get_form", side_effect=typeform.NotFoundException)
    def test_create_event_not_found(self, mock_get_form, authenticated_client):
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "typeform_id": "1a2b3c4d5e",
                "event_date": datetime.date.today().isoformat(),
            },
            expected_num_queries=self.expected_num_queries,
        )
        assert response.status_code == 303

        response = authenticated_client.get(response.location)
        assert html_parser.extract_alert(response.data) == "Le formulaire 1a2b3c4d5e n'a pas été trouvé sur Typeform."

        assert operations_models.SpecialEvent.query.count() == 0

    def test_create_far_in_the_past(self, authenticated_client):
        # Data come from TestingBackend
        event_date = datetime.date.today() - datetime.timedelta(days=12)
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "typeform_id": "abCd1234",
                "event_date": event_date.isoformat(),
            },
        )
        assert response.status_code == 303

        response = authenticated_client.get(response.location)
        assert "La date de l'évènement ne peut pas être dans le passé" in html_parser.extract_alert(response.data)

        assert operations_models.SpecialEvent.query.count() == 0


class GetEventDetailsTest(GetEndpointHelper):
    endpoint = "backoffice_web.operations.get_event_details"
    endpoint_kwargs = {"special_event_id": 1}
    needed_permission = perm_models.Permissions.READ_SPECIAL_EVENTS

    # authenticated user + user session + special event + responses
    expected_num_queries = 4

    def test_get_event_details(self, authenticated_client):
        event = operations_factories.SpecialEventFactory(
            externalId="fake00001",
            title="Énigme des enchanteurs",
            eventDate=datetime.datetime.utcnow() + datetime.timedelta(days=2),
        )
        special_event_id = event.id
        name_question = operations_factories.SpecialEventQuestionFactory(
            event=event,
            externalId="00001-abcde-00001",
            title="Comment t'appelles-tu ?",
        )
        chestnut_question = operations_factories.SpecialEventQuestionFactory(
            event=event,
            externalId="00001-abcde-00002",
            title="Qu'est-ce qui est petit et marron ?",
        )

        full_response = operations_factories.SpecialEventResponseFactory(
            event=event, status=operations_models.SpecialEventResponseStatus.PRESELECTED
        )
        full_name_answer = operations_factories.SpecialEventAnswerFactory(
            responseId=full_response.id, questionId=name_question.id, text="Elias de Kelliwic'h"
        )
        full_chestnut_answer = operations_factories.SpecialEventAnswerFactory(
            responseId=full_response.id, questionId=chestnut_question.id, text="Un marron"
        )

        no_user_incomplete_response = operations_factories.SpecialEventResponseNoUserFactory(event=event)
        no_user_name_answer = operations_factories.SpecialEventAnswerFactory(
            responseId=no_user_incomplete_response.id, questionId=name_question.id, text="Merlin l'enchanteur"
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, special_event_id=special_event_id))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        card_text = cards_text[0]

        assert "Énigme des enchanteurs" in card_text
        assert f"Typeform ID : {event.externalId}" in card_text
        assert f"Créée le : {format_date(event.dateCreated, '%d/%m/%Y à %Hh%M')}" in card_text
        assert f"Date de l'évènement : {format_date(event.eventDate, '%d/%m/%Y')}" in card_text
        assert f"Nombre de candidats : {len(event.responses)}" in card_text

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2

        assert rows[0]["Candidat"] == "Non trouvé"
        assert rows[0]["Email"] == no_user_incomplete_response.email
        assert rows[0]["Téléphone"] == no_user_incomplete_response.phoneNumber
        assert rows[0]["Éligibilité"] == ""
        assert rows[0]["Date de réponse"] == format_date(no_user_incomplete_response.dateSubmitted, "%d/%m/%Y à %Hh%M")
        assert rows[0]["État de la candidature"] == "Nouvelle"
        assert rows[0]["Réponses"] == " ".join([name_question.title, no_user_name_answer.text, chestnut_question.title])

        assert rows[1]["Candidat"] == f"{full_response.user.full_name} ({full_response.user.id})"
        assert rows[1]["Email"] == full_response.user.email
        assert rows[1]["Téléphone"] == (full_response.user.phoneNumber or "")
        assert rows[1]["Éligibilité"] == "Pass 18"
        assert rows[1]["Date de réponse"] == format_date(full_response.dateSubmitted, "%d/%m/%Y à %Hh%M")
        assert rows[1]["État de la candidature"] == "Préselectionnée"
        assert rows[1]["Réponses"] == " ".join(
            [name_question.title, full_name_answer.text, chestnut_question.title, full_chestnut_answer.text]
        )

    def test_filter_event_responses_by_response_status(self, authenticated_client):
        event = operations_factories.SpecialEventFactory(
            externalId="fake00002",
            eventDate=datetime.datetime.utcnow() + datetime.timedelta(days=2),
        )
        operations_factories.SpecialEventResponseFactory.create_batch(
            size=2,
            event=event,
            status=operations_models.SpecialEventResponseStatus.PRESELECTED,
        )
        operations_factories.SpecialEventResponseFactory.create_batch(
            size=4,
            event=event,
            status=operations_models.SpecialEventResponseStatus.NEW,
        )
        operations_factories.SpecialEventResponseFactory.create_batch(
            size=3,
            event=event,
            status=operations_models.SpecialEventResponseStatus.VALIDATED,
        )
        operations_factories.SpecialEventResponseFactory.create_batch(
            size=5,
            event=event,
            status=operations_models.SpecialEventResponseStatus.REJECTED,
        )

        url = url_for(self.endpoint, special_event_id=event.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 14

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url, params={"response_status": "PRESELECTED"})
            assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        assert {"Préselectionnée"} == {e["État de la candidature"] for e in rows}

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url, params={"response_status": "NEW"})
            assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 4
        assert {"Nouvelle"} == {e["État de la candidature"] for e in rows}

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url, params={"response_status": "VALIDATED"})
            assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 3
        assert {"Retenue"} == {e["État de la candidature"] for e in rows}

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url, params={"response_status": "REJECTED"})
            assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 5
        assert {"Rejetée"} == {e["État de la candidature"] for e in rows}

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                route=url,
                params=(("response_status", "PRESELECTED"), ("response_status", "NEW")),
            )
            assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 6
        assert {"Préselectionnée", "Nouvelle"} == {e["État de la candidature"] for e in rows}

    def test_filter_event_responses_by_eligibility(self, authenticated_client):
        event = operations_factories.SpecialEventFactory(
            externalId="fake00002",
            eventDate=datetime.datetime.utcnow() + datetime.timedelta(days=2),
        )
        response_pass_18 = operations_factories.SpecialEventResponseFactory(
            event=event, user=users_factories.BeneficiaryFactory()
        )
        response_pass_1517 = operations_factories.SpecialEventResponseFactory(
            event=event, user=users_factories.UnderageBeneficiaryFactory()
        )
        response_non_beneficiary = operations_factories.SpecialEventResponseFactory(
            event=event, user=users_factories.UserFactory()
        )
        response_suspended = operations_factories.SpecialEventResponseFactory(
            event=event, user=users_factories.BeneficiaryFactory(isActive=False)
        )

        url = url_for(self.endpoint, special_event_id=event.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url, params={"eligibility": "PASS_18_V3"})
            assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["Email"] == response_pass_18.user.email

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url, params=(("eligibility", "PASS_15_17"), ("eligibility", "PASS_18"), ("eligibility", "PASS_18_V3"))
            )
            assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        assert {row["Email"] for row in rows} == {response_pass_18.user.email, response_pass_1517.user.email}

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url, params=(("eligibility", "PUBLIC"), ("eligibility", "SUSPENDED")))
            assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        assert {row["Email"] for row in rows} == {response_non_beneficiary.user.email, response_suspended.user.email}

    def test_only_one_line_for_multiple_deposits(self, authenticated_client):
        user = users_factories.UserFactory(roles=[users_models.UserRole.BENEFICIARY])
        users_factories.DepositGrantFactory(
            user=user,
            type=finance_models.DepositType.GRANT_15_17,
            expirationDate=datetime.datetime.utcnow() - datetime.timedelta(days=2),
        )
        users_factories.DepositGrantFactory(
            user=user,
            type=finance_models.DepositType.GRANT_18,
            expirationDate=datetime.datetime.utcnow() + datetime.timedelta(days=300),
        )
        event = operations_factories.SpecialEventFactory(
            externalId="fake00001",
            title="Énigme des enchanteurs",
            eventDate=datetime.datetime.utcnow() + datetime.timedelta(days=2),
        )
        special_event_id = event.id
        name_question = operations_factories.SpecialEventQuestionFactory(
            event=event,
            externalId="00001-abcde-00001",
            title="Comment t'appelles-tu ?",
        )

        full_response = operations_factories.SpecialEventResponseFactory(
            event=event, status=operations_models.SpecialEventResponseStatus.PRESELECTED, user=user
        )
        operations_factories.SpecialEventAnswerFactory(
            responseId=full_response.id, questionId=name_question.id, text="Elias de Kelliwic'h"
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, special_event_id=special_event_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1


class ValidateResponseTest(PostEndpointHelper):
    endpoint = "backoffice_web.operations.validate_response"
    endpoint_kwargs = {"special_event_id": 1, "response_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_SPECIAL_EVENTS

    def test_validate_response(self, authenticated_client):
        event_response = operations_factories.SpecialEventResponseFactory(
            status=operations_models.SpecialEventResponseStatus.NEW
        )
        special_event_id = event_response.event.id
        response_id = event_response.id

        response = self.post_to_endpoint(
            authenticated_client, special_event_id=special_event_id, response_id=response_id
        )

        assert response.status_code == 303

        db.session.refresh(event_response)
        assert event_response.status == operations_models.SpecialEventResponseStatus.VALIDATED


class PreselectResponseTest(PostEndpointHelper):
    endpoint = "backoffice_web.operations.preselect_response"
    endpoint_kwargs = {"special_event_id": 1, "response_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_SPECIAL_EVENTS

    def test_validate_response(self, authenticated_client):
        event_response = operations_factories.SpecialEventResponseFactory(
            status=operations_models.SpecialEventResponseStatus.NEW
        )
        special_event_id = event_response.event.id
        response_id = event_response.id

        response = self.post_to_endpoint(
            authenticated_client, special_event_id=special_event_id, response_id=response_id
        )

        assert response.status_code == 303

        db.session.refresh(event_response)
        assert event_response.status == operations_models.SpecialEventResponseStatus.PRESELECTED


class RejectResponseTest(PostEndpointHelper):
    endpoint = "backoffice_web.operations.reject_response"
    endpoint_kwargs = {"special_event_id": 1, "response_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_SPECIAL_EVENTS

    def test_reject_response(self, authenticated_client):
        event_response = operations_factories.SpecialEventResponseFactory(
            status=operations_models.SpecialEventResponseStatus.NEW
        )
        special_event_id = event_response.event.id
        response_id = event_response.id

        response = self.post_to_endpoint(
            authenticated_client, special_event_id=special_event_id, response_id=response_id
        )

        assert response.status_code == 303

        db.session.refresh(event_response)
        assert event_response.status == operations_models.SpecialEventResponseStatus.REJECTED


class GetBatchValidateResponsesFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.operations.get_batch_validate_responses_form"
    endpoint_kwargs = {"special_event_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_SPECIAL_EVENTS
    # authenticated user + user session + special event
    expected_num_queries = 3

    def test_get_batch_validate_responses_form(self, authenticated_client):
        event = operations_factories.SpecialEventFactory()
        event_id = event.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, special_event_id=event_id))
            assert response.status_code == 200


class PostBatchValidateResponsesFormTest(PostEndpointHelper):
    endpoint = "backoffice_web.operations.get_batch_validate_responses_form"
    needed_permission = perm_models.Permissions.MANAGE_SPECIAL_EVENTS
    endpoint_kwargs = {"special_event_id": 1}

    def test_regular_responses(self, authenticated_client):
        event = operations_factories.SpecialEventFactory()
        event_response_new = operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.NEW,
        )
        event_response_rejected = operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.REJECTED,
        )
        event_response_preselected = operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.PRESELECTED,
        )

        response = self.post_to_endpoint(
            authenticated_client,
            special_event_id=event.id,
            form={
                "object_ids": ",".join(
                    [str(event_response_new.id), str(event_response_preselected.id), str(event_response_rejected.id)]
                )
            },
        )

        assert response.status_code == 200
        html_parser.assert_no_alert(response.data)
        assert html_parser.get_tag(response.data, class_="btn btn-primary", tag="button", string="Valider") is not None
        assert event_response_new.status == operations_models.SpecialEventResponseStatus.NEW
        assert event_response_rejected.status == operations_models.SpecialEventResponseStatus.REJECTED
        assert event_response_preselected.status == operations_models.SpecialEventResponseStatus.PRESELECTED
        object_ids_str = html_parser.extract_input_value(response.data, name="object_ids")
        object_ids_str_list = object_ids_str.split(",")
        assert len(object_ids_str_list) == 3
        assert {int(e) for e in object_ids_str_list} == {
            event_response_new.id,
            event_response_preselected.id,
            event_response_rejected.id,
        }

    def test_invalid_responses_status(self, authenticated_client):
        event = operations_factories.SpecialEventFactory()
        event_response_new = operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.VALIDATED,
        )
        event_response_validated = operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.VALIDATED,
        )
        event_id = event.id
        response = self.post_to_endpoint(
            authenticated_client,
            special_event_id=event_id,
            form={"object_ids": ",".join([str(event_response_new.id), str(event_response_validated.id)])},
        )

        assert response.status_code == 200
        assert (
            html_parser.extract_alert(response.data)
            == "Toutes les candidatures séléctionnées ont déjà été retenues. L'action n'aura aucun effet."
        )
        assert html_parser.extract(response.data, class_="btn btn-primary", tag="button") == []
        assert html_parser.extract(response.data, tag="form") == []
        assert event_response_new.status == operations_models.SpecialEventResponseStatus.VALIDATED
        assert event_response_validated.status == operations_models.SpecialEventResponseStatus.VALIDATED


class BatchValidateResponsesTest(PostEndpointHelper):
    endpoint = "backoffice_web.operations.batch_validate_responses"
    needed_permission = perm_models.Permissions.MANAGE_SPECIAL_EVENTS
    endpoint_kwargs = {"special_event_id": 1}

    def test_regular(self, authenticated_client):
        event = operations_factories.SpecialEventFactory()
        event_response_new = operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.NEW,
        )
        event_response_rejected = operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.REJECTED,
        )
        event_response_preselected = operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.PRESELECTED,
        )

        response = self.post_to_endpoint(
            authenticated_client,
            special_event_id=event.id,
            form={
                "object_ids": ",".join(
                    [str(event_response_new.id), str(event_response_preselected.id), str(event_response_rejected.id)]
                )
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert response.request.path == url_for(
            "backoffice_web.operations.get_event_details", special_event_id=event.id
        )
        assert html_parser.extract_alert(response.data) == "Les candidatures ont été retenues."

        assert event_response_new.status == operations_models.SpecialEventResponseStatus.VALIDATED
        assert event_response_rejected.status == operations_models.SpecialEventResponseStatus.VALIDATED
        assert event_response_preselected.status == operations_models.SpecialEventResponseStatus.VALIDATED


class GetBatchPreselectResponsesFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.operations.get_batch_preselect_responses_form"
    endpoint_kwargs = {"special_event_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_SPECIAL_EVENTS
    # authenticated user + user session + special event
    expected_num_queries = 3

    def test_get_batch_preselect_responses_form(self, authenticated_client):
        event = operations_factories.SpecialEventFactory()
        event_id = event.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, special_event_id=event_id))
            assert response.status_code == 200


class PostBatchPreselectResponsesFormTest(PostEndpointHelper):
    endpoint = "backoffice_web.operations.get_batch_preselect_responses_form"
    needed_permission = perm_models.Permissions.MANAGE_SPECIAL_EVENTS
    endpoint_kwargs = {"special_event_id": 1}

    def test_regular_responses(self, authenticated_client):
        event = operations_factories.SpecialEventFactory()
        event_response_new = operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.NEW,
        )
        event_response_rejected = operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.REJECTED,
        )
        event_response_validated = operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.VALIDATED,
        )

        response = self.post_to_endpoint(
            authenticated_client,
            special_event_id=event.id,
            form={
                "object_ids": ",".join(
                    [str(event_response_new.id), str(event_response_validated.id), str(event_response_rejected.id)]
                )
            },
        )

        assert response.status_code == 200
        html_parser.assert_no_alert(response.data)
        assert html_parser.get_tag(response.data, class_="btn btn-primary", tag="button", string="Valider") is not None
        assert event_response_new.status == operations_models.SpecialEventResponseStatus.NEW
        assert event_response_rejected.status == operations_models.SpecialEventResponseStatus.REJECTED
        assert event_response_validated.status == operations_models.SpecialEventResponseStatus.VALIDATED
        object_ids_str = html_parser.extract_input_value(response.data, name="object_ids")
        object_ids_str_list = object_ids_str.split(",")
        assert len(object_ids_str_list) == 3
        assert {int(e) for e in object_ids_str_list} == {
            event_response_new.id,
            event_response_validated.id,
            event_response_rejected.id,
        }

    def test_invalid_responses_status(self, authenticated_client):
        event = operations_factories.SpecialEventFactory()
        event_response_new = operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.PRESELECTED,
        )
        event_response_preselected = operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.PRESELECTED,
        )
        event_id = event.id
        response = self.post_to_endpoint(
            authenticated_client,
            special_event_id=event_id,
            form={"object_ids": ",".join([str(event_response_new.id), str(event_response_preselected.id)])},
        )

        assert response.status_code == 200
        assert (
            html_parser.extract_alert(response.data)
            == "Toutes les candidatures séléctionnées sont déjà à l'état \"préselectionné\". L'action n'aura aucun effet."
        )
        assert html_parser.extract(response.data, class_="btn btn-primary", tag="button") == []
        assert html_parser.extract(response.data, tag="form") == []
        assert event_response_new.status == operations_models.SpecialEventResponseStatus.PRESELECTED
        assert event_response_preselected.status == operations_models.SpecialEventResponseStatus.PRESELECTED


class BatchPreselectResponsesTest(PostEndpointHelper):
    endpoint = "backoffice_web.operations.batch_preselect_responses"
    needed_permission = perm_models.Permissions.MANAGE_SPECIAL_EVENTS
    endpoint_kwargs = {"special_event_id": 1}

    def test_regular(self, authenticated_client):
        event = operations_factories.SpecialEventFactory()
        event_response_new = operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.NEW,
        )
        event_response_rejected = operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.REJECTED,
        )
        event_response_validated = operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.VALIDATED,
        )

        response = self.post_to_endpoint(
            authenticated_client,
            special_event_id=event.id,
            form={
                "object_ids": ",".join(
                    [str(event_response_new.id), str(event_response_rejected.id), str(event_response_validated.id)]
                )
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert response.request.path == url_for(
            "backoffice_web.operations.get_event_details", special_event_id=event.id
        )
        assert html_parser.extract_alert(response.data) == "Les candidatures ont été préselectionnées."

        assert event_response_new.status == operations_models.SpecialEventResponseStatus.PRESELECTED
        assert event_response_rejected.status == operations_models.SpecialEventResponseStatus.PRESELECTED
        assert event_response_validated.status == operations_models.SpecialEventResponseStatus.PRESELECTED


class GetBatchRejectResponsesFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.operations.get_batch_reject_responses_form"
    endpoint_kwargs = {"special_event_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_SPECIAL_EVENTS
    # authenticated user + user session + special event
    expected_num_queries = 3

    def test_get_batch_reject_responses_form(self, authenticated_client):
        event = operations_factories.SpecialEventFactory()
        event_id = event.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, special_event_id=event_id))
            assert response.status_code == 200


class PostBatchRejectResponsesFormTest(PostEndpointHelper):
    endpoint = "backoffice_web.operations.get_batch_reject_responses_form"
    needed_permission = perm_models.Permissions.MANAGE_SPECIAL_EVENTS
    endpoint_kwargs = {"special_event_id": 1}

    def test_regular_responses(self, authenticated_client):
        event = operations_factories.SpecialEventFactory()
        event_response_new = operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.NEW,
        )
        event_response_preselected = operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.PRESELECTED,
        )
        event_response_validated = operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.VALIDATED,
        )

        response = self.post_to_endpoint(
            authenticated_client,
            special_event_id=event.id,
            form={
                "object_ids": ",".join(
                    [str(event_response_new.id), str(event_response_validated.id), str(event_response_preselected.id)]
                )
            },
        )

        assert response.status_code == 200
        html_parser.assert_no_alert(response.data)
        assert html_parser.get_tag(response.data, class_="btn btn-primary", tag="button", string="Valider") is not None
        assert event_response_new.status == operations_models.SpecialEventResponseStatus.NEW
        assert event_response_preselected.status == operations_models.SpecialEventResponseStatus.PRESELECTED
        assert event_response_validated.status == operations_models.SpecialEventResponseStatus.VALIDATED
        object_ids_str = html_parser.extract_input_value(response.data, name="object_ids")
        object_ids_str_list = object_ids_str.split(",")
        assert len(object_ids_str_list) == 3
        assert {int(e) for e in object_ids_str_list} == {
            event_response_new.id,
            event_response_validated.id,
            event_response_preselected.id,
        }

    def test_invalid_responses_status(self, authenticated_client):
        event = operations_factories.SpecialEventFactory()
        event_response_new = operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.REJECTED,
        )
        event_response_rejected = operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.REJECTED,
        )
        event_id = event.id
        response = self.post_to_endpoint(
            authenticated_client,
            special_event_id=event_id,
            form={"object_ids": ",".join([str(event_response_new.id), str(event_response_rejected.id)])},
        )

        assert response.status_code == 200
        assert (
            html_parser.extract_alert(response.data)
            == "Toutes les candidatures séléctionnées ont déjà été rejetées. L'action n'aura aucun effet."
        )
        assert html_parser.extract(response.data, class_="btn btn-primary", tag="button") == []
        assert html_parser.extract(response.data, tag="form") == []
        assert event_response_new.status == operations_models.SpecialEventResponseStatus.REJECTED
        assert event_response_rejected.status == operations_models.SpecialEventResponseStatus.REJECTED


class BatchRejectResponsesTest(PostEndpointHelper):
    endpoint = "backoffice_web.operations.batch_reject_responses"
    needed_permission = perm_models.Permissions.MANAGE_SPECIAL_EVENTS
    endpoint_kwargs = {"special_event_id": 1}

    def test_regular(self, authenticated_client):
        event = operations_factories.SpecialEventFactory()
        event_response_new = operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.NEW,
        )
        event_response_preselected = operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.PRESELECTED,
        )
        event_response_validated = operations_factories.SpecialEventResponseFactory(
            event=event,
            status=operations_models.SpecialEventResponseStatus.VALIDATED,
        )

        response = self.post_to_endpoint(
            authenticated_client,
            special_event_id=event.id,
            form={
                "object_ids": ",".join(
                    [str(event_response_new.id), str(event_response_preselected.id), str(event_response_validated.id)]
                )
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert response.request.path == url_for(
            "backoffice_web.operations.get_event_details", special_event_id=event.id
        )
        assert html_parser.extract_alert(response.data) == "Les candidatures ont été rejetées."

        assert event_response_new.status == operations_models.SpecialEventResponseStatus.REJECTED
        assert event_response_preselected.status == operations_models.SpecialEventResponseStatus.REJECTED
        assert event_response_validated.status == operations_models.SpecialEventResponseStatus.REJECTED
