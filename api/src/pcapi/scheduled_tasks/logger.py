from enum import Enum


class CronStatus(Enum):
    STARTED = "started"
    ENDED = "ended"
    FAILED = "failed"

    def __str__(self) -> str:
        return self.value


def build_cron_log_message(name: str, status: CronStatus | None, duration: int | float | None = None) -> str:
    log_message = f"type=cron name={name} status={status}"

    if duration:
        log_message += f" duration={duration}"

    return log_message
