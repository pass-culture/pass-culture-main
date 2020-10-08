from unittest.mock import patch

from pcapi.workers.beneficiary_job import beneficiary_job


@patch('pcapi.workers.beneficiary_job.create_beneficiary_from_application.execute')
def test_calls_use_case(mocked_create_beneficiary_use_case):
    # Given
    application_id = 5

    # When
    beneficiary_job(application_id)

    # Then
    mocked_create_beneficiary_use_case.assert_called_once_with(application_id)
