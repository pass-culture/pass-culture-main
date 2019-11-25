from enum import Enum


class CronStatus(Enum):
    STARTED = 'started'
    ENDED = 'ended'
    FAILED = 'failed'

    def __str__(self):
        return self.value
