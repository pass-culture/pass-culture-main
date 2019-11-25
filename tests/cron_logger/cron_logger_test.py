import traceback

from scripts.cron_logger.cron_logger import build_cron_log_message
from scripts.cron_logger.cron_status import CronStatus


class CronLoggerMessageBuilderTest():
    def test_should_contains_the_log_type(self):
        # When
        message = build_cron_log_message(name='', status='')

        # Then
        assert 'type=cron' in message

    def test_should_contains_the_name(self):
        # When
        message = build_cron_log_message(name='generation_du_document_xml', status='')

        # Then
        assert 'name=generation_du_document_xml' in message

    def test_should_contains_the_status(self):
        # When
        message = build_cron_log_message(name='generation_du_document_xml', status=CronStatus.STARTED)

        # Then
        assert 'status=started' in message

    def test_should_contains_duration_field_when_given(self):
        # When
        message = build_cron_log_message(name='generation_du_document_xml', status=CronStatus.ENDED, duration=245)

        # Then
        assert 'status=ended duration=245' in message


    def test_should_contains_stacktrace_attribute_if_needed(self):
        # When
        try:
            raise Exception('Failed to execute')
        except Exception:
            trace = traceback.format_exc()
            message = build_cron_log_message(name='generation_du_document_xml',
                                             status=CronStatus.FAILED,
                                             traceback=trace)

        # Then
        assert "status=failed stacktrace=Traceback (most recent call last): " in message
