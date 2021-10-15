from datetime import timedelta
from enum import Enum

from pcapi import settings


RESET_PASSWORD_TOKEN_LIFE_TIME = timedelta(hours=24)
RESET_PASSWORD_TOKEN_LIFE_TIME_EXTENDED = timedelta(days=30)
EMAIL_VALIDATION_TOKEN_LIFE_TIME = timedelta(hours=24)
EMAIL_CHANGE_TOKEN_LIFE_TIME = timedelta(hours=24)
ID_CHECK_TOKEN_LIFE_TIME = timedelta(hours=settings.ID_CHECK_TOKEN_LIFE_TIME_HOURS)
PHONE_VALIDATION_TOKEN_LIFE_TIME = timedelta(minutes=10)

ELIGIBILITY_AGE_18 = 18
ELIGIBILITY_UNDERAGE_RANGE = [15, 16, 17]

ACCOUNT_CREATION_MINIMUM_AGE = 15

WHITELISTED_COUNTRY_PHONE_CODES = {
    33,  # France métropolitaine
    590,  # Guadeloupe
    596,  # Martinique
    594,  # Guyane
    262,  # Réunion
    508,  # Saint-Pierre-et-Miquelon
    262,  # Mayotte
    590,  # Saint-Barthélémy
    590,  # Saint-Martin
    681,  # Wallis-et-Futuna
    689,  # Tahiti
    687,  # Nouvelle-Calédonie
}

EDUCONNECT_SAML_REQUEST_ID_TTL = 24 * 60 * 60  # 1 day in seconds


class SuspensionReason(Enum):
    def __str__(self) -> str:
        return str(self.value)

    # If you add a new reason, update `suspend_account()` to cancel
    # bookings if applicable.
    END_OF_CONTRACT = "end of contract"
    END_OF_ELIGIBILITY = "end of eligibility"
    FRAUD = "fraud"
    UPON_USER_REQUEST = "upon user request"


SUSPENSION_REASON_CHOICES = (
    (SuspensionReason.END_OF_ELIGIBILITY, "fin d'éligibilité"),
    (SuspensionReason.END_OF_CONTRACT, "fin de contrat"),
    (SuspensionReason.FRAUD, "fraude"),
    (SuspensionReason.UPON_USER_REQUEST, "demande de l'utilisateur"),
)

assert set(_t[0] for _t in SUSPENSION_REASON_CHOICES) == set(SuspensionReason)

PHONE_PREFIX_BY_DEPARTEMENT_CODE = {
    "971": "590",  # Guadeloupe
    "972": "596",  # Martinique
    "973": "594",  # Guyane
    "974": "262",  # Réunion
    "975": "509",  # Saint-Pierre-et-Miquelon
    "976": "262",  # Mayotte
    "977": "590",  # Saint-Barthélémy
    "978": "590",  # Saint-Martin
    "986": "681",  # Wallis-et-Futuna
    "987": "689",  # Tahiti
    "988": "687",  # Nouvelle-Calédonie
}

METROPOLE_PHONE_PREFIX = "33"
