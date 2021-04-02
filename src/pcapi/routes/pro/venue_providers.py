import subprocess

from flask import jsonify
from flask import request
from flask_login import login_required

from pcapi.core.providers.venue_provider import VenueProvider
from pcapi.flask_app import private_api
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries
from pcapi.repository.provider_queries import get_provider_enabled_for_pro_by_id
from pcapi.repository.venue_queries import find_by_id
from pcapi.routes.serialization import as_dict
from pcapi.routes.serialization.venue_provider_serialize import PostVenueProviderBody
from pcapi.routes.serialization.venue_provider_serialize import VenueProviderResponse
from pcapi.serialization.decorator import spectree_serialize
from pcapi.use_cases.connect_venue_to_allocine import connect_venue_to_allocine
from pcapi.use_cases.connect_venue_to_provider import connect_venue_to_provider
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.includes import VENUE_PROVIDER_INCLUDES
from pcapi.utils.rest import expect_json_data
from pcapi.validation.routes.venue_providers import check_existing_provider
from pcapi.validation.routes.venues import check_existing_venue
from pcapi.workers.venue_provider_job import venue_provider_job


# @debt api-migration
@private_api.route("/venueProviders", methods=["GET"])
@login_required
def list_venue_providers():
    venue_id = request.args.get("venueId")
    if venue_id is None:
        e = ApiErrors()
        e.add_error("venueId", "Vous devez obligatoirement fournir le paramètre venueId")
        return jsonify(e.errors), 400

    vp_query = VenueProvider.query.filter_by(venueId=dehumanize(venue_id))
    return jsonify([as_dict(venue_provider, includes=VENUE_PROVIDER_INCLUDES) for venue_provider in vp_query.all()])


# @debt api-migration
@private_api.route("/venueProviders", methods=["POST"])
@login_required
@expect_json_data
@spectree_serialize(on_success_status=201, response_model=VenueProviderResponse)
def create_venue_provider(body: PostVenueProviderBody):
    venue_provider_payload = body

    provider_id = dehumanize(venue_provider_payload.providerId)
    provider = get_provider_enabled_for_pro_by_id(provider_id)
    check_existing_provider(provider)

    venue_id = dehumanize(venue_provider_payload.venueId)
    venue = find_by_id(venue_id)
    check_existing_venue(venue)

    if provider.localClass == "AllocineStocks":
        new_venue_provider = connect_venue_to_allocine(venue, venue_provider_payload)
    else:
        new_venue_provider = connect_venue_to_provider(venue, provider)

    _run_first_synchronization(new_venue_provider)

    return VenueProviderResponse.from_orm(new_venue_provider)


def _run_first_synchronization(new_venue_provider: VenueProvider):
    if not feature_queries.is_active(FeatureToggle.SYNCHRONIZE_VENUE_PROVIDER_IN_WORKER):
        subprocess.Popen(
            [
                "python",
                "src/pcapi/scripts/pc.py",
                "update_providables",
                "--venue-provider-id",
                str(new_venue_provider.id),
            ]
        )
        return

    venue_provider_job.delay(new_venue_provider.id)
