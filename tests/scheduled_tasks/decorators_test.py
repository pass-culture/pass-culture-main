from unittest.mock import MagicMock
from unittest.mock import call
from unittest.mock import patch

from pcapi.scheduled_tasks.decorators import cron_context
from pcapi.scheduled_tasks.decorators import cron_require_feature
from pcapi.scheduled_tasks.decorators import log_cron
from pcapi.scheduled_tasks.logger import CronStatus


class CronContextTest:
    def test_should_give_app_context_to_decorated_function(self):
        # Given
        @cron_context
        def decorated_function(*args):
            return 'expected result'

        application = MagicMock()
        application.app_context.return_value = MagicMock()

        # When
        result = decorated_function(application)

        # Then
        assert result == 'expected result'
        application.app_context.assert_called_once()


class CronRequireFeatureTest:
    @patch('pcapi.scheduled_tasks.decorators.feature_queries.is_active', return_value=True)
    def test_cron_require_feature(self, mock_active_feature):
        # Given
        @cron_require_feature('feature')
        def decorated_function():
            return 'expected result'

        # When
        result = decorated_function()

        # Then
        assert result == 'expected result'

    @patch('pcapi.scheduled_tasks.decorators.logger.info')
    @patch('pcapi.scheduled_tasks.decorators.feature_queries.is_active', return_value=False)
    def when_feature_is_not_activated_raise_an_error(self, mock_not_active_feature, mock_logger):
        # Given
        @cron_require_feature('feature')
        def decorated_function():
            return 'expected result'

        # When
        result = decorated_function()

        # Then
        assert result is None
        mock_logger.assert_called_once_with('feature is not active')


class LogCronTest:
    @patch('pcapi.scheduled_tasks.decorators.time.time')
    @patch('pcapi.scheduled_tasks.decorators.logger.info')
    @patch('pcapi.scheduled_tasks.decorators.build_cron_log_message')
    def test_should_call_logger_with_builded_message(self, mock_cron_log_builder, mock_logger_info, mock_time):
        # Given
        @log_cron
        def decorated_function(*args):
            return 'expected result'

        time_start = 1582299799.985631
        time_end = 1582399799.9856312
        mock_time.side_effect = [time_start, time_end]

        # When
        result = decorated_function()

        # Then
        assert result == 'expected result'
        assert mock_time.call_count == 2
        assert mock_logger_info.call_count == 2
        assert mock_cron_log_builder.call_count == 2
        assert mock_cron_log_builder.call_args_list == [call(name=decorated_function.__name__,
                                                             status=CronStatus.STARTED),
                                                        call(name=decorated_function.__name__,
                                                             status=CronStatus.ENDED,
                                                             duration=time_end - time_start)]
