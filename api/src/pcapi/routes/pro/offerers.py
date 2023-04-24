import logging

from flask_login import current_user
from flask_login import login_required
import sqlalchemy.orm as sqla_orm

import pcapi.core.educational.exceptions as educational_exceptions
from pcapi.core.offerers import api
from pcapi.core.offerers import repository
import pcapi.core.offerers.exceptions as offerers_exceptions
import pcapi.core.offerers.models as offerers_models
from pcapi.models import feature
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import transaction
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import offerers_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.feature import feature_required
from pcapi.utils.rest import check_user_has_access_to_offerer

from . import blueprint


logger = logging.getLogger(__name__)


@private_api.route("/offerers/names", methods=["GET"])
@login_required
@spectree_serialize(response_model=offerers_serialize.GetOfferersNamesResponseModel, api=blueprint.pro_private_schema)
def list_offerers_names(
    query: offerers_serialize.GetOfferersNamesQueryModel,
) -> offerers_serialize.GetOfferersNamesResponseModel:
    if query.offerer_id is not None:
        offerers = offerers_models.Offerer.query.filter(offerers_models.Offerer.id == query.offerer_id)
    else:
        offerers = repository.get_all_offerers_for_user(
            user=current_user,
            validated=query.validated,
            include_non_validated_user_offerers=not query.validated_for_user,
        )
        offerers = offerers.order_by(offerers_models.Offerer.name, offerers_models.Offerer.id)
        offerers = offerers.distinct(offerers_models.Offerer.name, offerers_models.Offerer.id)

    offerers = offerers.options(sqla_orm.load_only(offerers_models.Offerer.id, offerers_models.Offerer.name))

    return offerers_serialize.GetOfferersNamesResponseModel(
        offerersNames=[offerers_serialize.GetOffererNameResponseModel.from_orm(offerer) for offerer in offerers]
    )


@private_api.route("/offerers/educational", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=offerers_serialize.GetEducationalOfferersResponseModel, api=blueprint.pro_private_schema
)
def list_educational_offerers(
    query: offerers_serialize.GetEducationalOfferersQueryModel,
) -> offerers_serialize.GetEducationalOfferersResponseModel:
    offerer_id = query.offerer_id

    try:
        offerers = api.get_educational_offerers(offerer_id, current_user)

        return offerers_serialize.GetEducationalOfferersResponseModel(
            educationalOfferers=[
                offerers_serialize.GetEducationalOffererResponseModel.from_orm(offerer) for offerer in offerers
            ]
        )

    except offerers_exceptions.MissingOffererIdQueryParameter:
        raise ApiErrors({"offerer_id": "Missing query parameter"})


@private_api.route("/offerers/<int:offerer_id>", methods=["GET"])
@login_required
@spectree_serialize(response_model=offerers_serialize.GetOffererResponseModel, api=blueprint.pro_private_schema)
def get_offerer(offerer_id: int) -> offerers_serialize.GetOffererResponseModel:
    check_user_has_access_to_offerer(current_user, offerer_id)
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)
    return offerers_serialize.GetOffererResponseModel.from_orm(offerer)


@private_api.route("/offerers/<int:offerer_id>/api_keys", methods=["POST"])
@login_required
@spectree_serialize(response_model=offerers_serialize.GenerateOffererApiKeyResponse, api=blueprint.pro_private_schema)
def generate_api_key_route(offerer_id: int) -> offerers_serialize.GenerateOffererApiKeyResponse:
    check_user_has_access_to_offerer(current_user, offerer_id)
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)
    try:
        clear_key = api.generate_and_save_api_key(offerer.id)
    except offerers_exceptions.ApiKeyCountMaxReached:
        raise ApiErrors({"api_key_count_max": "Le nombre de clés maximal a été atteint"})
    except offerers_exceptions.ApiKeyPrefixGenerationError:
        raise ApiErrors({"api_key": "Could not generate api key"})

    return offerers_serialize.GenerateOffererApiKeyResponse(apiKey=clear_key)


