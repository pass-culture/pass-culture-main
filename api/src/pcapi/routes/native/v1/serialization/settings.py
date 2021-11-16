from pydantic.class_validators import validator

from pcapi.routes.native.utils import convert_to_cent
from pcapi.serialization.utils import to_camel

from . import BaseModel


class SettingsResponse(BaseModel):
    account_creation_minimum_age: int
    auto_activate_digital_bookings: bool
    allow_id_check_registration: bool
    deposit_amount: int
    display_dms_redirection: bool
    enable_native_id_check_version: bool
    enable_native_id_check_verbose_debugging: bool
    enable_id_check_retention: bool
    enable_native_eac_individual: bool
    enable_phone_validation: bool
    enable_underage_generalisation: bool
    id_check_address_autocompletion: bool
    is_recaptcha_enabled: bool
    is_webapp_v2_enabled: bool
    object_storage_url: str
    use_app_search: bool
    whole_france_opening: bool

    _convert_deposit_amount = validator("deposit_amount", pre=True, allow_reuse=True)(convert_to_cent)

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
