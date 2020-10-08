from unittest.mock import patch

from pcapi.models import ApiErrors
from pcapi.utils.feature import feature_required


class FeatureRequiredTest:
    @patch('pcapi.utils.feature.feature_queries.is_active', return_value=True)
    def when_feature_is_activated_dont_raise_error(self, active_feature):
        # given
        @feature_required('feature')
        def decorated_function():
            return 'expected result'

        # when
        result = decorated_function()

        # then
        assert result == 'expected result'

    @patch('pcapi.utils.feature.feature_queries.is_active', return_value=False)
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