@private_api.route("/offerers/api_keys/<api_key_prefix>", methods=["DELETE"])
@login_required
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def delete_api_key(api_key_prefix: str) -> None:
    with transaction():
        try:
            api.delete_api_key_by_user(current_user, api_key_prefix)
        except (sqla_orm.exc.NoResultFound, offerers_exceptions.ApiKeyDeletionDenied):
            raise ApiErrors({"prefix": "not found"}, 404)


@private_api.route("/offerers", methods=["POST"])
@login_required
@spectree_serialize(
    on_success_status=201, response_model=offerers_serialize.GetOffererResponseModel, api=blueprint.pro_private_schema
)
def create_offerer(body: offerers_serialize.CreateOffererQueryModel) -> offerers_serialize.GetOffererResponseModel:
    user_offerer = api.create_offerer(current_user, body)

    return offerers_serialize.GetOffererResponseModel.from_orm(user_offerer.offerer)


@private_api.route("/offerers/<int:offerer_id>/eac-eligibility", methods=["GET"])
@login_required
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def can_offerer_create_educational_offer(offerer_id: int) -> None:
    try:
        api.can_offerer_create_educational_offer(offerer_id)
    except educational_exceptions.CulturalPartnerNotFoundException:
        logger.info("This offerer has not been found in Adage", extra={"offerer_id": offerer_id})
        raise ApiErrors({"offerer": "not found in adage"}, 404)
    except educational_exceptions.AdageException:
        logger.info("Api call failed", extra={"offerer_id": offerer_id})
        raise ApiErrors({"adage_api": "error"}, 500)


@private_api.route("/offerers/<int:offerer_id>/reimbursement-points", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=offerers_serialize.ReimbursementPointListResponseModel,
    api=blueprint.pro_private_schema,
)
def get_available_reimbursement_points(
    offerer_id: int,
) -> offerers_serialize.ReimbursementPointListResponseModel:
    offerers_models.Offerer.query.get_or_404(offerer_id)
    check_user_has_access_to_offerer(current_user, offerer_id)

    reimbursement_points = repository.find_available_reimbursement_points_for_offerer(offerer_id)
    # TODO(fseguin, 2023-03-01): cleanup when WIP_ENABLE_NEW_ONBOARDING FF is removed
    return offerers_serialize.ReimbursementPointListResponseModel(
        __root__=[
            offerers_serialize.ReimbursementPointResponseModel(  # type: ignore [call-arg]
                venueId=reimbursement_point.id,
                venueName=reimbursement_point.common_name,  # type: ignore [arg-type]
                siret=reimbursement_point.siret,
                iban=reimbursement_point.iban,  # type: ignore [arg-type]
                bic=reimbursement_point.bic,
            )
            for reimbursement_point in reimbursement_points
        ],
    )


@private_api.route("/offerers/<int:offerer_id>/dashboard", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=offerers_serialize.OffererStatsResponseModel,
    api=blueprint.pro_private_schema,
)
def get_offerer_stats_dashboard_url(
    offerer_id: int,
) -> offerers_serialize.OffererStatsResponseModel:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)
    check_user_has_access_to_offerer(current_user, offerer.id)
    url = api.get_metabase_stats_iframe_url(offerer, venues=offerer.managedVenues)
    return offerers_serialize.OffererStatsResponseModel(dashboardUrl=url)


@private_api.route("/offerers/new", methods=["POST"])
@feature_required(feature.FeatureToggle.WIP_ENABLE_NEW_ONBOARDING)
@login_required
@spectree_serialize(
    on_success_status=201, response_model=offerers_serialize.GetOffererResponseModel, api=blueprint.pro_private_schema
)
def save_new_onboarding_data(
    body: offerers_serialize.SaveNewOnboardingDataQueryModel,
) -> offerers_serialize.GetOffererResponseModel:
    user_offerer = api.create_from_onboarding_data(current_user, body)
    return offerers_serialize.GetOffererResponseModel.from_orm(user_offerer.offerer)
