from pcapi.core.bookings import conf
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from .serialization import settings as serializers


@blueprint.native_v1.route("/settings", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=serializers.SettingsResponse)
def get_settings() -> serializers.SettingsResponse:
    current_deposit_version = conf.get_current_deposit_version()
    booking_configuration = conf.LIMIT_CONFIGURATIONS[current_deposit_version]

    return serializers.SettingsResponse(deposit_amount=booking_configuration.TOTAL_CAP)
