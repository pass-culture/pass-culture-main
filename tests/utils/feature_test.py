from datetime import datetime
from unittest.mock import patch

from models import ApiErrors
from utils.feature import feature_required, get_feature_end_of_quarantine_date


class FeatureRequiredTest:
    @patch('utils.feature.feature_queries.is_active', return_value=True)
    def when_feature_is_activated_dont_raise_error(self, active_feature):
        # given
        @feature_required('feature')
        def decorated_function():
            return 'expected result'

        # when
        result = decorated_function()

        # then
        assert result == 'expected result'

    @patch('utils.feature.feature_queries.is_active', return_value=False)
    def when_feature_is_not_activated_raise_an_error(self, not_active_feature):
        # given
        @feature_required('feature')
        def decorated_function():
            return 'expected result'

        # when
        try:
            decorated_function()

        # then
        except ApiErrors as error:
            assert error.status_code == 403
            assert error.errors == {'Forbidden': ["You don't have access to this page or resource"]}


class GetFeatureEndOfQuarantineDateTest:
    @patch.dict('os.environ', {
        'END_OF_QUARANTINE_DATE': '2020-04-05'
    })
    def test_should_parse_date_from_env_variable_to_datetime(self):
        # Given
        expected_date = datetime(year=2020, month=4, day=5)

        # When
        end_of_quarantine_date = get_feature_end_of_quarantine_date()

        # Then
        assert end_of_quarantine_date == expected_date

    @patch.dict('os.environ', {})
    def test_should_parse_default_date_to_datetime_when_no_env_variable_found(self):
        # Given
        expected_date = datetime(year=2020, month=4, day=25)

        # When
        end_of_quarantine_date = get_feature_end_of_quarantine_date()

        # Then
        assert end_of_quarantine_date == expected_date
