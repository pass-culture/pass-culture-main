import logging
from unittest import mock

import pytest

from pcapi.core.offers import exceptions
from pcapi.core.users.factories import UserFactory

from tests.conftest import TestClient


class ValidateDistantImageTest:
    @pytest.mark.usefixtures("db_session")
    @mock.patch("pcapi.routes.pro.offers.get_distant_image")
    def test_ok(self, mock_get_distant_image, caplog, app):
        # Given
        caplog.set_level(logging.INFO)
        body = {"url": "https://example.com/exampleaaa.jpg"}
        user = UserFactory()
        auth_request = TestClient(app.test_client()).with_auth(email=user.email)
        mock_get_distant_image.return_value = b"aze"

        # When
        response = auth_request.post(
            "/offers/thumbnail-url-validation", json=body, headers={"origin": "http://localhost:3000"}
        )

        # Then
        assert len(caplog.records) == 0
        assert response.status_code == 200
        assert response.json == {"errors": [], "image": "data:image/png;base64,YXpl"}

    @pytest.mark.usefixtures("db_session")
    @mock.patch("pcapi.routes.pro.offers.get_distant_image")
    def test_unaccessible_file(self, mock_get_distant_image, caplog, app):
        # Given
        caplog.set_level(logging.INFO)
        body = {"url": "https://example.com/bla"}
        user = UserFactory()
        auth_request = TestClient(app.test_client()).with_auth(email=user.email)
        mock_get_distant_image.side_effect = exceptions.FailureToRetrieve()

        # When
        response = auth_request.post(
            "/offers/thumbnail-url-validation", json=body, headers={"origin": "http://localhost:3000"}
        )

        # Then
        assert response.status_code == 200
        assert (
            caplog.records[0].message
            == "When validating image at: https://example.com/bla, this error was encountered: FailureToRetrieve"
        )
        assert response.json == {
            "errors": [
                "Nous n’avons pas pu récupérer cette image; vous pouvez la télécharger "
                'puis l’importer depuis l’onglet "Importer"'
            ],
            "image": None,
        }

    @pytest.mark.usefixtures("db_session")
    @mock.patch("pcapi.routes.pro.offers.get_distant_image")
    def test_image_size_too_large(self, mock_get_distant_image, caplog, app):
        # Given
        caplog.set_level(logging.INFO)
        body = {"url": "https://example.com/wallpaper.jpg"}
        user = UserFactory()
        auth_request = TestClient(app.test_client()).with_auth(email=user.email)
        mock_get_distant_image.side_effect = exceptions.FileSizeExceeded(max_size=10_000_000)

        # When
        response = auth_request.post(
            "/offers/thumbnail-url-validation", json=body, headers={"origin": "http://localhost:3000"}
        )

        # Then
        assert response.status_code == 200
        assert (
            caplog.records[0].message
            == "When validating image at: https://example.com/wallpaper.jpg, this error was encountered: FileSizeExceeded"
        )
        assert response.json == {"errors": ["Utilisez une image dont le poids est inférieur à 10.0 MB"], "image": None}

    @pytest.mark.usefixtures("db_session")
    @mock.patch("pcapi.routes.pro.offers.get_distant_image")
    def test_image_too_small(self, mock_get_distant_image, caplog, app):
        # Given
        caplog.set_level(logging.INFO)
        body = {"url": "https://example.com/icon.jpeg"}
        user = UserFactory()
        auth_request = TestClient(app.test_client()).with_auth(email=user.email)
        mock_get_distant_image.side_effect = exceptions.ImageTooSmall(min_width=400, min_height=400)

        # When
        response = auth_request.post(
            "/offers/thumbnail-url-validation", json=body, headers={"origin": "http://localhost:3000"}
        )

        # Then
        assert response.status_code == 200
        assert (
            caplog.records[0].message
            == "When validating image at: https://example.com/icon.jpeg, this error was encountered: ImageTooSmall"
        )
        assert response.json == {
            "errors": ["Utilisez une image plus grande (supérieure à 400px par 400px)"],
            "image": None,
        }

    @pytest.mark.usefixtures("db_session")
    @mock.patch("pcapi.routes.pro.offers.get_distant_image")
    def test_wrong_format(self, mock_get_distant_image, caplog, app):
        # Given
        caplog.set_level(logging.INFO)
        body = {"url": "https://example.com/meme.gif"}
        user = UserFactory()
        auth_request = TestClient(app.test_client()).with_auth(email=user.email)
        mock_get_distant_image.side_effect = exceptions.UnacceptedFileType(
            accepted_types=(
                "png",
                "jpg",
                "jpeg",
            )
        )

        # When
        response = auth_request.post(
            "/offers/thumbnail-url-validation", json=body, headers={"origin": "http://localhost:3000"}
        )

        # Then
        assert response.status_code == 200
        assert (
            caplog.records[0].message
            == "When validating image at: https://example.com/meme.gif, this error was encountered: UnacceptedFileType"
        )
        assert response.json == {"errors": ["Utilisez un format png, jpg, jpeg"], "image": None}
