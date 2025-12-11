import logging

from pcapi.routes.native import blueprint
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.routes.native.v1.serialization import geography as serialization
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils import countries as countries_utils
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)


@blueprint.native_route("/countries", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=serialization.InseeCountries)
@authenticated_and_active_user_required
@atomic()
def get_countries() -> serialization.InseeCountries:
    countries = [
        serialization.InseeCountry(cog=int(cog), libcog=libcog) for (cog, libcog) in countries_utils.INSEE_COUNTRIES
    ]
    return serialization.InseeCountries(countries=countries)
