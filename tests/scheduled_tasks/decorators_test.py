from unittest.mock import MagicMock, patch, call

from scheduled_tasks.decorators import cron_context, log_cron
from scheduled_tasks.logger import CronStatus


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


class LogCronTest:
    @patch('scheduled_tasks.decorators.time.time')
    @patch('scheduled_tasks.decorators.logger.info')
    @patch('scheduled_tasks.decorators.build_cron_log_message')
    def test_should_call_logger_with_builded_message(self, mock_cron_log_builder, mock_logger, mock_time):
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
        assert mock_logger.call_count == 2
        assert mock_cron_log_builder.call_count == 2
        assert mock_cron_log_builder.call_args_list == [call(name=decorated_function.__name__,
                                                             status=CronStatus.STARTED),
                                                        call(name=decorated_function.__name__,
                                                             status=CronStatus.ENDED,
                                                             duration=time_end - time_start)]
