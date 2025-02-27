import decimal

import pcapi.core.offers.models as offers_models
from pcapi.core.users import models as users_models
from pcapi.models.feature import FeatureToggle

from . import models


# Lock to prevent parallel push of invoices
REDIS_PUSH_INVOICE_LOCK = "pc:finance:push_invoice_lock"
REDIS_PUSH_INVOICE_LOCK_TIMEOUT = 86400  # 60 * 60 * 24 = 24h

# lock to prevent parallel push of bank accounts
REDIS_PUSH_BANK_ACCOUNT_LOCK = "pc:finance:push_bank_account_lock"
REDIS_PUSH_BANK_ACCOUNT_LOCK_TIMEOUT = 86400  # = 60 * 60 * 24 = 24h

# lock to forbid the backoffice any write access to the pricing while the script is running
REDIS_GENERATE_CASHFLOW_LOCK = "pc:finance:generate_cashflow_lock"
REDIS_GENERATE_CASHFLOW_LOCK_TIMEOUT = 60 * 60 * 24  # 24h

# Age in days before generating a cashflow and a debit note when total pricings is positive
DEBIT_NOTE_AGE_THRESHOLD_FOR_CASHFLOW = 90

GRANT_18_VALIDITY_IN_YEARS = 2

GRANTED_DEPOSIT_AMOUNT_15 = decimal.Decimal(20)
GRANTED_DEPOSIT_AMOUNT_16 = decimal.Decimal(30)
GRANTED_DEPOSIT_AMOUNT_17 = decimal.Decimal(30)
GRANTED_DEPOSIT_AMOUNT_17_v3 = decimal.Decimal(50)
GRANTED_DEPOSIT_AMOUNT_18_v1 = decimal.Decimal(500)
GRANTED_DEPOSIT_AMOUNT_18_v2 = decimal.Decimal(300)
GRANTED_DEPOSIT_AMOUNT_18_v3 = decimal.Decimal(150)

GRANT_18_DIGITAL_CAP_V1 = decimal.Decimal(200)
GRANT_18_DIGITAL_CAP_V2 = decimal.Decimal(100)
GRANT_18_PHYSICAL_CAP_V1 = decimal.Decimal(200)
GRANT_18_PHYSICAL_CAP_V2: decimal.Decimal | None = None
GRANT_17_18_DIGITAL_CAP = decimal.Decimal(100)
GRANT_17_18_PHYSICAL_CAP: decimal.Decimal | None = None

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


RECREDIT_TYPE_AGE_MAPPING = {
    15: models.RecreditType.RECREDIT_15,
    16: models.RecreditType.RECREDIT_16,
    17: models.RecreditType.RECREDIT_17,
}


def get_recredit_mapping() -> dict[int, models.RecreditType]:
    if FeatureToggle.WIP_ENABLE_CREDIT_V3.is_active():
        RECREDIT_TYPE_AGE_MAPPING[18] = models.RecreditType.RECREDIT_18
    return RECREDIT_TYPE_AGE_MAPPING


RECREDIT_TYPE_AMOUNT_MAPPING = {
    models.RecreditType.RECREDIT_15: GRANTED_DEPOSIT_AMOUNT_15,
    models.RecreditType.RECREDIT_16: GRANTED_DEPOSIT_AMOUNT_16,
    models.RecreditType.RECREDIT_17: GRANTED_DEPOSIT_AMOUNT_17,
}


def get_credit_amount_per_age(age: int) -> decimal.Decimal | None:
    if FeatureToggle.WIP_ENABLE_CREDIT_V3.is_active():
        return _get_deposit_17_18_credit_amount_per_age(age)

    return _get_pre_decree_credit_amount_per_age(age)


def get_credit_amount_per_age_and_eligibility(
    age: int, eligibility: users_models.EligibilityType | None
) -> decimal.Decimal | None:
    if eligibility is None:
        return None

    if eligibility == users_models.EligibilityType.AGE17_18:
        return _get_deposit_17_18_credit_amount_per_age(age)

    return _get_pre_decree_credit_amount_per_age(age)


def _get_deposit_17_18_credit_amount_per_age(age: int) -> decimal.Decimal | None:
    match age:
        case 17:
            return GRANTED_DEPOSIT_AMOUNT_17_v3
        case 18:
            return GRANTED_DEPOSIT_AMOUNT_18_v3
        case _:
            return None


def _get_pre_decree_credit_amount_per_age(age: int) -> decimal.Decimal | None:
    match age:
        case 15:
            return GRANTED_DEPOSIT_AMOUNT_15
        case 16:
            return GRANTED_DEPOSIT_AMOUNT_16
        case 17:
            return GRANTED_DEPOSIT_AMOUNT_17
        case 18:
            return GRANTED_DEPOSIT_AMOUNT_18_v2
        case _:
            return None


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
