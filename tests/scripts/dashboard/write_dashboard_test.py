from unittest import mock
from unittest.mock import MagicMock
from unittest.mock import patch

from pcapi.scripts.dashboard.write_dashboard import _get_departement_code
from pcapi.scripts.dashboard.write_dashboard import write_dashboard
from pcapi.scripts.dashboard.write_dashboard import write_dashboard_worksheet


class WriteDashboardTest:
    def test_should_connect_to_spreadsheet(self):
        # Given
        mock_connection = MagicMock()
        mock_write_worksheet = MagicMock()

        # When
        write_dashboard(mock_connection, mock_write_worksheet)

        # Then
        mock_connection.assert_called_once()

    def test_should_write_one_worksheet_per_experimentation_departement_and_one_for_global(self):
        # Given
        mock_connection = MagicMock()
        mock_write_worksheet = MagicMock()
        experimentation_departements = ['01', '02']

        # When
        write_dashboard(mock_connection, mock_write_worksheet, experimentation_departements)

        # Then
        mock_write_worksheet.assert_has_calls(
            [
                mock.call(mock_connection.return_value, '01'),
                mock.call(mock_connection.return_value, '02'),
                mock.call(mock_connection.return_value, 'Global')
            ]
        )


class WriteDashboardWorksheetTest:
    @patch('pcapi.scripts.dashboard.write_dashboard._write_finance_section')
    @patch('pcapi.scripts.dashboard.write_dashboard._write_diversification_section')
    @patch('pcapi.scripts.dashboard.write_dashboard._write_usage_section')
    @patch('pcapi.scripts.dashboard.write_dashboard._initialize_worksheet')
    def test_initializes_worksheet_within_given_spreadsheet(self, initialize_worksheet, write_usage_section,
                                                            write_diversification_section, write_finance_section):
        # Given
        initialize_worksheet.return_value = MagicMock()
        write_usage_section.return_value = 5
        write_diversification_section.return_value = 6
        spreadsheet = MagicMock()

        # When
        write_dashboard_worksheet(spreadsheet, '08')

        # Then
        initialize_worksheet.assert_called_once_with(spreadsheet, '08')

    @patch('pcapi.scripts.dashboard.write_dashboard._write_finance_section')
    @patch('pcapi.scripts.dashboard.write_dashboard._write_diversification_section')
    @patch('pcapi.scripts.dashboard.write_dashboard._write_usage_section')
    @patch('pcapi.scripts.dashboard.write_dashboard._initialize_worksheet')
    def test_writes_worksheet_title(self, initialize_worksheet, write_usage_section, write_diversification_section,
                                    write_finance_section):
        # Given
        worksheet = MagicMock()
        initialize_worksheet.return_value = worksheet
        write_usage_section.return_value = 5
        write_diversification_section.return_value = 6
        spreadsheet = worksheet

        # When
        write_dashboard_worksheet(spreadsheet, '08')

        # Then
        worksheet.update_value.assert_called_once_with('A1', 'TABLEAU DE BORD PASS CULTURE')

    @patch('pcapi.scripts.dashboard.write_dashboard._write_finance_section')
    @patch('pcapi.scripts.dashboard.write_dashboard._write_diversification_section')
    @patch('pcapi.scripts.dashboard.write_dashboard._write_usage_section')
    @patch('pcapi.scripts.dashboard.write_dashboard._initialize_worksheet')
    def test_writes_usage_section_for_departement_starting_on_line_4(self, initialize_worksheet, write_usage_section,
                                                                     write_diversification_section,
                                                                     write_finance_section):
        # Given
        worksheet = MagicMock()
        initialize_worksheet.return_value = worksheet
        write_usage_section.return_value = 5
        write_diversification_section.return_value = 6
        spreadsheet = worksheet

        # When
        write_dashboard_worksheet(spreadsheet, '08')

        # Then
        write_usage_section.assert_called_once_with('08', worksheet, 4)

    @patch('pcapi.scripts.dashboard.write_dashboard._write_finance_section')
    @patch('pcapi.scripts.dashboard.write_dashboard._write_diversification_section')
    @patch('pcapi.scripts.dashboard.write_dashboard._write_usage_section')
    @patch('pcapi.scripts.dashboard.write_dashboard._initialize_worksheet')
    def test_writes_diversification_section_for_departement_starting_on_line_5(self, initialize_worksheet,
                                                                               write_usage_section,
                                                                               write_diversification_section,
                                                                               write_finance_section):
        # Given
        worksheet = MagicMock()
        initialize_worksheet.return_value = worksheet
        write_usage_section.return_value = 5
        write_diversification_section.return_value = 6
        spreadsheet = worksheet

        # When
        write_dashboard_worksheet(spreadsheet, '08')

        # Then
        write_diversification_section.assert_called_once_with('08', worksheet, 5)

    @patch('pcapi.scripts.dashboard.write_dashboard._write_finance_section')
    @patch('pcapi.scripts.dashboard.write_dashboard._write_diversification_section')
    @patch('pcapi.scripts.dashboard.write_dashboard._write_usage_section')
    @patch('pcapi.scripts.dashboard.write_dashboard._initialize_worksheet')
    def test_writes_finance_section_for_departement_starting_on_line_6(self, initialize_worksheet, write_usage_section,
                                                                       write_diversification_section,
                                                                       write_finance_section):
        # Given
        worksheet = MagicMock()
        initialize_worksheet.return_value = worksheet
        write_usage_section.return_value = 5
        write_diversification_section.return_value = 6
        spreadsheet = worksheet

        # When
        write_dashboard_worksheet(spreadsheet, '08')

        # Then
        write_finance_section.assert_called_once_with('08', worksheet, 6)


class GetDepartementCodeTest:
    def test_should_return_None_when_tab_name_is_Global(self):
        # When
        departement_code = _get_departement_code('Global')

        # Then
        assert departement_code is None

    def test_should_return_input_when_tab_name_is_not_Global(self):
        # When
        departement_code = _get_departement_code('06')

        # Then
        assert departement_code == '06'
