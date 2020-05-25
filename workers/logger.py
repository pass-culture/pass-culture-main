from enum import Enum


def build_job_log_message(name: str, error: str):
    log_message = f"type=job name={name} status=failed"

    if error:
        log_message += f" error={error}"

    return log_message
