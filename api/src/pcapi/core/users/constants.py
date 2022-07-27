import datetime
from enum import Enum


RESET_PASSWORD_TOKEN_LIFE_TIME = datetime.timedelta(hours=24)
RESET_PASSWORD_TOKEN_LIFE_TIME_EXTENDED = datetime.timedelta(days=30)
EMAIL_VALIDATION_TOKEN_LIFE_TIME = datetime.timedelta(minutes=30)
EMAIL_CHANGE_TOKEN_LIFE_TIME = datetime.timedelta(hours=24)
PHONE_VALIDATION_TOKEN_LIFE_TIME = datetime.timedelta(hours=12)

ELIGIBILITY_AGE_18 = 18
ELIGIBILITY_UNDERAGE_RANGE = [15, 16, 17]

ACCOUNT_CREATION_MINIMUM_AGE = 15

ACCOUNT_UNSUSPENSION_DELAY = 60  # days

EDUCONNECT_SAML_REQUEST_ID_TTL = 24 * 60 * 60  # 1 day in seconds


class SuspensionReason(Enum):
    def __str__(self) -> str:
        return str(self.value)

    # If you add a new reason, update `suspend_account()` to cancel
    # bookings if applicable.
    CLOSED_STRUCTURE_DEFINITIVE = "definitively closed structure"
    CLOSED_STRUCTURE_TEMP = "temporarly closed structure"
    END_OF_CONTRACT = "end of contract"
    END_OF_ELIGIBILITY = "end of eligibility"
    FRAUD_BOOKING_CANCEL = "booking cancel fraud"
    FRAUD_CREATION_PRO = "creation PRO fraud"
    FRAUD_DUPLICATE = "duplicate fraud"
    FRAUD_FAKE_DOCUMENT = "fake document fraud"
    FRAUD_HACK = "hacking fraud"
    FRAUD_RESELL_PASS = "pass resell fraud"
    FRAUD_RESELL_PRODUCT = "product resell fraud"
    FRAUD_SUSPICION = "fraud suspicion"
    FRAUD_USURPATION = "usurpating fraud"
    FRAUD_USURPATION_PRO = "usurpating PRO fraud"
    UPON_USER_REQUEST = "upon user request"
    DELETED = "deleted"


SUSPENSION_REASON_CHOICES = (
    (SuspensionReason.FRAUD_FAKE_DOCUMENT, "Fraude faux document"),
    (SuspensionReason.FRAUD_RESELL_PRODUCT, "Fraude revente produit"),
    (SuspensionReason.FRAUD_RESELL_PASS, "Fraude revente pass"),
    (SuspensionReason.FRAUD_USURPATION, "Fraude usurpation"),
    (SuspensionReason.FRAUD_SUSPICION, "Fraude suspicion"),
    (SuspensionReason.FRAUD_DUPLICATE, "Fraude doublon"),
    (SuspensionReason.FRAUD_HACK, "Fraude hacking"),
    (SuspensionReason.FRAUD_BOOKING_CANCEL, "Fraude annulation réservation"),
    (SuspensionReason.END_OF_CONTRACT, "Fin de contrat"),
    (SuspensionReason.END_OF_ELIGIBILITY, "Fin d'éligibilité"),
    (SuspensionReason.UPON_USER_REQUEST, "Demande de l'utilisateur"),
    (SuspensionReason.FRAUD_USURPATION_PRO, "Fraude PRO usurpation"),
    (SuspensionReason.FRAUD_CREATION_PRO, "Fraude PRO création"),
    (SuspensionReason.CLOSED_STRUCTURE_DEFINITIVE, "Structure définitivement fermée"),
    (SuspensionReason.CLOSED_STRUCTURE_TEMP, "Structure fermée provisoirement"),
    (SuspensionReason.DELETED, "Supprimé"),
)

assert set(_t[0] for _t in SUSPENSION_REASON_CHOICES) == set(SuspensionReason)


class SuspensionEventType(Enum):
    SUSPENDED = "SUSPENDED"
    UNSUSPENDED = "UNSUSPENDED"


SUSPENSION_EVENT_TYPE_CHOICES = (
    (SuspensionEventType.SUSPENDED, "Suspendu"),
    (SuspensionEventType.UNSUSPENDED, "Réactivé"),
)

assert set(_t[0] for _t in SUSPENSION_EVENT_TYPE_CHOICES) == set(SuspensionEventType)
