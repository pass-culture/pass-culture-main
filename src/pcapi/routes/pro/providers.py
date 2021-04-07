from flask import jsonify
from flask_login import login_required

from pcapi.core.providers.repository import get_enabled_providers_for_pro
from pcapi.core.providers.repository import get_providers_enabled_for_pro_excluding_specific_provider
from pcapi.flask_app import private_api
from pcapi.local_providers import AllocineStocks
from pcapi.models import Venue
from pcapi.repository.allocine_pivot_queries import has_allocine_pivot_for_venue
from pcapi.routes.serialization import as_dict
from pcapi.utils.rest import load_or_404


# @debt api-migration
@private_api.route("/providers/<venue_id>", methods=["GET"])
@login_required
def get_providers_by_venue(venue_id: str):
    venue = load_or_404(Venue, venue_id)
    has_allocine_pivot = has_allocine_pivot_for_venue(venue)
    if has_allocine_pivot:
        providers = get_enabled_providers_for_pro()
    else:
        allocine_local_class = AllocineStocks.__name__
        providers = get_providers_enabled_for_pro_excluding_specific_provider(allocine_local_class)
    result = []
    for provider in providers:
        provider_dict = as_dict(provider)
        del provider_dict["apiUrl"]
        del provider_dict["authToken"]
        result.append(provider_dict)
    return jsonify(result)
