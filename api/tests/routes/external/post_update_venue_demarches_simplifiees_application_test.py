from unittest.mock import patch

import pytest

from pcapi import settings


class Returns202Test:
    @patch("pcapi.routes.external.bank_informations.bank_information_job.delay")
    @pytest.mark.usefixtures("db_session")
    def when_has_valid_provider_name_and_dossier_id(self, mock_bank_information_job, client):
        # Given
        data = {"dossier_id": "666", "procedure_id": settings.DMS_VENUE_PROCEDURE_ID_V4}

        # When
        response = client.post("/bank_informations/venue/application_update?token=good_token", form=data)

        # Then
        assert response.status_code == 202
        mock_bank_information_job.assert_called_once_with("666", settings.DMS_VENUE_PROCEDURE_ID_V4)


class Returns400Test:
    @patch("pcapi.routes.external.bank_informations.bank_information_job.delay")
    @pytest.mark.usefixtures("db_session")
    def when_has_not_dossier_in_request_form_data(self, mock_bank_information_job, client):
        # Given
        data = {"fake_key": "666", "procedure_id": settings.DMS_VENUE_PROCEDURE_ID_V4}

        # When
        response = client.post("/bank_informations/venue/application_update?token=good_token", form=data)

        # Then
        assert response.status_code == 400
        mock_bank_information_job.assert_not_called()


class Returns403Test:
    @patch("pcapi.routes.external.bank_informations.bank_information_job.delay")
    @pytest.mark.usefixtures("db_session")
    def when_has_not_a_token_in_url_params(self, mock_bank_information_job, client):
        # Given
        data = {"dossier_id": "666", "procedure_id": settings.DMS_VENUE_PROCEDURE_ID_V4}

        # When
        response = client.post("/bank_informations/venue/application_update", form=data)

        # Then
        assert response.status_code == 403
        mock_bank_information_job.assert_not_called()

    @patch("pcapi.routes.external.bank_informations.bank_information_job.delay")
    @pytest.mark.usefixtures("db_session")
    def when_token_in_url_params_is_not_good(self, mock_bank_information_job, client):
        # Given
        data = {"dossier_id": "666", "procedure_id": settings.DMS_VENUE_PROCEDURE_ID_V4}

        # When
        response = client.post("/bank_informations/venue/application_update?token=ABCD", form=data)

        # Then
        assert response.status_code == 403
        mock_bank_information_job.assert_not_called()
