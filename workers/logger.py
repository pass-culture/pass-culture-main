from enum import Enum


def build_job_log_message(name: str, traceback=None):
    log_message = f"type=job name={name} type=error"

    if traceback:
        oneline_stack = ''.join(traceback).replace('\n', ' ### ')
        log_message += f" stacktrace={oneline_stack}"

    return log_message
