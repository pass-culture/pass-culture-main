import logging

from flask_login import current_user
from flask_login import login_required
from sqlalchemy.orm import exc as orm_exc

from pcapi.connectors.api_adage import AdageException
from pcapi.connectors.api_adage import CulturalPartnerNotFoundException
from pcapi.core.offerers import api
from pcapi.core.offerers import repository
from pcapi.core.offerers.exceptions import ApiKeyCountMaxReached
from pcapi.core.offerers.exceptions import ApiKeyDeletionDenied
from pcapi.core.offerers.exceptions import ApiKeyPrefixGenerationError
from pcapi.core.offerers.exceptions import MissingOffererIdQueryParameter
import pcapi.core.offerers.models as offerers_models
from pcapi.core.offerers.repository import get_all_offerers_for_user
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import transaction
from pcapi.routes.apis import private_api
from pcapi.routes.serialization.offerers_serialize import CreateOffererQueryModel
from pcapi.routes.serialization.offerers_serialize import GenerateOffererApiKeyResponse
from pcapi.routes.serialization.offerers_serialize import GetEducationalOffererResponseModel
from pcapi.routes.serialization.offerers_serialize import GetEducationalOfferersQueryModel
from pcapi.routes.serialization.offerers_serialize import GetEducationalOfferersResponseModel
from pcapi.routes.serialization.offerers_serialize import GetOffererListQueryModel
from pcapi.routes.serialization.offerers_serialize import GetOffererNameResponseModel
from pcapi.routes.serialization.offerers_serialize import GetOffererResponseModel
from pcapi.routes.serialization.offerers_serialize import GetOfferersListResponseModel
from pcapi.routes.serialization.offerers_serialize import GetOfferersNamesQueryModel
from pcapi.routes.serialization.offerers_serialize import GetOfferersNamesResponseModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.utils.rest import load_or_404

from . import blueprint


logger = logging.getLogger(__name__)


@private_api.route("/offerers", methods=["GET"])
@login_required
@spectree_serialize(
    on_error_statuses=[400], response_model=GetOfferersListResponseModel, api=blueprint.pro_private_schema
)
def get_offerers(query: GetOffererListQueryModel) -> GetOfferersListResponseModel:
    offerers_query = repository.get_all_offerers_for_user(
        current_user,
        keywords=query.keywords,
    )
    offerers_query = offerers_query.order_by(offerers_models.Offerer.name)
    offerers_query = offerers_query.paginate(
        query.page,
        per_page=query.paginate,
        error_out=False,
    )

    offerers = offerers_query.items
    for offerer in offerers:
        offerer.append_user_has_access_attribute(
            user_id=current_user.id,
            is_admin=current_user.has_admin_role,
        )
    return GetOfferersListResponseModel(
        offerers=offerers,
        nbTotalResults=offerers_query.total,
    )


@private_api.route("/offerers/names", methods=["GET"])
@login_required
@spectree_serialize(response_model=GetOfferersNamesResponseModel, api=blueprint.pro_private_schema)
def list_offerers_names(query: GetOfferersNamesQueryModel) -> GetOfferersNamesResponseModel:
    offerers = get_all_offerers_for_user(
        user=current_user,
        validated=query.validated,
        validated_for_user=query.validated_for_user,
    )

    return GetOfferersNamesResponseModel(
        offerersNames=[GetOffererNameResponseModel.from_orm(offerer) for offerer in offerers]
    )


@private_api.route("/offerers/educational", methods=["GET"])
@login_required
@spectree_serialize(response_model=GetEducationalOfferersResponseModel, api=blueprint.pro_private_schema)
def list_educational_offerers(query: GetEducationalOfferersQueryModel) -> GetEducationalOfferersResponseModel:
    offerer_id = query.offerer_id

    try:
        offerers = api.get_educational_offerers(offerer_id, current_user)

        return GetEducationalOfferersResponseModel(
            educationalOfferers=[GetEducationalOffererResponseModel.from_orm(offerer) for offerer in offerers]
        )

    except MissingOffererIdQueryParameter:
        raise ApiErrors({"offerer_id": "Missing query parameter"})


@private_api.route("/offerers/<offerer_id>", methods=["GET"])
@login_required
@spectree_serialize(response_model=GetOffererResponseModel, api=blueprint.pro_private_schema)
def get_offerer(offerer_id: str) -> GetOffererResponseModel:
    check_user_has_access_to_offerer(current_user, dehumanize(offerer_id))
    offerer = load_or_404(offerers_models.Offerer, offerer_id)

    return GetOffererResponseModel.from_orm(offerer)


@private_api.route("/offerers/<offerer_id>/api_keys", methods=["POST"])
@login_required
@spectree_serialize(response_model=GenerateOffererApiKeyResponse, api=blueprint.pro_private_schema)
def generate_api_key_route(offerer_id: str) -> GenerateOffererApiKeyResponse:
    check_user_has_access_to_offerer(current_user, dehumanize(offerer_id))
    offerer = load_or_404(offerers_models.Offerer, offerer_id)
    try:
        clear_key = api.generate_and_save_api_key(offerer.id)
    except ApiKeyCountMaxReached:
        raise ApiErrors({"api_key_count_max": "Le nombre de clés maximal a été atteint"})
    except ApiKeyPrefixGenerationError:
        raise ApiErrors({"api_key": "Could not generate api key"})

    return GenerateOffererApiKeyResponse(apiKey=clear_key)


@private_api.route("/offerers/api_keys/<api_key_prefix>", methods=["DELETE"])
@login_required
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
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
@spectree_serialize(on_success_status=201, response_model=GetOffererResponseModel, api=blueprint.pro_private_schema)
def create_offerer(body: CreateOffererQueryModel) -> GetOffererResponseModel:
    user_offerer = api.create_offerer(current_user, body)

    return GetOffererResponseModel.from_orm(user_offerer.offerer)


@private_api.route("/offerers/<humanized_offerer_id>/eac-eligibility", methods=["GET"])
@login_required
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def can_offerer_create_educational_offer(humanized_offerer_id: str):
    try:
        api.can_offerer_create_educational_offer(dehumanize(humanized_offerer_id))
    except CulturalPartnerNotFoundException:
        logger.info("This offerer has not been found in Adage", extra={"offerer_id": humanized_offerer_id})
        raise ApiErrors({"offerer": "not found in adage"}, 404)
    except AdageException:
        logger.info("Api call failed", extra={"offerer_id": humanized_offerer_id})
        raise ApiErrors({"adage_api": "error"}, 500)
