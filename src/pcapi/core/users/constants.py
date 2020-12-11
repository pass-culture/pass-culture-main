from datetime import timedelta
from enum import Enum


RESET_PASSWORD_TOKEN_LIFE_TIME = timedelta(hours=24)
EMAIL_VALIDATION_TOKEN_LIFE_TIME = timedelta(hours=24)
ID_CHECK_TOKEN_LIFE_TIME = timedelta(days=1)

ELIGIBILITY_AGE = 18


class SuspensionReason(Enum):
    def __str__(self) -> str:
        return str(self.value)

    END_OF_CONTRACT = "end of contract"
    END_OF_ELIGIBILITY = "end of eligibility"
    FRAUD = "fraud"
    UPON_USER_REQUEST = "upon user request"
