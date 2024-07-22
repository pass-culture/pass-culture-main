import decimal

import pcapi.core.offers.models as offers_models

from . import models


# lock to forbid the backoffice any write access to the pricing while the script is running
REDIS_GENERATE_CASHFLOW_LOCK = "pc:finance:generate_cashflow_lock"
REDIS_GENERATE_CASHFLOW_LOCK_TIMEOUT = 60 * 60 * 24  # 24h

REDIS_INVOICES_LEFT_TO_GENERATE = "pcapi:finance:generate_invoices:counter"
REDIS_GENERATE_INVOICES_COUNTER_TIMEOUT = 60 * 60 * 12  # 12h
REDIS_GENERATE_INVOICES_LENGTH = "pcapi:finance:generate_invoices:length"
REDIS_GENERATE_INVOICES_LENGTH_TIMEOUT = 60 * 60 * 12  # 12h

# Age in days before generating a cashflow and a debit note when total pricings is positive
DEBIT_NOTE_AGE_THRESHOLD_FOR_CASHFLOW = 90

GRANT_18_VALIDITY_IN_YEARS = 2

GRANTED_DEPOSIT_AMOUNT_15 = decimal.Decimal(20)
GRANTED_DEPOSIT_AMOUNT_16 = decimal.Decimal(30)
GRANTED_DEPOSIT_AMOUNT_17 = decimal.Decimal(30)
GRANTED_DEPOSIT_AMOUNT_18_v1 = decimal.Decimal(500)
GRANTED_DEPOSIT_AMOUNT_18_v2 = decimal.Decimal(300)

GRANT_18_DIGITAL_CAP_V1 = decimal.Decimal(200)
GRANT_18_DIGITAL_CAP_V2 = decimal.Decimal(100)
GRANT_18_PHYSICAL_CAP_V1 = decimal.Decimal(200)
GRANT_18_PHYSICAL_CAP_V2: decimal.Decimal | None = None

WALLIS_AND_FUTUNA_DEPARTMENT_CODE = "986"
MAYOTTE_DEPARTMENT_CODE = "976"
SAINT_PIERRE_ET_MIQUELON_DEPARTMENT_CODE = "975"

SPECIFIC_DIGITAL_CAPS_BY_DEPARTMENT_CODE = {
    WALLIS_AND_FUTUNA_DEPARTMENT_CODE: None,
    MAYOTTE_DEPARTMENT_CODE: decimal.Decimal(150),
    SAINT_PIERRE_ET_MIQUELON_DEPARTMENT_CODE: decimal.Decimal(200),
}


GRANTED_DEPOSIT_AMOUNTS_FOR_UNDERAGE_BY_AGE = {
    15: GRANTED_DEPOSIT_AMOUNT_15,
    16: GRANTED_DEPOSIT_AMOUNT_16,
    17: GRANTED_DEPOSIT_AMOUNT_17,
}

GRANTED_DEPOSIT_AMOUNTS_FOR_18_BY_VERSION = {
    1: GRANTED_DEPOSIT_AMOUNT_18_v1,  # not used anymore, still present in database
    2: GRANTED_DEPOSIT_AMOUNT_18_v2,
}


RECREDIT_TYPE_AGE_MAPPING = {
    15: models.RecreditType.RECREDIT_15,
    16: models.RecreditType.RECREDIT_16,
    17: models.RecreditType.RECREDIT_17,
}

RECREDIT_TYPE_AMOUNT_MAPPING = {
    models.RecreditType.RECREDIT_15: GRANTED_DEPOSIT_AMOUNT_15,
    models.RecreditType.RECREDIT_16: GRANTED_DEPOSIT_AMOUNT_16,
    models.RecreditType.RECREDIT_17: GRANTED_DEPOSIT_AMOUNT_17,
}


def get_amount_to_display(user_age: int) -> decimal.Decimal | None:
    if user_age == 18:
        amount_to_display: decimal.Decimal | None = GRANTED_DEPOSIT_AMOUNT_18_v2
    else:
        amount_to_display = GRANTED_DEPOSIT_AMOUNTS_FOR_UNDERAGE_BY_AGE.get(user_age)

    return amount_to_display


def digital_cap_applies_to_offer(offer: offers_models.Offer) -> bool:
    return offer.isDigital and offer.subcategory.is_digital_deposit


def physical_cap_applies_to_offer(offer: offers_models.Offer) -> bool:
    return not offer.isDigital and offer.subcategory.is_physical_deposit


class SpecificCaps:
    DIGITAL_CAP: decimal.Decimal | None = None
    PHYSICAL_CAP: decimal.Decimal | None = None

    def __init__(self, digital_cap: decimal.Decimal | None, physical_cap: decimal.Decimal | None) -> None:
        self.DIGITAL_CAP = digital_cap
        self.PHYSICAL_CAP = physical_cap

    def digital_cap_applies(self, offer: offers_models.Offer) -> bool:
        return digital_cap_applies_to_offer(offer) and bool(self.DIGITAL_CAP)

    def physical_cap_applies(self, offer: offers_models.Offer) -> bool:
        return physical_cap_applies_to_offer(offer) and bool(self.PHYSICAL_CAP)
