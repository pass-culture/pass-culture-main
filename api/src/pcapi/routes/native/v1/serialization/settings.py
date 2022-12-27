import pcapi.core.finance.conf as finance_conf
from pcapi.routes.native.utils import convert_to_cent
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel


class DepositAmountsByAge(BaseModel):
    age_15 = convert_to_cent(finance_conf.GRANTED_DEPOSIT_AMOUNT_15)
    age_16 = convert_to_cent(finance_conf.GRANTED_DEPOSIT_AMOUNT_16)
    age_17 = convert_to_cent(finance_conf.GRANTED_DEPOSIT_AMOUNT_17)
    age_18 = convert_to_cent(finance_conf.GRANTED_DEPOSIT_AMOUNT_18_v2)


class SettingsResponse(BaseModel):
    account_creation_minimum_age: int
    app_enable_autocomplete: bool
    deposit_amounts_by_age = DepositAmountsByAge()
    display_dms_redirection: bool
    enable_front_image_resizing: bool
    enable_native_cultural_survey: bool
    enable_native_id_check_verbose_debugging: bool
    enable_phone_validation: bool
    id_check_address_autocompletion: bool
    is_recaptcha_enabled: bool
    object_storage_url: str
    pro_disable_events_qrcode: bool
    account_unsuspension_limit: int

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
