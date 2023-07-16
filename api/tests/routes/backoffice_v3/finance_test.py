from flask import url_for
import pytest

from pcapi.core import testing
from pcapi.core.finance import factories as finance_factories
from pcapi.core.permissions import models as perm_models

from .helpers import html_parser
from .helpers.get import GetEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class ListIncidentsTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.finance_incident.list_incidents"
    needed_permission = perm_models.Permissions.READ_INCIDENTS

    expected_num_queries = 0
    expected_num_queries += 1  # Fetch Session
    expected_num_queries += 1  # Fetch User
    expected_num_queries += 1  # Fetch Finance Incidents

    def test_list_incidents_without_filter(self, authenticated_client):
        incidents = finance_factories.FinanceIncidentFactory.create_batch(10)

        url = url_for(self.endpoint)

        with testing.assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == len(incidents)
        assert rows[0]["ID"] == str(incidents[0].id)
        assert rows[0]["Statut de l'incident"] == "Créé"
        assert rows[0]["Type d'incident"] == "Trop Perçu"
