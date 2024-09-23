from unittest.mock import patch

from flask import url_for
import pytest

from pcapi.connectors import typeform
from pcapi.core.operations import factories as operations_factories
from pcapi.core.operations import models as operations_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries

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
