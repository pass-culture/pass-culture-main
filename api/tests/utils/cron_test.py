from unittest.mock import call
from unittest.mock import patch

import pytest

import pcapi.utils.cron as cron_decorators
from pcapi.models.feature import FeatureToggle


@pytest.mark.usefixtures("db_session")
class CronRequireFeatureTest:
    @pytest.mark.features(UPDATE_BOOKING_USED=True)
    def test_cron_require_feature(self):
        # Given
        @cron_decorators.cron_require_feature(FeatureToggle.UPDATE_BOOKING_USED)
        def decorated_function():
            return "expected result"

        # When
        result = decorated_function()

        # Then
        assert result == "expected result"

    @pytest.mark.features(UPDATE_BOOKING_USED=False)
    @patch("pcapi.utils.cron.logger.info")
    def when_feature_is_not_activated_raise_an_error(self, mock_logger):
        # Given
        @cron_decorators.cron_require_feature(FeatureToggle.UPDATE_BOOKING_USED)
        def decorated_function():
            return "expected result"

        # When
        result = decorated_function()

        # Then
        assert result is None
        mock_logger.assert_called_once_with("%s is not active", FeatureToggle.UPDATE_BOOKING_USED)


class LogCronTest:
    @patch("pcapi.utils.cron.time.time")
    @patch("pcapi.utils.cron.logger.info")
    @patch("pcapi.utils.cron.build_cron_log_message")
    def test_should_call_logger_with_builded_message(self, mock_cron_log_builder, mock_logger_info, mock_time):
        # Given
        @cron_decorators.log_cron_with_transaction
        def decorated_function(*args):
            return "expected result"

        time_start = 1582299799.985631
        time_end = 1582399799.9856312
        mock_time.side_effect = [time_start, time_end]

        # When
        result = decorated_function()

        # Then
        assert result == "expected result"
        assert mock_time.call_count == 2
        assert mock_logger_info.call_count == 2
        assert mock_cron_log_builder.call_count == 2
        assert mock_cron_log_builder.call_args_list == [
            call(name=decorated_function.__name__, status=cron_decorators.CronStatus.STARTED),
            call(
                name=decorated_function.__name__,
                status=cron_decorators.CronStatus.ENDED,
                duration=time_end - time_start,
            ),
        ]


class CronLoggerMessageBuilderTest:
    def test_should_contain_the_log_type(self):
        # When
        message = cron_decorators.build_cron_log_message(name="", status="")

        # Then
        assert "type=cron" in message

    def test_should_contain_the_name(self):
        # When
        message = cron_decorators.build_cron_log_message(name="generation_du_document_xml", status="")

        # Then
        assert "name=generation_du_document_xml" in message

    def test_should_contain_the_status(self):
        # When
        message = cron_decorators.build_cron_log_message(
            name="generation_du_document_xml", status=cron_decorators.CronStatus.STARTED
        )

        # Then
        assert "status=started" in message

    def test_should_contain_duration_field_when_given(self):
        # When
        message = cron_decorators.build_cron_log_message(
            name="generation_du_document_xml", status=cron_decorators.CronStatus.ENDED, duration=245
        )

        # Then
        assert "status=ended duration=245" in message
