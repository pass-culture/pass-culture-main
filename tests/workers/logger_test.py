from pcapi.workers.logger import JobStatus
from pcapi.workers.logger import build_job_log_message


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
