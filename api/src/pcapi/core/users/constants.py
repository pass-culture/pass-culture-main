import datetime
import enum

from pcapi import settings


ACCOUNT_CREATION_TOKEN_LIFE_TIME = datetime.timedelta(hours=1)
OAUTH_STATE_TOKEN_LIFE_TIME = datetime.timedelta(hours=1)
RESET_PASSWORD_TOKEN_LIFE_TIME = datetime.timedelta(hours=24)
EMAIL_VALIDATION_TOKEN_LIFE_TIME = datetime.timedelta(minutes=30)
# FIXME (dbaty, 2024-06-26) for now, pro users cannot re-send the token themselves.
# The default (30 minutes) TTL could thus be too low. So we use an augmented TTL.
# Once pro users can re-send tokens, we can use the default TTL (EMAIL_VALIDATION_TOKEN_LIFE_TIME).
EMAIL_VALIDATION_TOKEN_FOR_PRO_LIFE_TIME = datetime.timedelta(days=90)
EMAIL_VALIDATION_TOKEN_UPON_MANUAL_CREATION_LIFE_TIME = datetime.timedelta(days=1)
EMAIL_CHANGE_TOKEN_LIFE_TIME = datetime.timedelta(seconds=settings.EMAIL_CHANGE_TOKEN_LIFE_TIME)
PHONE_VALIDATION_TOKEN_LIFE_TIME = datetime.timedelta(hours=12)
SUSPICIOUS_LOGIN_EMAIL_TOKEN_LIFE_TIME = datetime.timedelta(weeks=1)

MAX_SUSPICIOUS_LOGIN_EMAILS = 5

MAX_EMAIL_UPDATE_ATTEMPTS_FOR_PRO = 5
EMAIL_PRO_UPDATE_ATTEMPTS_TTL = 24 * 60 * 60  # 1 day in seconds

ELIGIBILITY_AGE_18 = 18
ELIGIBILITY_UNDERAGE_RANGE = [15, 16, 17]

ACCOUNT_CREATION_MINIMUM_AGE = 15

ACCOUNT_UNSUSPENSION_DELAY = 60  # days

EDUCONNECT_SAML_REQUEST_ID_TTL = 24 * 60 * 60  # 1 day in seconds


class SuspensionReason(enum.Enum):
    def __str__(self) -> str:
        return str(self.value)

    # If you add a new reason, update `suspend_account()` to cancel
    # bookings if applicable.
    BLACKLISTED_DOMAIN_NAME = "nom de domaine blacklisté"
    CLOSED_STRUCTURE_DEFINITIVE = "definitively closed structure"
    CLOSED_STRUCTURE_TEMP = "temporarly closed structure"
    DELETED = "deleted"
    DEVICE_AT_RISK = "device at risk"
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
    SUSPICIOUS_LOGIN_REPORTED_BY_USER = "suspicious login reported by user"
    SUSPENSION_FOR_INVESTIGATION_TEMP = "temporary suspension for investigation"
    UPON_USER_REQUEST = "upon user request"


PRO_SUSPENSION_REASON_CHOICES = {
    SuspensionReason.CLOSED_STRUCTURE_DEFINITIVE: "Structure définitivement fermée",
    SuspensionReason.CLOSED_STRUCTURE_TEMP: "Structure fermée provisoirement",
    SuspensionReason.END_OF_CONTRACT: "Fin de contrat",
    SuspensionReason.FRAUD_CREATION_PRO: "Fraude PRO création",
    SuspensionReason.FRAUD_USURPATION_PRO: "Fraude PRO usurpation",
    SuspensionReason.SUSPENSION_FOR_INVESTIGATION_TEMP: "Suspension provisoire pour investigations",
}

PUBLIC_SUSPENSION_REASON_CHOICES = {
    SuspensionReason.BLACKLISTED_DOMAIN_NAME: "Nom de domaine blacklisté",
    SuspensionReason.DELETED: "Supprimé",
    SuspensionReason.DEVICE_AT_RISK: "Device à risque",
    SuspensionReason.END_OF_ELIGIBILITY: "Fin d'éligibilité",
    SuspensionReason.FRAUD_BOOKING_CANCEL: "Fraude annulation réservation",
    SuspensionReason.FRAUD_DUPLICATE: "Fraude doublon",
    SuspensionReason.FRAUD_FAKE_DOCUMENT: "Fraude faux document",
    SuspensionReason.FRAUD_HACK: "Fraude hacking",
    SuspensionReason.FRAUD_RESELL_PRODUCT: "Fraude revente produit",
    SuspensionReason.FRAUD_RESELL_PASS: "Fraude revente pass",
    SuspensionReason.FRAUD_SUSPICION: "Fraude suspicion",
    SuspensionReason.FRAUD_USURPATION: "Fraude usurpation",
    SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER: "Connexion suspicieuse signalée par l'utilisateur",
    SuspensionReason.UPON_USER_REQUEST: "Demande de l'utilisateur",
}

SUSPENSION_REASON_CHOICES = PRO_SUSPENSION_REASON_CHOICES | PUBLIC_SUSPENSION_REASON_CHOICES

assert set(SUSPENSION_REASON_CHOICES) == set(SuspensionReason)
