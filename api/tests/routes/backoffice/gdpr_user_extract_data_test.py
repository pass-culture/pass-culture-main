import datetime

from flask import url_for
import pytest

from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.routes.backoffice.filters import format_date

from .helpers import html_parser
from .helpers.get import GetEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


@pytest.fixture(scope="function", name="list_of_gdpr_user_extract_data")
def gdpr_user_extract_data_fixture() -> tuple:
    gdpr_1 = users_factories.GdprUserDataExtractBeneficiaryFactory()
    gdpr_2 = users_factories.GdprUserDataExtractBeneficiaryFactory(dateProcessed=datetime.datetime.utcnow())
    gdpr_3 = users_factories.GdprUserDataExtractBeneficiaryFactory()
    gdpr_4 = users_factories.GdprUserDataExtractBeneficiaryFactory()
    gdpr_5 = users_factories.GdprUserDataExtractBeneficiaryFactory(
        dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=8)
    )
    return gdpr_5, gdpr_4, gdpr_3, gdpr_2, gdpr_1


class ListGdprUserExtractDataTest(GetEndpointHelper):
    endpoint = "backoffice_web.gdpr_extract.list_gdpr_user_data_extract"
    needed_permission = perm_models.Permissions.EXTRACT_PUBLIC_ACCOUNT

    # Use assert_num_queries() instead of assert_no_duplicated_queries() which does not detect one extra query caused
    # by a field added in the jinja template.
    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch gdpr_data_extract
    # - fetch temporary FF WIP_BENEFICIARY_EXTRACT_TOOL
    expected_num_queries = 4

    @override_features(WIP_BENEFICIARY_EXTRACT_TOOL=True)
    def test_list_gdpr_user_extract_data(self, authenticated_client, list_of_gdpr_user_extract_data):

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 4

        assert rows[0]["ID de l'extrait"] == str(list_of_gdpr_user_extract_data[1].id)
        assert rows[0]["Date de création de la demande"] == format_date(list_of_gdpr_user_extract_data[1].dateCreated)
        assert rows[0]["État de la demande"] == "en attente"
        assert (
            rows[0]["Nom et prénom du jeune"]
            == f"{list_of_gdpr_user_extract_data[1].user.full_name} ({str(list_of_gdpr_user_extract_data[1].user.id)})"
        )
        assert rows[0]["Auteur de la demande"] == list_of_gdpr_user_extract_data[1].authorUser.full_name

        assert rows[2]["État de la demande"] == "prêt"

        for row in rows:
            assert list_of_gdpr_user_extract_data[4].id not in row

    @override_features(WIP_BENEFICIARY_EXTRACT_TOOL=False)
    def test_list_gdpr_user_extract_data_ff_false(self, authenticated_client, list_of_gdpr_user_extract_data):
        with assert_num_queries(self.expected_num_queries - 1):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 0
