import logging

from flask import jsonify
from flask import request
from flask_login import current_user
from flask_login import login_required
from sqlalchemy.orm import exc as orm_exc

from pcapi.core.bookings.repository import get_active_bookings_quantity_for_offerer
from pcapi.core.bookings.repository import get_validated_bookings_quantity_for_offerer
from pcapi.core.offerers import api
from pcapi.core.offerers.exceptions import ApiKeyCountMaxReached
from pcapi.core.offerers.exceptions import ApiKeyDeletionDenied
from pcapi.core.offerers.exceptions import ApiKeyPrefixGenerationError
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.repository import get_all_offerers_for_user
from pcapi.core.offers.repository import get_active_offers_count_for_venue
from pcapi.core.offers.repository import get_sold_out_offers_count_for_venue
from pcapi.flask_app import private_api
from pcapi.infrastructure.container import list_offerers_for_pro_user
from pcapi.models import ApiErrors
from pcapi.repository import transaction
from pcapi.routes.serialization import as_dict
from pcapi.routes.serialization.offerers_serialize import CreateOffererQueryModel
from pcapi.routes.serialization.offerers_serialize import GenerateOffererApiKeyResponse
from pcapi.routes.serialization.offerers_serialize import GetOffererNameResponseModel
from pcapi.routes.serialization.offerers_serialize import GetOffererResponseModel
from pcapi.routes.serialization.offerers_serialize import GetOfferersNamesQueryModel
from pcapi.routes.serialization.offerers_serialize import GetOfferersNamesResponseModel
from pcapi.routes.serialization.venues_serialize import VenueStatsResponseModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.use_cases.list_offerers_for_pro_user import OfferersRequestParameters
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.includes import OFFERER_INCLUDES
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.utils.rest import load_or_404


logger = logging.getLogger(__name__)


def get_dict_offerer(offerer: Offerer) -> dict:
    offerer.append_user_has_access_attribute(user_id=current_user.id, is_admin=current_user.isAdmin)

    return as_dict(offerer, includes=OFFERER_INCLUDES)


def get_dict_offerers(offerers: list[Offerer]) -> list:
    return [as_dict(offerer, includes=OFFERER_INCLUDES) for offerer in offerers]


# @debt api-migration
@private_api.route("/offerers", methods=["GET"])
@login_required
def get_offerers():
    keywords = request.args.get("keywords")
    only_validated_offerers = request.args.get("validated")

    is_filtered_by_offerer_status = only_validated_offerers is not None

    if is_filtered_by_offerer_status:
        if only_validated_offerers.lower() not in ("true", "false"):
            errors = ApiErrors()
            errors.add_error("validated", "Le paramètre 'validated' doit être 'true' ou 'false'")
            raise errors

        only_validated_offerers = only_validated_offerers.lower() == "true"

    offerers_request_parameters = OfferersRequestParameters(
        user_id=current_user.id,
        user_is_admin=current_user.isAdmin,
        is_filtered_by_offerer_status=is_filtered_by_offerer_status,
        only_validated_offerers=only_validated_offerers,
        keywords=keywords,
        pagination_limit=request.args.get("paginate", "10"),
        page=request.args.get("page", "0"),
    )

    paginated_offerers = list_offerers_for_pro_user.execute(offerers_request_parameters=offerers_request_parameters)

    response = jsonify(get_dict_offerers(paginated_offerers.offerers))
    response.headers["Total-Data-Count"] = paginated_offerers.total
    response.headers["Access-Control-Expose-Headers"] = "Total-Data-Count"

    return response, 200


@private_api.route("/offerers/names", methods=["GET"])
@login_required
@spectree_serialize(response_model=GetOfferersNamesResponseModel)
def list_offerers_names(query: GetOfferersNamesQueryModel) -> GetOfferersNamesResponseModel:
    offerers = get_all_offerers_for_user(
        user=current_user,
        filters={
            "validated": query.validated,
            "validated_for_user": query.validated_for_user,
        },
    )

    return GetOfferersNamesResponseModel(
        offerersNames=[GetOffererNameResponseModel.from_orm(offerer) for offerer in offerers]
    )


@private_api.route("/offerers/<offerer_id>", methods=["GET"])
@login_required
@spectree_serialize(response_model=GetOffererResponseModel)
def get_offerer(offerer_id: str) -> GetOffererResponseModel:
    check_user_has_access_to_offerer(current_user, dehumanize(offerer_id))
    offerer = load_or_404(Offerer, offerer_id)

    return GetOffererResponseModel.from_orm(offerer)


@private_api.route("/offerers/<humanized_offerer_id>/stats", methods=["GET"])
@login_required
@spectree_serialize(on_success_status=200, response_model=GetOffererResponseModel)
def get_venues_by_offerer_with_stats(humanized_offerer_id: str) -> GetOffererResponseModel:
    check_user_has_access_to_offerer(current_user, dehumanize(humanized_offerer_id))
    offerer = load_or_404(Offerer, humanized_offerer_id)

    venue_stats_by_ids = {}
    active_bookings_quantity_by_venue = get_active_bookings_quantity_for_offerer(offerer.id)
    validated_bookings_quantity_by_venue = get_validated_bookings_quantity_for_offerer(offerer.id)

    for managedVenue in offerer.managedVenues:
        active_offers_count = get_active_offers_count_for_venue(managedVenue.id)
        sold_out_offers_count = get_sold_out_offers_count_for_venue(managedVenue.id)

        venue_stats_by_ids[managedVenue.id] = VenueStatsResponseModel(
            activeBookingsQuantity=active_bookings_quantity_by_venue.get(managedVenue.id, 0),
            validatedBookingsQuantity=validated_bookings_quantity_by_venue.get(managedVenue.id, 0),
            activeOffersCount=active_offers_count,
            soldOutOffersCount=sold_out_offers_count,
        )

    return GetOffererResponseModel.from_orm(offerer, venue_stats_by_ids)


@private_api.route("/offerers/<offerer_id>/api_keys", methods=["POST"])
@login_required
@spectree_serialize(response_model=GenerateOffererApiKeyResponse)
def generate_api_key_route(offerer_id: str) -> GenerateOffererApiKeyResponse:
    check_user_has_access_to_offerer(current_user, dehumanize(offerer_id))
    offerer = load_or_404(Offerer, offerer_id)
    try:
        clear_key = api.generate_and_save_api_key(offerer.id)
    except ApiKeyCountMaxReached:
        raise ApiErrors({"api_key_count_max": "Le nombre de clés maximal a été atteint"})
    except ApiKeyPrefixGenerationError:
        raise ApiErrors({"api_key": "Could not generate api key"})

    return GenerateOffererApiKeyResponse(apiKey=clear_key)


@private_api.route("/offerers/api_keys/<api_key_prefix>", methods=["DELETE"])
@login_required
@spectree_serialize(on_success_status=204)
def delete_api_key(api_key_prefix: str):
    with transaction():
        try:
            api.delete_api_key_by_user(current_user, api_key_prefix)
        except orm_exc.NoResultFound:
            raise ApiErrors({"prefix": "not found"}, 404)
        except ApiKeyDeletionDenied:
            raise ApiErrors({"api_key": "deletion forbidden"}, 403)


@private_api.route("/offerers", methods=["POST"])
@login_required
@spectree_serialize(on_success_status=201, response_model=GetOffererResponseModel)
def create_offerer(body: CreateOffererQueryModel) -> GetOffererResponseModel:
    user_offerer = api.create_offerer(current_user, body)

    return GetOffererResponseModel.from_orm(user_offerer.offerer)
