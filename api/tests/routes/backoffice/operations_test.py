import datetime
from unittest.mock import patch

from flask import url_for
import pytest

from pcapi.connectors import typeform
from pcapi.core.operations import factories as operations_factories
from pcapi.core.operations import models as operations_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.routes.backoffice.filters import format_date

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
    needed_permission = perm_models.Permissions.MANAGE_SPECIAL_EVENTS

    # authenticated user + user session + list of special events + count + WIP_ENABLE_OFFER_ADDRESS FF
    expected_num_queries = 5

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


class CreateEventTest(PostEndpointHelper):
    endpoint = "backoffice_web.operations.create_event"
    needed_permission = perm_models.Permissions.MANAGE_SPECIAL_EVENTS

    # - authenticated user
    # - user session
    # - insert into special_event or rollback
    expected_num_queries = 3
    # - insert into special_event_question
    expected_num_queries_with_questions = expected_num_queries + 1

    def test_create_event(self, authenticated_client):
        # Data come from TestingBackend
        typeform_id = "1a2b3c4d5"

        response = self.post_to_endpoint(
            authenticated_client,
            form={"typeform_id": typeform_id},
            expected_num_queries=self.expected_num_queries_with_questions,
        )
        assert response.status_code == 303

        response = authenticated_client.get(response.location)
        assert html_parser.extract_alert(response.data) == "L'opération spéciale Jeu concours 1a2b3c4d5 a été importée."

        assert operations_models.SpecialEvent.query.one().externalId == typeform_id
        assert operations_models.SpecialEventQuestion.query.count() == 3

    def test_create_event_already_exists(self, authenticated_client, special_events):
        # Data come from TestingBackend
        response = self.post_to_endpoint(
            authenticated_client, form={"typeform_id": "abCd1234"}, expected_num_queries=self.expected_num_queries
        )
        assert response.status_code == 303

        response = authenticated_client.get(response.location)
        assert html_parser.extract_alert(response.data) == "Cette opération spéciale a déjà été importée."

        assert operations_models.SpecialEvent.query.count() == len(special_events)

    @patch("pcapi.connectors.typeform.get_form", side_effect=typeform.NotFoundException)
    def test_create_event_not_found(self, mock_get_form, authenticated_client):
        response = self.post_to_endpoint(
            authenticated_client, form={"typeform_id": "1a2b3c4d5e"}, expected_num_queries=self.expected_num_queries
        )
        assert response.status_code == 303

        response = authenticated_client.get(response.location)
        assert html_parser.extract_alert(response.data) == "Le formulaire 1a2b3c4d5e n'a pas été trouvé sur Typeform."

        assert operations_models.SpecialEvent.query.count() == 0


class GetEventDetailsTest(GetEndpointHelper):
    endpoint = "backoffice_web.operations.get_event_details"
    endpoint_kwargs = {"special_event_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_SPECIAL_EVENTS

    # authenticated user + user session + special event + responses + WIP_ENABLE_OFFER_ADDRESS FF
    expected_num_queries = 5

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
            title=f"Comment t'appelles-tu ?",
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
        assert f"Date de l'évènement : {format_date(event.eventDate, '%d/%m/%Y à %Hh%M')}" in card_text
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
