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
        special_event = db.session.query(operations_models.SpecialEvent).one()
        assert special_event.eventDate == datetime.date.today()
        assert special_event.externalId == typeform_id
        assert db.session.query(operations_models.SpecialEventQuestion).count() == 3
        assert db.session.query(operations_models.SpecialEventResponse).count() == 1
        assert db.session.query(operations_models.SpecialEventAnswer).count() == 3

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

        assert db.session.query(operations_models.SpecialEvent).count() == len(special_events)

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

        assert db.session.query(operations_models.SpecialEvent).count() == 0

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

        assert db.session.query(operations_models.SpecialEvent).count() == 0


class GetEventDetailsTest(GetEndpointHelper):
    endpoint = "backoffice_web.operations.get_event_details"
    endpoint_kwargs = {"special_event_id": 1}
    needed_permission = perm_models.Permissions.READ_SPECIAL_EVENTS

    # get authenticated user
    # get user session
    # get special event
    # get special event stats
    # get special event responses
    # count special event responses (for pagination)
    expected_num_queries = 6

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
        operations_factories.SpecialEventAnswerFactory(
            responseId=full_response.id, questionId=name_question.id, text="Elias de Kelliwic'h"
        )
        operations_factories.SpecialEventAnswerFactory(
            responseId=full_response.id, questionId=chestnut_question.id, text="Un marron"
        )

        no_user_incomplete_response = operations_factories.SpecialEventResponseNoUserFactory(event=event)
        operations_factories.SpecialEventAnswerFactory(
            responseId=no_user_incomplete_response.id, questionId=name_question.id, text="Merlin l'enchanteur"
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, special_event_id=special_event_id))
            assert response.status_code == 200

        descriptions = html_parser.extract_descriptions(response.data)
        assert "Énigme des enchanteurs" in html_parser.extract(response.data, tag="h2")
        assert event.externalId.encode() in response.data
        assert descriptions["Date d'import"] == format_date(event.dateCreated, "%d/%m/%Y")
        assert descriptions["Date de l'opération"] == format_date(event.eventDate, "%d/%m/%Y")
        assert str(len(event.responses)) == descriptions["Nombre de candidats total"]
        assert descriptions["Nombre de nouvelles candidatures"] == "1"
        assert descriptions["Nombre de candidatures en attente"] == "0"
        assert descriptions["Nombre de candidatures à contacter"] == "1"
        assert descriptions["Nombre de candidatures confirmées"] == "0"
        assert descriptions["Nombre de candidatures de backup"] == "0"

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2

        assert rows[0]["ID"] == str(no_user_incomplete_response.id)
        assert rows[0]["Candidat"] == no_user_incomplete_response.email
        assert rows[0]["État de la candidature"] == "Nouvelle"
        assert rows[0]["Candidatures totales"] == "-"
        assert rows[0]["Candidatures effectives"] == "-"
        assert rows[0]["Éligibilité"] == "-"
        assert rows[0]["Date de réponse"] == format_date(no_user_incomplete_response.dateSubmitted, "%d/%m/%Y à %Hh%M")

        assert rows[1]["ID"] == str(full_response.id)
        assert rows[1]["Candidat"] == f"{full_response.user.full_name} ({full_response.user.id})"
        assert rows[1]["État de la candidature"] == "À contacter"
        assert rows[1]["Candidatures totales"] == "1"
        assert rows[1]["Candidatures effectives"] == "0"
        assert rows[1]["Éligibilité"] == "Pass 18"
        assert rows[1]["Date de réponse"] == format_date(full_response.dateSubmitted, "%d/%m/%Y à %Hh%M")

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
        assert {"À contacter"} == {e["État de la candidature"] for e in rows}

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
        assert {"Confirmée"} == {e["État de la candidature"] for e in rows}

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
        assert {"À contacter", "Nouvelle"} == {e["État de la candidature"] for e in rows}

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
        assert rows[0]["Candidat"] == f"{response_pass_18.user.full_name} ({response_pass_18.user.id})"

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url, params=(("eligibility", "PASS_15_17"), ("eligibility", "PASS_18"), ("eligibility", "PASS_18_V3"))
            )
            assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        assert {row["Candidat"] for row in rows} == {
            f"{response_pass_18.user.full_name} ({response_pass_18.user.id})",
            f"{response_pass_1517.user.full_name} ({response_pass_1517.user.id})",
        }

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url, params=(("eligibility", "PUBLIC"), ("eligibility", "SUSPENDED")))
            assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        assert {row["Candidat"] for row in rows} == {
            f"{response_non_beneficiary.user.full_name} ({response_non_beneficiary.user.id})",
            f"{response_suspended.user.full_name} ({response_suspended.user.id})",
        }

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


