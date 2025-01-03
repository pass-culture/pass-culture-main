import pcapi.core.finance.conf as finance_conf
from pcapi.core.finance.utils import XPR_TO_EUR_RATE
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import ConfiguredBaseModel
from pcapi.routes.shared.price import convert_to_cent


class DepositAmountsByAge(BaseModel):
    age_15 = convert_to_cent(finance_conf.GRANTED_DEPOSIT_AMOUNT_15)
    age_16 = convert_to_cent(finance_conf.GRANTED_DEPOSIT_AMOUNT_16)
    age_17 = convert_to_cent(finance_conf.GRANTED_DEPOSIT_AMOUNT_17)
    age_18 = convert_to_cent(finance_conf.GRANTED_DEPOSIT_AMOUNT_18_v2)


class Rates(BaseModel):
    pacificFrancToEuro = XPR_TO_EUR_RATE


class SettingsResponse(ConfiguredBaseModel):
    account_creation_minimum_age: int
    account_unsuspension_limit: int
    app_enable_autocomplete: bool
    deposit_amounts_by_age = DepositAmountsByAge()
    display_dms_redirection: bool
    enable_front_image_resizing: bool
    enable_native_cultural_survey: bool
    enable_phone_validation: bool
    id_check_address_autocompletion: bool
    ineligible_postal_codes: list[str]
    is_recaptcha_enabled: bool
    object_storage_url: str
    rates = Rates()
    wip_enable_credit_v3: bool
