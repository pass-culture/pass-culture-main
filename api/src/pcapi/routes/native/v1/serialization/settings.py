from pydantic.class_validators import validator

from pcapi.routes.native.utils import convert_to_cent
from pcapi.serialization.utils import to_camel

from . import BaseModel


class SettingsResponse(BaseModel):
    deposit_amount: int
    is_recaptcha_enabled: bool
    auto_activate_digital_bookings: bool
    allow_id_check_registration: bool
    enable_native_id_check_version: bool
    enable_native_id_check_verbose_debugging: bool
    enable_id_check_retention: bool
    enable_phone_validation: bool
    object_storage_url: str
    whole_france_opening: bool
    display_dms_redirection: bool
    use_app_search: bool
    id_check_address_autocompletion: bool
    is_webapp_v2_enabled: bool
    enable_native_eac_individual: bool
    account_creation_minimum_age: int

    _convert_deposit_amount = validator("deposit_amount", pre=True, allow_reuse=True)(convert_to_cent)

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
