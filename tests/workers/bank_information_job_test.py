from workers.save_offerer_bank_informations import pc_synchronize_new_bank_informations
from unittest.mock import patch, call

@patch('workers.save_offerer_bank_informations.launch_provider_on_data')
def when_provider_name_is_offerer_should_launch_OffererBankInformationProvider(mock_launch_provider_data):
    # Given
    application_id = 'id'
    provider_name = 'offerer'

    # When
    pc_synchronize_new_bank_informations(application_id, provider_name)

    # Then
    assert mock_launch_provider_data.call_args_list == [
        call("OffererBankInformationProvider", ['id'])
    ]


@patch('workers.save_offerer_bank_informations.launch_provider_on_data')
def when_provider_name_is_venue_should_launch_VenueBankInformationProvider(mock_launch_provider_data):
    # Given
    application_id = 'id'
    provider_name = 'venue'

    # When
    pc_synchronize_new_bank_informations(application_id, provider_name)

    # Then
    assert mock_launch_provider_data.call_args_list == [
        call("VenueBankInformationProvider", ['id'])
    ]

@patch('workers.save_offerer_bank_informations.launch_provider_on_data')
def when_provider_name_is_another_should_launch_nothing(mock_launch_provider_data):
    # Given
    application_id = ''
    provider_name = ''

    # When
    pc_synchronize_new_bank_informations(application_id, provider_name)

    # Then
    mock_launch_provider_data.assert_not_called()