from pathlib import Path
from unittest.mock import patch

import pytest
from requests import Response

from pcapi.core.testing import override_settings

import tests
from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


class VerifyIdentityDocumentTest:
    IMAGES_DIR = Path(tests.__path__[0]) / "files"

    @override_settings(ID_CHECK_MIDDLEWARE_TOKEN="fake_token")
    @patch("pcapi.core.users.api.delete_object")
    @patch("pcapi.core.users.api._get_identity_document_informations")
    @patch("pcapi.connectors.beneficiaries.id_check_middleware.requests.post")
    def test_ask_for_document_verification(
        self,
        mocked_middleware_post,
        mocked_get_identity_document_informations,
        mocked_delete_object,
        app,
    ):
        identity_document = (self.IMAGES_DIR / "mouette_small.jpg").read_bytes()
        storage_path = "fake_storage_path.jpg"
        mocked_get_identity_document_informations.return_value = ("fake@email.com", identity_document)
        mocked_response = Response()
        mocked_response.status_code = 200
        mocked_response._content = b'{"code": "registration:completed"}'
        mocked_middleware_post.return_value = mocked_response
        json_data = {"image_storage_path": storage_path}
        test_client = TestClient(app.test_client())
        response = test_client.post(
            "/cloud-tasks/verify_identity_document",
            json=json_data,
            headers={"AUTHORIZATION": "Bearer cloud-task-bearer-token"},
        )

        assert response.status_code == 204
        mocked_get_identity_document_informations.assert_called_once_with(storage_path)
        mocked_middleware_post.assert_called_once_with(
            "https://id-check-middleware-dev.passculture.app/simple-registration-process",
            headers={
                "X-Authentication": "fake_token",
            },
            data={"email": "fake@email.com"},
            files=[("file", identity_document)],
        )
        mocked_delete_object.assert_called_once_with(storage_path)

    def test_bad_requests_parameters(self, app):
        test_client = TestClient(app.test_client())
        response = test_client.post("/cloud-tasks/verify_identity_document")

        assert response.status_code == 400
