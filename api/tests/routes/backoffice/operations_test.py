import datetime
import re
from unittest.mock import patch

import pytest
from dateutil.relativedelta import relativedelta
from flask import url_for

from pcapi.connectors import typeform
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.operations import factories as operations_factories
from pcapi.core.operations import models as operations_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.routes.backoffice.filters import format_date
from pcapi.utils import date as date_utils

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

    # user session + list of special events + count
    expected_num_queries = 3

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

    # - session + user
    # - insert into special_event or rollback
    expected_num_queries = 2
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
        venue = offerers_factories.VenueFactory()
        event_date = datetime.date.today() + datetime.timedelta(days=7)
        end_import_date = datetime.date.today() + datetime.timedelta(days=6)

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "typeform_id": typeform_id,
                "event_date": event_date.isoformat(),
                "end_import_date": end_import_date.isoformat(),
                "venue": venue.id,
            },
            expected_num_queries=self.expected_num_queries_with_job + 1,  # retrieve the venue
        )
        assert response.status_code == 303

        response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(response.data)
            == f"L'opération spéciale Jeu concours {typeform_id} a été importée."
        )
        special_event = db.session.query(operations_models.SpecialEvent).one()
        assert special_event.eventDate == event_date
        assert special_event.endImportDate == end_import_date
        assert special_event.externalId == typeform_id
        assert special_event.venueId == venue.id
        assert db.session.query(operations_models.SpecialEventQuestion).count() == 3
        assert db.session.query(operations_models.SpecialEventResponse).count() == 1
        assert db.session.query(operations_models.SpecialEventAnswer).count() == 3

    def test_create_event_without_venue(self, authenticated_client):
        # Data come from TestingBackend
        typeform_id = "1a2b3c4d5"
        event_date = datetime.date.today() + datetime.timedelta(days=7)
        end_import_date = datetime.date.today() + datetime.timedelta(days=6)

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "typeform_id": typeform_id,
                "event_date": event_date.isoformat(),
                "end_import_date": end_import_date.isoformat(),
                "venue": "",
            },
            expected_num_queries=self.expected_num_queries_with_job,
        )
        assert response.status_code == 303

        response = authenticated_client.get(response.location)
        special_event = db.session.query(operations_models.SpecialEvent).one()
        assert special_event.eventDate == event_date
        assert special_event.endImportDate == end_import_date
        assert special_event.externalId == typeform_id
        assert special_event.venueId is None

    def test_create_event_already_exists(self, authenticated_client, special_events):
        # Data come from TestingBackend
        event_date = datetime.date.today() + datetime.timedelta(days=7)
        end_import_date = datetime.date.today() + datetime.timedelta(days=6)

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "typeform_id": "abCd1234",
                "event_date": event_date.isoformat(),
                "end_import_date": end_import_date.isoformat(),
            },
            expected_num_queries=self.expected_num_queries,
        )
        assert response.status_code == 303

        response = authenticated_client.get(response.location)
        assert html_parser.extract_alert(response.data) == "Cette opération spéciale a déjà été importée."

        assert db.session.query(operations_models.SpecialEvent).count() == len(special_events)

    @patch("pcapi.connectors.typeform.get_form", side_effect=typeform.NotFoundException)
    def test_create_event_not_found(self, mock_get_form, authenticated_client):
        event_date = datetime.date.today() + datetime.timedelta(days=7)
        end_import_date = datetime.date.today() + datetime.timedelta(days=6)

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "typeform_id": "1a2b3c4d5e",
                "event_date": event_date.isoformat(),
                "end_import_date": end_import_date.isoformat(),
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

    # get session + user
    # get special event
    # get special event stats
    # get special event responses
    # count special event responses (for pagination)
    expected_num_queries = 5

    def test_get_event_details(self, authenticated_client):
        event = operations_factories.SpecialEventFactory(
            externalId="fake00001",
            title="Énigme des enchanteurs",
            eventDate=date_utils.get_naive_utc_now() + datetime.timedelta(days=2),
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
        assert format_date(event.dateCreated, "%d/%m/%Y") in descriptions["Date d'import"]
        assert format_date(event.eventDate, "%d/%m/%Y") in descriptions["Date de l'opération"]
        assert str(len(event.responses)) == descriptions["Nombre de candidats total"]
        assert descriptions["Nouvelles candidatures"] == "1"
        assert descriptions["Candidatures en attente"] == "0"
        assert descriptions["Candidatures à contacter"] == "1"
        assert descriptions["Candidatures confirmées"] == "0"
        assert descriptions["Candidatures de backup"] == "0"

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2

        assert rows[0]["ID"] == str(no_user_incomplete_response.id)
        assert rows[0]["Candidat"] == no_user_incomplete_response.email
        assert rows[0]["Email"] == "-"
        assert rows[0]["Dép."] == ""
        assert rows[0]["État de la candidature"] == "Nouvelle"
        assert rows[0]["Candidatures totales"] == "-"
        assert rows[0]["Participations effectives"] == "-"
        assert rows[0]["Éligibilité"] == "-"
        assert rows[0]["Date de réponse"] == format_date(no_user_incomplete_response.dateSubmitted, "%d/%m/%Y à %Hh%M")

        assert rows[1]["ID"] == str(full_response.id)
        assert rows[1]["Candidat"] == f"{full_response.user.full_name} ({full_response.user.id})"
        assert rows[1]["Email"] == full_response.user.email
        assert rows[1]["Dép."] == str(full_response.user.departementCode)
        assert rows[1]["État de la candidature"] == "À contacter"
        assert rows[1]["Candidatures totales"] == "1"
        assert rows[1]["Participations effectives"] == "0"
        assert rows[1]["Éligibilité"] == "Pass 18"
        assert rows[1]["Date de réponse"] == format_date(full_response.dateSubmitted, "%d/%m/%Y à %Hh%M")

    def test_filter_event_responses_by_response_status(self, authenticated_client):
        event = operations_factories.SpecialEventFactory(
            externalId="fake00002",
            eventDate=date_utils.get_naive_utc_now() + datetime.timedelta(days=2),
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

    def test_filter_event_responses_by_age(self, authenticated_client):
        event = operations_factories.SpecialEventFactory()
        operations_factories.SpecialEventResponseFactory(
            event=event,
            user__validatedBirthDate=datetime.date.today() - relativedelta(years=22),
        )
        event_response = operations_factories.SpecialEventResponseFactory(
            event=event,
            user__validatedBirthDate=datetime.date.today() - relativedelta(years=20),
        )
        operations_factories.SpecialEventResponseFactory(
            event=event,
            user__validatedBirthDate=datetime.date.today() - relativedelta(years=18),
        )

        url = url_for(self.endpoint, special_event_id=event.id, age=20)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(event_response.id)

    def test_filter_event_responses_by_content(self, authenticated_client):
        event = operations_factories.SpecialEventFactory()
        question1 = operations_factories.SpecialEventQuestionFactory()
        question2 = operations_factories.SpecialEventQuestionFactory()

        operations_factories.SpecialEventResponseFactory(
            event=event,
        )
        visible_response = operations_factories.SpecialEventResponseFactory(
            event=event,
        )
        hidden_response = operations_factories.SpecialEventResponseFactory(
            event=event,
        )

        operations_factories.SpecialEventAnswerFactory(
            questionId=question1.id, responseId=visible_response.id, text="visible"
        )
        operations_factories.SpecialEventAnswerFactory(
            questionId=question1.id, responseId=hidden_response.id, text="hidden"
        )

        operations_factories.SpecialEventAnswerFactory(
            questionId=question2.id, responseId=visible_response.id, text="hidden"
        )
        operations_factories.SpecialEventAnswerFactory(
            questionId=question2.id, responseId=hidden_response.id, text="visible"
        )
        filters = {
            "response-question": str(question1.id),
            "response-response": "visIblé",
        }
        url = url_for(self.endpoint, special_event_id=event.id, **filters)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(visible_response.id)

    def test_filter_event_responses_by_department(self, authenticated_client):
        event = operations_factories.SpecialEventFactory()
        operations_factories.SpecialEventResponseFactory(event=event, user__postalCode="75008")
        response_1 = operations_factories.SpecialEventResponseFactory(event=event, user__postalCode="74400")
        response_2 = operations_factories.SpecialEventResponseFactory(event=event, user__postalCode="97304")
        operations_factories.SpecialEventResponseFactory(event=event, user__postalCode="97439")

        url = url_for(self.endpoint, special_event_id=event.id, department=["74", "973"])
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        assert {row["ID"] for row in rows} == {str(response_1.id), str(response_2.id)}

    def test_filter_event_responses_by_eligibility(self, authenticated_client):
        event = operations_factories.SpecialEventFactory(
            externalId="fake00002",
            eventDate=date_utils.get_naive_utc_now() + datetime.timedelta(days=2),
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

    @staticmethod
    def _extract_user_id_from_cell(cell_tag):
        raw_text = html_parser.filter_whitespaces(cell_tag.text)
        match = re.search("\ \((?P<user_id>\d+)\)", raw_text)
        return match.groupdict().get("user_id") if match else None

    def test_display_user_tags(self, authenticated_client):
        tag1 = users_factories.UserTagFactory(name="tag1")
        tag2 = users_factories.UserTagFactory(label="Tag 2")
        user1 = users_factories.UserFactory(tags=[tag1, tag2])
        user2 = users_factories.UserFactory()
        event = operations_factories.SpecialEventFactory(
            externalId="fake00001",
            title="A",
            eventDate=date_utils.get_naive_utc_now() + datetime.timedelta(days=2),
        )
        special_event_id = event.id
        name_question = operations_factories.SpecialEventQuestionFactory(
            event=event,
            externalId="00001-abcde-00001",
            title="Comment t'appelles-tu ?",
        )

        full_response1 = operations_factories.SpecialEventResponseFactory(
            event=event, status=operations_models.SpecialEventResponseStatus.PRESELECTED, user=user1
        )
        operations_factories.SpecialEventAnswerFactory(
            responseId=full_response1.id, questionId=name_question.id, text="Jean A"
        )

        full_response2 = operations_factories.SpecialEventResponseFactory(
            event=event, status=operations_models.SpecialEventResponseStatus.PRESELECTED, user=user2
        )
        operations_factories.SpecialEventAnswerFactory(
            responseId=full_response2.id, questionId=name_question.id, text="Jean B"
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, special_event_id=special_event_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data, td_text_only=False)
        assert len(rows) == 2
        assert {self._extract_user_id_from_cell(e["Candidat"]) for e in rows} == {str(user1.id), str(user2.id)}
        tags1 = [r["Tags"] for r in rows if self._extract_user_id_from_cell(r["Candidat"]) == str(user1.id)][0]
        tags2 = [r["Tags"] for r in rows if self._extract_user_id_from_cell(r["Candidat"]) == str(user2.id)][0]
        assert set(html_parser.extract_badges(tags1.decode())) == {"tag1", "Tag 2"}
        assert html_parser.filter_whitespaces(tags2.text) == ""

    def test_only_one_line_for_multiple_deposits(self, authenticated_client):
        user = users_factories.UserFactory(roles=[users_models.UserRole.BENEFICIARY])
        users_factories.DepositGrantFactory(
            user=user,
            type=finance_models.DepositType.GRANT_15_17,
            expirationDate=date_utils.get_naive_utc_now() - datetime.timedelta(days=2),
        )
        users_factories.DepositGrantFactory(
            user=user,
            type=finance_models.DepositType.GRANT_18,
            expirationDate=date_utils.get_naive_utc_now() + datetime.timedelta(days=300),
        )
        event = operations_factories.SpecialEventFactory(
            externalId="fake00001",
            title="Énigme des enchanteurs",
            eventDate=date_utils.get_naive_utc_now() + datetime.timedelta(days=2),
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

        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"operation-response-row-{event_response.id}")
        assert cells[2] == str(event_response.id)
        db.session.refresh(event_response)
        assert event_response.status == response_status

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

        assert response.status_code == 200
        db.session.refresh(event_response)
        assert event_response.status == operations_models.SpecialEventResponseStatus.WITHDRAWN


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
        event_response1 = operations_factories.SpecialEventResponseFactory()
        event_response2 = operations_factories.SpecialEventResponseFactory(event=event_response1.event)

        response = self.post_to_endpoint(
            authenticated_client,
            special_event_id=event_response1.eventId,
            response_status=response_status.value,
            form={"object_ids": f"{event_response1.id},{event_response2.id}"},
        )
        assert response.status_code == 200
        for event_response in (event_response1, event_response2):
            cells = html_parser.extract_plain_row(response.data, id=f"operation-response-row-{event_response.id}")
            assert cells[2] == str(event_response.id)
        db.session.refresh(event_response1)
        db.session.refresh(event_response2)
        assert event_response1.status == response_status
        assert event_response2.status == response_status


class UpdateDateEventTest(PostEndpointHelper):
    endpoint = "backoffice_web.operations.update_date_event"
    endpoint_kwargs = {"special_event_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_SPECIAL_EVENTS

    def test_set_event_date(self, authenticated_client):
        event = operations_factories.SpecialEventFactory()
        date = datetime.date.today()
        assert event.eventDate != date

        response = self.post_to_endpoint(
            authenticated_client,
            special_event_id=event.id,
            form={"date": date.isoformat()},
        )

        assert response.status_code == 303
        db.session.refresh(event)
        assert event.eventDate == date


class UpdateEndImportDateTest(PostEndpointHelper):
    endpoint = "backoffice_web.operations.update_end_import_date"
    endpoint_kwargs = {"special_event_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_SPECIAL_EVENTS

    def test_set_end_import_date(self, authenticated_client):
        event = operations_factories.SpecialEventFactory()
        date = datetime.date.today()
        assert event.endImportDate != date

        response = self.post_to_endpoint(
            authenticated_client,
            special_event_id=event.id,
            form={"date": date.isoformat()},
        )

        assert response.status_code == 303
        db.session.refresh(event)
        assert event.endImportDate == date


class UpdateVenueTest(PostEndpointHelper):
    endpoint = "backoffice_web.operations.update_venue"
    endpoint_kwargs = {"special_event_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_SPECIAL_EVENTS

    def test_set_venue(self, authenticated_client):
        event = operations_factories.SpecialEventFactory(venue=offerers_factories.VenueFactory())
        venue = offerers_factories.VenueFactory()

        response = self.post_to_endpoint(
            authenticated_client,
            special_event_id=event.id,
            form={"venue": [str(venue.id)]},
        )

        assert response.status_code == 303

        db.session.refresh(event)
        assert event.venueId == venue.id

    def test_remove_venue(self, authenticated_client):
        event = operations_factories.SpecialEventFactory(venue=offerers_factories.VenueFactory())

        response = self.post_to_endpoint(
            authenticated_client,
            special_event_id=event.id,
            form={"venue": [""]},
        )

        assert response.status_code == 303
        db.session.refresh(event)
        assert event.venueId is None
