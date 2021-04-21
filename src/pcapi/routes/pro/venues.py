from flask import jsonify
from flask import request
from flask_login import current_user
from flask_login import login_required

from pcapi.core.bookings.repository import get_active_bookings_quantity_for_venue
from pcapi.core.bookings.repository import get_validated_bookings_quantity_for_venue
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.validation import validate_coordinates
from pcapi.core.offers.repository import get_active_offers_count_for_venue
from pcapi.core.offers.repository import get_sold_out_offers_count_for_venue
from pcapi.domain.identifier.identifier import Identifier
from pcapi.flask_app import private_api
from pcapi.infrastructure.container import get_all_venues_by_pro_user
from pcapi.repository import repository
from pcapi.routes.serialization import as_dict
from pcapi.routes.serialization.venues_serialize import EditVenueBodyModel
from pcapi.routes.serialization.venues_serialize import GetVenueResponseModel
from pcapi.routes.serialization.venues_serialize import VenueStatsResponseModel
from pcapi.routes.serialization.venues_serialize import serialize_venues_with_offerer_name
from pcapi.serialization.decorator import spectree_serialize
from pcapi.use_cases.create_venue import create_venue
from pcapi.utils.includes import VENUE_INCLUDES
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.utils.rest import expect_json_data
from pcapi.utils.rest import load_or_404


@private_api.route("/venues/<venue_id>", methods=["GET"])
@login_required
@spectree_serialize(response_model=GetVenueResponseModel)
def get_venue(venue_id: str) -> GetVenueResponseModel:
    venue = load_or_404(Venue, venue_id)
    check_user_has_access_to_offerer(current_user, venue.managingOffererId)

    return GetVenueResponseModel.from_orm(venue)


# @debt api-migration
@private_api.route("/venues", methods=["GET"])
@login_required
def get_venues():
    map_string_args = {
        "true": True,
        "false": False,
    }
    validated = request.args.get("validated", None)
    if map_string_args.get(validated, None) is not None:
        validated = map_string_args[validated]

    validated_for_user = request.args.get("validatedForUser", None)
    if map_string_args.get(validated_for_user, None) is not None:
        validated_for_user = map_string_args[validated_for_user]

    active_offerers_only = request.args.get("activeOfferersOnly", None)
    if map_string_args.get(active_offerers_only, None) is not None:
        active_offerers_only = map_string_args[active_offerers_only]

    offerer_identifier = Identifier.from_scrambled_id(request.args.get("offererId"))

    venues = get_all_venues_by_pro_user.execute(
        pro_identifier=current_user.id,
        user_is_admin=current_user.isAdmin,
        active_offerers_only=active_offerers_only,
        offerer_id=offerer_identifier,
        validated_offerer=validated,
        validated_offerer_for_user=validated_for_user,
    )
    return jsonify(serialize_venues_with_offerer_name(venues)), 200


# @debt api-migration
@private_api.route("/venues", methods=["POST"])
@login_required
@expect_json_data
def post_create_venue():
    validate_coordinates(request.json.get("latitude", None), request.json.get("longitude", None))

    venue = create_venue(venue_properties=request.json, save=repository.save)

    return jsonify(as_dict(venue, includes=VENUE_INCLUDES)), 201


@private_api.route("/venues/<venue_id>", methods=["PATCH"])
@login_required
@spectree_serialize(response_model=GetVenueResponseModel)
def edit_venue(venue_id: str, body: EditVenueBodyModel) -> GetVenueResponseModel:
    venue = load_or_404(Venue, venue_id)

    check_user_has_access_to_offerer(current_user, venue.managingOffererId)
    venue = offerers_api.update_venue(venue, **body.dict(exclude_unset=True))

    return GetVenueResponseModel.from_orm(venue)


@private_api.route("/venues/<humanized_venue_id>/stats", methods=["GET"])
@login_required
@spectree_serialize(on_success_status=200, response_model=VenueStatsResponseModel)
def get_venue_stats(humanized_venue_id: str) -> VenueStatsResponseModel:
    venue = load_or_404(Venue, humanized_venue_id)
    check_user_has_access_to_offerer(current_user, venue.managingOffererId)

    active_bookings_quantity = get_active_bookings_quantity_for_venue(venue.id)
    validated_bookings_count = get_validated_bookings_quantity_for_venue(venue.id)
    active_offers_count = get_active_offers_count_for_venue(venue.id)
    sold_out_offers_count = get_sold_out_offers_count_for_venue(venue.id)

    return VenueStatsResponseModel(
        activeBookingsQuantity=active_bookings_quantity,
        validatedBookingsQuantity=validated_bookings_count,
        activeOffersCount=active_offers_count,
        soldOutOffersCount=sold_out_offers_count,
    )
