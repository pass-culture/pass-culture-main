import traceback
from unittest.mock import patch

from workers.logger import build_job_log_message, JobStatus


class JobLoggerMessageBuilderTest():
    def test_should_contain_the_log_type(self):
        # When
        message = build_job_log_message(job='', status='')

        # Then
        assert 'type=job' in message

    def test_should_contain_the_name(self):
        # When
        message = build_job_log_message(job='my job name', status='')

        # Then
        assert 'name=my job name' in message

    def test_should_contain_the_status(self):
        # When
        message = build_job_log_message(job='my job name', status=JobStatus.STARTED)

        # Then
        assert 'status=started' in message

    @patch('workers.logger.traceback.format_tb')
    def test_should_contain_stacktrace_attribute_if_needed(self, mock_format_traceback):
        # given
        mock_format_traceback.return_value = ['oups ! ']

        # When
        try:
            raise Exception('Failed to execute')
        except Exception:
            message = build_job_log_message(job='generation_du_document_xml',
                                             status=JobStatus.FAILED,
                                             error= 'my error',
                                             stack=traceback)

        # Then
        assert "status=failed error=my error stacktrace=oups ! " in message
