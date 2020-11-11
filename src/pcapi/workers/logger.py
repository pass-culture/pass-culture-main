from enum import Enum
from typing import Optional


class JobStatus(Enum):
    STARTED = "started"
    ENDED = "ended"
    FAILED = "failed"

    def __str__(self):
        return self.value


def build_job_log_message(job: str, status: JobStatus, error: Optional[str] = None) -> str:
    log_message = f"type=job name={job} status={status}"

    if error:
        log_message += f" error={error}"

    return log_message
