import datetime
import os
from random import randbytes

import pytest
from flask import url_for

from pcapi import settings
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.routes.backoffice.filters import format_date
from pcapi.utils import date as date_utils

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
    gdpr_2 = users_factories.GdprUserDataExtractBeneficiaryFactory(dateProcessed=date_utils.get_naive_utc_now())
    gdpr_3 = users_factories.GdprUserDataExtractBeneficiaryFactory()
    gdpr_4 = users_factories.GdprUserDataExtractBeneficiaryFactory()
    gdpr_5 = users_factories.GdprUserDataExtractBeneficiaryFactory(
        dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=8)
    )
    return gdpr_5, gdpr_4, gdpr_3, gdpr_2, gdpr_1


class ListGdprUserExtractDataTest(GetEndpointHelper):
    endpoint = "backoffice_web.gdpr_extract.list_gdpr_user_data_extract"
    needed_permission = perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT

    # Use assert_num_queries() instead of assert_no_duplicated_queries() which does not detect one extra query caused
    # by a field added in the jinja template.
    # - fetch session +user (1 query)
    # - fetch gdpr_data_extract
    expected_num_queries = 2

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
            rows[0]["Prénom et nom du jeune"]
            == f"{list_of_gdpr_user_extract_data[1].user.full_name} ({str(list_of_gdpr_user_extract_data[1].user.id)})"
        )
        assert rows[0]["Auteur de la demande"] == list_of_gdpr_user_extract_data[1].authorUser.full_name

        assert rows[2]["État de la demande"] == "prête"

        for row in rows:
            assert list_of_gdpr_user_extract_data[4].id not in row

    def test_display_download_button_when_extract_is_processed(self, authenticated_client):
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(dateProcessed=date_utils.get_naive_utc_now())

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        expected_action_target = url_for("backoffice_web.gdpr_extract.download_gdpr_extract", extract_id=extract.id)

        assert b'<i class="bi bi-cloud-download-fill"></i>' in response.data
        assert expected_action_target.encode("utf-8") in response.data

    def test_hide_download_button_when_extract_is_not_processed(self, authenticated_client):
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        expected_action_target = url_for("backoffice_web.gdpr_extract.download_gdpr_extract", extract_id=extract.id)

        assert b'<i class="bi bi-cloud-download-fill"></i>' not in response.data
        assert (
            b"""<i class="bi bi-trash"
             style="opacity: 0.5"></i>"""
            in response.data
        )
        assert expected_action_target.encode("utf-8") not in response.data


class DownloadPublicAccountExtractTest(PostEndpointHelper, StorageFolderManager):
    endpoint = "backoffice_web.gdpr_extract.download_gdpr_extract"
    endpoint_kwargs = {"extract_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT
    storage_folder = settings.LOCAL_STORAGE_DIR / settings.GCP_GDPR_EXTRACT_BUCKET / settings.GCP_GDPR_EXTRACT_FOLDER
    # - session + user
    # - get extract + user
    expected_num_queries = 2

    def test_download_public_account_extract(self, authenticated_client):
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(dateProcessed=date_utils.get_naive_utc_now())

        expected_data = randbytes(4096)
        with open(self.storage_folder / f"{extract.id}.zip", "wb") as fp:
            fp.write(expected_data)

        response = self.post_to_endpoint(
            authenticated_client, extract_id=extract.id, expected_num_queries=self.expected_num_queries
        )

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/zip"
        assert int(response.headers["Content-Length"]) == len(expected_data)
        assert response.headers["Content-Disposition"] == f'attachment; filename="{extract.user.email}.zip"'
        assert response.data == expected_data

    def test_extract_not_found(self, authenticated_client):
        expected_url = url_for("backoffice_web.gdpr_extract.list_gdpr_user_data_extract")

        response = self.post_to_endpoint(
            authenticated_client, extract_id="0", expected_num_queries=self.expected_num_queries
        )

        assert response.status_code == 303
        assert response.location == expected_url
        redirection = authenticated_client.get(response.location)
        assert "L'extraction demandée n'existe pas ou a expiré" in html_parser.extract_alerts(redirection.data)

    def test_extract_expired(self, authenticated_client):
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            dateProcessed=date_utils.get_naive_utc_now(),
            dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=8),
        )

        expected_url = url_for("backoffice_web.gdpr_extract.list_gdpr_user_data_extract")
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
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(dateProcessed=date_utils.get_naive_utc_now())

        expected_url = url_for("backoffice_web.gdpr_extract.list_gdpr_user_data_extract")
        response = self.post_to_endpoint(
            authenticated_client, extract_id=extract.id, expected_num_queries=self.expected_num_queries
        )

        assert response.status_code == 303
        assert response.location == expected_url
        redirection = authenticated_client.get(response.location)
        assert "L'extraction demandée existe mais aucune archive ne lui est associée" in html_parser.extract_alerts(
            redirection.data
        )


class DeleteGdprUserExtractTest(PostEndpointHelper, StorageFolderManager):
    endpoint = "backoffice_web.gdpr_extract.delete_gdpr_user_data_extract"
    endpoint_kwargs = {"gdpr_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT
    storage_folder = settings.LOCAL_STORAGE_DIR / settings.GCP_GDPR_EXTRACT_BUCKET / settings.GCP_GDPR_EXTRACT_FOLDER

    def test_delete_gdpr_user_extract(self, authenticated_client):
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(dateProcessed=date_utils.get_naive_utc_now())
        with open(self.storage_folder / f"{extract.id}.zip", "wb"):
            pass

        response = self.post_to_endpoint(authenticated_client, gdpr_id=extract.id)
        assert response.status_code == 302

        expected_url = url_for("backoffice_web.gdpr_extract.list_gdpr_user_data_extract")
        assert response.location == expected_url

        assert db.session.query(users_models.GdprUserDataExtract).count() == 0
        assert len(os.listdir(self.storage_folder)) == 0

        response = authenticated_client.get(response.location)
        assert "L'extraction de données a bien été effacée." in html_parser.extract_alert(response.data)

    def test_delete_gdpr_user_extract_still_processing(self, authenticated_client):
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory()

        response = self.post_to_endpoint(authenticated_client, gdpr_id=extract.id)
        expected_url = url_for("backoffice_web.gdpr_extract.list_gdpr_user_data_extract")
        assert response.location == expected_url

        response = authenticated_client.get(response.location)
        assert "L'extraction de données est toujours en cours pour cet utilisateur." in html_parser.extract_alert(
            response.data
        )

    def test_delete_gdpr_user_extract_id_gdpr_does_not_exist(self, authenticated_client):
        response = self.post_to_endpoint(authenticated_client, gdpr_id=0)

        expected_url = url_for("backoffice_web.gdpr_extract.list_gdpr_user_data_extract")
        assert response.location == expected_url

        response = authenticated_client.get(response.location)
        assert "L'extrait demandé n'existe pas." in html_parser.extract_alert(response.data)

    def test_delete_gdpr_user_extract_ready_but_without_zip_file(self, authenticated_client):
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(dateProcessed=date_utils.get_naive_utc_now())

        response = self.post_to_endpoint(authenticated_client, gdpr_id=extract.id)
        assert response.status_code == 302

        expected_url = url_for("backoffice_web.gdpr_extract.list_gdpr_user_data_extract")
        assert response.location == expected_url

        assert db.session.query(users_models.GdprUserDataExtract).count() == 0

        response = authenticated_client.get(response.location)
        assert "L'extraction de données a bien été effacée." in html_parser.extract_alert(response.data)
