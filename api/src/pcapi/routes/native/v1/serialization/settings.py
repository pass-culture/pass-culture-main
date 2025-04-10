import decimal

import pcapi.core.finance.conf as finance_conf
from pcapi.core.finance.utils import XPR_TO_EUR_RATE
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import ConfiguredBaseModel
from pcapi.routes.shared.price import convert_to_cent


class DepositAmountsByAge(BaseModel):
    age_15: int
    age_16: int
    age_17: int
    age_18: int


def _convert_amount(amount: decimal.Decimal | None) -> int:
    if amount is None:
        return 0
    converted_amount = convert_to_cent(amount)
    return converted_amount if converted_amount is not None else 0


def get_deposit_amounts_by_age() -> DepositAmountsByAge:
    return DepositAmountsByAge(
        age_15=0,
        age_16=0,
        age_17=_convert_amount(finance_conf.GRANTED_DEPOSIT_AMOUNT_17_v3),
        age_18=_convert_amount(finance_conf.GRANTED_DEPOSIT_AMOUNT_18_v3),
    )


class Rates(BaseModel):
    pacificFrancToEuro = XPR_TO_EUR_RATE


class SettingsResponse(ConfiguredBaseModel):
    account_creation_minimum_age: int
    account_unsuspension_limit: int
    app_enable_autocomplete: bool
    deposit_amounts_by_age: DepositAmountsByAge
    display_dms_redirection: bool
    enable_front_image_resizing: bool
    enable_native_cultural_survey: bool
    enable_phone_validation: bool
    id_check_address_autocompletion: bool
    ineligible_postal_codes: list[str]
    is_recaptcha_enabled: bool
    object_storage_url: str
    rates = Rates()
    # TODO: remove when the app does not use the feature flag anymore PC-35597
    wip_enable_credit_v3: bool
