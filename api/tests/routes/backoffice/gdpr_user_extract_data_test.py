import datetime
from random import randbytes

from flask import url_for
import pytest

from pcapi import settings
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.routes.backoffice.filters import format_date

from tests.test_utils import StorageFolderManager

from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


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

    @override_features(WIP_BENEFICIARY_EXTRACT_TOOL=True)
    def test_display_download_button_when_extract_is_processed(self, authenticated_client):
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(dateProcessed=datetime.datetime.utcnow())

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        expected_action_target = url_for("backoffice_web.gdpr_extract.download_gdpr_extract", extract_id=extract.id)

        assert b'<i class="bi bi-cloud-download-fill"></i>' in response.data
        assert expected_action_target.encode("utf-8") in response.data

    @override_features(WIP_BENEFICIARY_EXTRACT_TOOL=True)
    def test_hide_download_button_when_extract_is_not_processed(self, authenticated_client):
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        expected_action_target = url_for("backoffice_web.gdpr_extract.download_gdpr_extract", extract_id=extract.id)

        assert b'<i class="bi bi-cloud-download-fill"></i>' not in response.data
        assert (
            b"""<i style="opacity: 0.5"
                       class="bi bi-cloud-download-fill"></i>"""
            in response.data
        )
        assert expected_action_target.encode("utf-8") not in response.data

    @override_features(WIP_BENEFICIARY_EXTRACT_TOOL=False)
    def test_list_gdpr_user_extract_data_ff_false(self, authenticated_client, list_of_gdpr_user_extract_data):
        with assert_num_queries(self.expected_num_queries - 1):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 0


class DownloadPublicAccountExtractTest(PostEndpointHelper, StorageFolderManager):
    endpoint = "backoffice_web.gdpr_extract.download_gdpr_extract"
    endpoint_kwargs = {"extract_id": 1}
    needed_permission = perm_models.Permissions.EXTRACT_PUBLIC_ACCOUNT
    storage_folder = settings.LOCAL_STORAGE_DIR / settings.GCP_GDPR_EXTRACT_BUCKET / settings.GCP_GDPR_EXTRACT_FOLDER
    # - session
    # - current user
    # - get extract + user
    expected_num_queries = 3

    def test_download_public_account_extract(self, authenticated_client):
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(dateProcessed=datetime.datetime.utcnow())

        expected_data = randbytes(4096)
        with open(self.storage_folder / f"{extract.id}.zip", "wb") as fp:
            fp.write(expected_data)

        response = self.post_to_endpoint(
            authenticated_client, extract_id=extract.id, expected_num_queries=self.expected_num_queries
        )

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/zip"
        assert int(response.headers["Content-Length"]) == len(expected_data)
        assert response.headers["Content-Disposition"] == f'attachment; filename="{extract.user.full_name}.zip"'
        assert response.data == expected_data

    def test_extract_not_found(self, authenticated_client):
        expected_url = url_for("backoffice_web.gdpr_extract.list_gdpr_user_data_extract", _external=True)

        response = self.post_to_endpoint(
            authenticated_client, extract_id="0", expected_num_queries=self.expected_num_queries
        )

        assert response.status_code == 303
        assert response.location == expected_url
        redirection = authenticated_client.get(response.location)
        assert "L'extraction demandée n'existe pas ou a expiré" in html_parser.extract_alerts(redirection.data)

    def test_extract_expired(self, authenticated_client):
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            dateProcessed=datetime.datetime.utcnow(),
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=8),
        )

        expected_url = url_for("backoffice_web.gdpr_extract.list_gdpr_user_data_extract", _external=True)
        expected_data = randbytes(4096)
        with open(self.storage_folder / f"{extract.id}.zip", "wb") as fp:
            fp.write(expected_data)

        response = self.post_to_endpoint(
            authenticated_client, extract_id=extract.id, expected_num_queries=self.expected_num_queries
        )

        assert response.status_code == 303
        assert response.location == expected_url
        redirection = authenticated_client.get(response.location)
        assert "L'extraction demandée n'existe pas ou a expiré" in html_parser.extract_alerts(redirection.data)

    def test_no_file_in_bucket(self, authenticated_client):
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(dateProcessed=datetime.datetime.utcnow())

        expected_url = url_for("backoffice_web.gdpr_extract.list_gdpr_user_data_extract", _external=True)
        response = self.post_to_endpoint(
            authenticated_client, extract_id=extract.id, expected_num_queries=self.expected_num_queries
        )

        assert response.status_code == 303
        assert response.location == expected_url
        redirection = authenticated_client.get(response.location)
        assert "L'extraction demandée existe mais aucune archive ne lui est associée" in html_parser.extract_alerts(
            redirection.data
        )
