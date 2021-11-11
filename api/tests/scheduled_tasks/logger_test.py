from pcapi.scheduled_tasks.logger import CronStatus
from pcapi.scheduled_tasks.logger import build_cron_log_message


class CronLoggerMessageBuilderTest:
    def test_should_contain_the_log_type(self):
        # When
        message = build_cron_log_message(name="", status="")

        # Then
        assert "type=cron" in message

    def test_should_contain_the_name(self):
        # When
        message = build_cron_log_message(name="generation_du_document_xml", status="")

        # Then
        assert "name=generation_du_document_xml" in message

    def test_should_contain_the_status(self):
        # When
        message = build_cron_log_message(name="generation_du_document_xml", status=CronStatus.STARTED)

        # Then
        assert "status=started" in message

    def test_should_contain_duration_field_when_given(self):
        # When
        message = build_cron_log_message(name="generation_du_document_xml", status=CronStatus.ENDED, duration=245)

        # Then
        assert "status=ended duration=245" in message
