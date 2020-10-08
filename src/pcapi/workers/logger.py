from typing import Optional
from enum import Enum
import traceback
from types import TracebackType


class JobStatus(Enum):
    STARTED = 'started'
    ENDED = 'ended'
    FAILED = 'failed'

    def __str__(self):
        return self.value


def build_job_log_message(job: str, status: JobStatus, error: Optional[str] = None, stack: Optional[TracebackType] = None) -> str:
    log_message = f"type=job name={job} status={status}"

    if error:
        log_message += f" error={error}"

    if stack:
        list_stack = traceback.format_tb(stack)
        oneline_stack = ''.join(list_stack).replace('\n', ' ### ')
        log_message += f" stacktrace={oneline_stack}"

    return log_message
