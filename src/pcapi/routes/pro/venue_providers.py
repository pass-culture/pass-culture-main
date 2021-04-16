from typing import Any
from typing import Tuple

from flask import jsonify
from flask import request
from flask_login import login_required

from pcapi.core.providers import api
from pcapi.core.providers.models import VenueProvider
from pcapi.flask_app import private_api
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.serialization import as_dict
from pcapi.routes.serialization.venue_provider_serialize import PostVenueProviderBody
from pcapi.routes.serialization.venue_provider_serialize import VenueProviderResponse
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.includes import VENUE_PROVIDER_INCLUDES


# @debt api-migration
@private_api.route("/venueProviders", methods=["GET"])
@login_required
def list_venue_providers() -> Tuple[Any, int]:
    venue_id = request.args.get("venueId")
    if venue_id is None:
        e = ApiErrors()
        e.add_error("venueId", "Vous devez obligatoirement fournir le paramètre venueId")
        return jsonify(e.errors), 400

    vp_query = VenueProvider.query.filter_by(venueId=dehumanize(venue_id))
    return jsonify([as_dict(venue_provider, includes=VENUE_PROVIDER_INCLUDES) for venue_provider in vp_query.all()])


@private_api.route("/venueProviders", methods=["POST"])
@login_required
@spectree_serialize(on_success_status=201, response_model=VenueProviderResponse)
def create_venue_provider(body: PostVenueProviderBody) -> VenueProviderResponse:
    body.venueIdAtOfferProvider = None

    new_venue_provider = api.create_venue_provider(body)

    return VenueProviderResponse.from_orm(new_venue_provider)
