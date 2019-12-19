from unittest.mock import patch, MagicMock

from sandboxes.scripts.save_sandbox import save_sandbox
from sandboxes.scripts.testcafe_helpers import get_all_getters
from tests.conftest import clean_database
from tests.sandboxes.mock_adresse_api import MOCK_ADRESSE_API_RESPONSE
from tests.model_creators.provider_creators import saveCounts, assertCreatedCounts
from utils.logger import logger


@patch('sandboxes.scripts.utils.ban.requests.get')
@clean_database
def test_save_industrial_sandbox(mock_request, app):
    # given
    response_return_value = MagicMock(status_code=200, text='')
    response_return_value.json = MagicMock(side_effect=MOCK_ADRESSE_API_RESPONSE)
    mock_request.return_value = response_return_value

    saveCounts()
    logger_info = logger.info
    logger.info = lambda o: None

    # when
    save_sandbox('industrial')

    # then
    assertCreatedCounts(
        ApiKey=13,
        Booking=42,
        Deposit=8,
        Mediation=86,
        Offer=106,
        Offerer=14,
        Product=148,
        Recommendation=101,
        Stock=102,
        User=53,
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
