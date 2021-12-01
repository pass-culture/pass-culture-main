from unittest.mock import patch

from pcapi import settings
from pcapi.workers.bank_information_job import bank_information_job


class synchronizeBankInformationsTest:
    @patch("pcapi.workers.bank_information_job.save_offerer_bank_informations.execute")
    def when_provider_name_is_offerer_should_save_offerer_bank_informations(self, mock_save_offerer_bank_informations):
        # Given
        application_id = "id"
        provider_name = "offerer"

        # When
        bank_information_job(application_id, provider_name, settings.DMS_VENUE_PROCEDURE_ID)

        # Then
        mock_save_offerer_bank_informations.assert_called_once_with("id")

    @patch("pcapi.workers.bank_information_job.save_venue_bank_informations.execute")
    def when_provider_name_is_venue_should_save_venue_bank_informations(self, mock_save_venue_bank_informations):
        # Given
        application_id = "id"
        provider_name = "venue"

        # When
        bank_information_job(application_id, provider_name, settings.DMS_VENUE_PROCEDURE_ID)

        # Then
        mock_save_venue_bank_informations.assert_called_once_with("id", settings.DMS_VENUE_PROCEDURE_ID)

    @patch("pcapi.workers.bank_information_job.save_venue_bank_informations.execute")
    @patch("pcapi.workers.bank_information_job.save_offerer_bank_informations.execute")
    def when_provider_name_is_another_should_launch_nothing(
        self, mock_save_offerer_bank_informations, mock_save_venue_bank_informations
    ):
        # Given
        application_id = ""
        provider_name = ""

        # When
        bank_information_job(application_id, provider_name, settings.DMS_VENUE_PROCEDURE_ID)

        # Then
        mock_save_offerer_bank_informations.assert_not_called()
        mock_save_venue_bank_informations.assert_not_called()
