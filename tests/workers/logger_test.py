import sys

from workers.logger import build_job_log_message, JobStatus


class JobLoggerMessageBuilderTest():
    def test_should_have_job_as_log_type(self):
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

    def test_should_contain_stacktrace_attribute_when_the_job_raises_and_exception(self):
        # given
        try:
            raise Exception('Failed to execute')
        except Exception:
            # traceback can only be created in an except block
            traceback = sys.exc_info()[2]

        # When
        message = build_job_log_message(job='generation_du_document_xml',
                                        status=JobStatus.FAILED,
                                        error='my error',
                                        stack=traceback)

        # Then
        assert "status=failed error=my error stacktrace=" in message
        assert "raise Exception('Failed to execute')" in message
