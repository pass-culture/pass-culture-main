from enum import Enum
import traceback


def build_job_log_message(name: str, error: str, stack: traceback):
    log_message = f"type=job name={name} status=failed"

    if error:
        log_message += f" error={error}"

    if traceback:
        list_stack = traceback.format_tb(stack)
        oneline_stack = ''.join(list_stack).replace('\n', ' ### ')
        log_message += f" stacktrace={oneline_stack}"

    return log_message
