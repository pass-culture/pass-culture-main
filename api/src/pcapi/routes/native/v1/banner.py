from flask import request

import pcapi.core.banner.api as banner_api
from pcapi.core.subscription import api as subscription_api
from pcapi.core.users import models as users_models
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.routes.native.v1 import blueprint
from pcapi.routes.native.v1.serialization import banner as serializers
from pcapi.serialization.decorator import spectree_serialize


@blueprint.native_v1.route("/banner", methods=["GET"])
@spectree_serialize(on_success_status=200, api=blueprint.api, response_model=serializers.BannerResponse)
@authenticated_and_active_user_required
def get_banner(user: users_models.User) -> serializers.BannerResponse | None:
    is_geolocated = request.args.get("isGeolocated", "false") == "true"

    subscription_state = subscription_api.get_user_subscription_state(user)

    banner = None
    if subscription_state.next_step in banner_api.ACTIVATION_BANNER_NEXT_STEPS:
        banner = banner_api.get_activation_banner(user.age)
    elif not is_geolocated:
        banner = banner_api.GEOLOCATION_BANNER

    return serializers.BannerResponse(banner=banner)