class SetResponseStatusTest(PostEndpointHelper):
    endpoint = "backoffice_web.operations.set_response_status"
    endpoint_kwargs = {"special_event_id": 1, "response_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_SPECIAL_EVENTS

    @pytest.mark.parametrize(
        "response_status",
        [
            operations_models.SpecialEventResponseStatus.PRESELECTED,
            operations_models.SpecialEventResponseStatus.BACKUP,
            operations_models.SpecialEventResponseStatus.VALIDATED,
            operations_models.SpecialEventResponseStatus.WITHDRAWN,
            operations_models.SpecialEventResponseStatus.WAITING,
            operations_models.SpecialEventResponseStatus.REJECTED,
        ],
    )
    def test_set_response_status(self, response_status, authenticated_client):
        event_response = operations_factories.SpecialEventResponseFactory()

        response = self.post_to_endpoint(
            authenticated_client,
            special_event_id=event_response.eventId,
            response_id=event_response.id,
            form={"response_status": response_status.value},
        )

        assert response.status_code == 303

        db_response = (
            db.session.query(
                operations_models.SpecialEventResponse.status,
            )
            .filter(
                operations_models.SpecialEventResponse.id == event_response.id,
            )
            .one()
        )
        assert db_response.status == response_status

    def test_set_response_status_new(self, authenticated_client):
        event_response = operations_factories.SpecialEventResponseFactory(
            status=operations_models.SpecialEventResponseStatus.WITHDRAWN,
        )

        response = self.post_to_endpoint(
            authenticated_client,
            special_event_id=event_response.eventId,
            response_id=event_response.id,
            form={"response_status": operations_models.SpecialEventResponseStatus.NEW.value},
        )

        assert response.status_code == 303

        db_response = (
            db.session.query(
                operations_models.SpecialEventResponse.status,
            )
            .filter(
                operations_models.SpecialEventResponse.id == event_response.id,
            )
            .one()
        )
        assert db_response.status == operations_models.SpecialEventResponseStatus.WITHDRAWN


class BatchValidateResponsesStatusTest(PostEndpointHelper):
    endpoint = "backoffice_web.operations.batch_validate_responses_status"
    endpoint_kwargs = {
        "special_event_id": 1,
        "response_status": operations_models.SpecialEventResponseStatus.PRESELECTED.value,
    }
    needed_permission = perm_models.Permissions.MANAGE_SPECIAL_EVENTS

    @pytest.mark.parametrize(
        "response_status",
        [
            operations_models.SpecialEventResponseStatus.PRESELECTED,
            operations_models.SpecialEventResponseStatus.BACKUP,
            operations_models.SpecialEventResponseStatus.VALIDATED,
            operations_models.SpecialEventResponseStatus.WITHDRAWN,
            operations_models.SpecialEventResponseStatus.WAITING,
            operations_models.SpecialEventResponseStatus.REJECTED,
        ],
    )
    def test_batch_validate_responses_status(self, response_status, authenticated_client):
        event_response = operations_factories.SpecialEventResponseFactory()
        event_response2 = operations_factories.SpecialEventResponseFactory(event=event_response.event)

        response = self.post_to_endpoint(
            authenticated_client,
            special_event_id=event_response.eventId,
            response_status=response_status.value,
            form={"object_ids": f"{event_response.id},{event_response2.id}"},
        )
        assert response.status_code == 303
        db_response = (
            db.session.query(
                operations_models.SpecialEventResponse.status,
            )
            .filter(
                operations_models.SpecialEventResponse.id.in_([event_response.id, event_response2.id]),
            )
            .all()
        )
        assert db_response[0].status == response_status
        assert db_response[1].status == response_status
