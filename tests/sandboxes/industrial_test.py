from unittest import mock
from unittest.mock import patch, MagicMock

from sandboxes.scripts.save_sandbox import save_sandbox
from sandboxes.scripts.testcafe_helpers import get_all_getters
from tests.conftest import clean_database
from tests.model_creators.provider_creators import save_counts, assert_created_counts
from tests.sandboxes.mock_adresse_api import MOCK_ADRESSE_API_RESPONSE
from utils.logger import logger


@patch('sandboxes.scripts.utils.ban.requests.get')
@clean_database
def test_save_industrial_sandbox(mock_request, app):
    # given
    response_return_value = MagicMock(status_code=200, text='')
    response_return_value.json = MagicMock(side_effect=MOCK_ADRESSE_API_RESPONSE)
    mock_request.return_value = response_return_value

    save_counts()
    logger_info = logger.info
    logger.info = lambda o: None

    # when
    save_sandbox('industrial')

    # then
    assert_created_counts(
        ApiKey=13,
        Booking=43,
        Deposit=8,
        Mediation=84,
        Offer=106,
        Offerer=14,
        Product=155,
        Recommendation=84,
        StockSQLEntity=102,
        UserSQLEntity=53,
        UserOfferer=125,
        Venue=22,
    )

    # teardown
    logger.info = logger_info


@patch('sandboxes.scripts.utils.ban.requests.get')
@clean_database
def test_all_helpers_are_returning_actual_sandbox_data(mock_request, app):
    # given
    response_return_value = MagicMock(status_code=200, text='')
    response_return_value.json = MagicMock(side_effect=MOCK_ADRESSE_API_RESPONSE)
    mock_request.return_value = response_return_value
    save_sandbox('industrial')

    # when
    helpers = get_all_getters()

    # then
    for k, v in helpers.items():
        assert v is not None, f"Getter '{k}' is not returning anything"


class AlgoliaIndexingTest:
    @patch.dict('os.environ', {'ALGOLIA_TRIGGER_INDEXATION': '0'})
    @patch('sandboxes.scripts.creators.industrial.create_industrial_algolia_objects.clear_index')
    @patch('sandboxes.scripts.creators.industrial.create_industrial_algolia_objects.delete_all_indexed_offers')
    @patch('sandboxes.scripts.creators.industrial.create_industrial_algolia_objects.process_eligible_offers')
    @patch('sandboxes.scripts.utils.ban.requests.get')
    @clean_database
    def test_should_not_index_offers_to_algolia_when_indexation_is_disabled(self,
                                                                            mock_request,
                                                                            mock_process_eligible_offers,
                                                                            mock_delete_all_indexed_offers,
                                                                            mock_clear_index,
                                                                            app):
        # Given
        response_return_value = MagicMock(status_code=200, text='')
        response_return_value.json = MagicMock(side_effect=MOCK_ADRESSE_API_RESPONSE)
        mock_request.return_value = response_return_value

        # When
        save_sandbox('industrial')

        # Then
        mock_delete_all_indexed_offers.assert_not_called()
        mock_clear_index.assert_not_called()
        mock_process_eligible_offers.assert_not_called()

    @patch.dict('os.environ', {'ALGOLIA_TRIGGER_INDEXATION': '1'})
    @patch('sandboxes.scripts.creators.industrial.create_industrial_algolia_objects.delete_all_indexed_offers')
    @patch('sandboxes.scripts.creators.industrial.create_industrial_algolia_objects.clear_index')
    @patch('sandboxes.scripts.creators.industrial.create_industrial_algolia_objects.process_eligible_offers')
    @patch('sandboxes.scripts.utils.ban.requests.get')
    @clean_database
    def test_should_index_offers_to_algolia_when_indexation_is_enabled(self,
                                                                       mock_request,
                                                                       mock_process_eligible_offers,
                                                                       mock_delete_all_indexed_offers,
                                                                       mock_clear_index,
                                                                       app):
        # Given
        response_return_value = MagicMock(status_code=200, text='')
        response_return_value.json = MagicMock(side_effect=MOCK_ADRESSE_API_RESPONSE)
        mock_request.return_value = response_return_value

        # When
        save_sandbox('industrial')

        # Then
        mock_delete_all_indexed_offers.assert_called()
        mock_clear_index.assert_called()
        mock_process_eligible_offers.assert_called()
