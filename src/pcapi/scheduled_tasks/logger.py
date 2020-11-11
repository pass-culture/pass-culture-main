from enum import Enum


class CronStatus(Enum):
    STARTED = "started"
    ENDED = "ended"
    FAILED = "failed"

    def __str__(self):
        return self.value


def build_cron_log_message(name: str, status: CronStatus, duration: int = None):
    log_message = f"type=cron name={name} status={status}"

    if duration:
        log_message += f" duration={duration}"

    return log_message
