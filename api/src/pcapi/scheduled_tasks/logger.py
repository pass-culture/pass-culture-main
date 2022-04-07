from enum import Enum


class CronStatus(Enum):
    STARTED = "started"
    ENDED = "ended"
    FAILED = "failed"

    def __str__(self):  # type: ignore [no-untyped-def]
        return self.value


def build_cron_log_message(name: str, status: CronStatus, duration: int = None):  # type: ignore [no-untyped-def]
    log_message = f"type=cron name={name} status={status}"

    if duration:
        log_message += f" duration={duration}"

    return log_message
