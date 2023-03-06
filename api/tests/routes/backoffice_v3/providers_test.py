from flask import url_for
import pytest

from pcapi.core.permissions import models as perm_models
from pcapi.core.providers import factories as providers_factories
from pcapi.core.testing import assert_num_queries

from .helpers import html_parser
from .helpers import unauthorized as unauthorized_helpers


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class ListProvidersTest:
    endpoint = "backoffice_v3_web.providers.get_providers_details"

    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch each provider with joinedload (4 queries)
    expected_num_queries = 6

    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.providers.get_providers_details"
        needed_permission = perm_models.Permissions.MANAGE_PROVIDERS

    def test_get_providers(self, authenticated_client):
        # given
        allocine_provider = providers_factories.AllocinePivotFactory()
        boost_provider = providers_factories.BoostCinemaDetailsFactory()
        cgr_provider = providers_factories.CGRCinemaDetailsFactory()
        cineoffice_provider = providers_factories.CDSCinemaDetailsFactory()

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))

        # then
        allocine_rows = html_parser.extract_table_rows(response.data, "allocine-tab-pane")
        assert allocine_rows[0]["Id du Lieu"] == str(allocine_provider.venue.id)
        assert allocine_rows[0]["Lieu"] == allocine_provider.venue.name
        assert allocine_rows[0]["Identifiant cinéma (Allociné)"] == allocine_provider.theaterId
        assert allocine_rows[0]["Identifiant interne Allociné"] == allocine_provider.internalId

        boost_rows = html_parser.extract_table_rows(response.data, "boost-tab-pane")
        assert boost_rows[0]["Id du Lieu"] == str(boost_provider.cinemaProviderPivot.venue.id)
        assert boost_rows[0]["Lieu"] == boost_provider.cinemaProviderPivot.venue.name
        assert boost_rows[0]["Identifiant cinéma (Boost)"] == boost_provider.cinemaProviderPivot.idAtProvider
        assert boost_rows[0]["Nom de l'utilisateur (Boost)"] == boost_provider.username
        assert boost_rows[0]["Mot de passe (Boost)"] == boost_provider.password
        assert boost_rows[0]["Url du cinéma (Boost)"] == boost_provider.cinemaUrl

        cgr_rows = html_parser.extract_table_rows(response.data, "cgr-tab-pane")
        assert cgr_rows[0]["Id du Lieu"] == str(cgr_provider.cinemaProviderPivot.venue.id)
        assert cgr_rows[0]["Lieu"] == cgr_provider.cinemaProviderPivot.venue.name
        assert cgr_rows[0]["Identifiant cinéma (CGR)"] == cgr_provider.cinemaProviderPivot.idAtProvider
        assert cgr_rows[0]["Url du cinéma (CGR)"] == cgr_provider.cinemaUrl

        cineoffice_rows = html_parser.extract_table_rows(response.data, "cineoffice-tab-pane")
        assert cineoffice_rows[0]["Id du Lieu"] == str(cineoffice_provider.cinemaProviderPivot.venue.id)
        assert cineoffice_rows[0]["Lieu"] == cineoffice_provider.cinemaProviderPivot.venue.name
        assert cineoffice_rows[0]["Identifiant cinéma (CDS)"] == cineoffice_provider.cinemaProviderPivot.idAtProvider
        assert cineoffice_rows[0]["Nom de l'utilisateur (CDS)"] == cineoffice_provider.accountId
        assert cineoffice_rows[0]["Clé API (CDS)"] == cineoffice_provider.cinemaApiToken
