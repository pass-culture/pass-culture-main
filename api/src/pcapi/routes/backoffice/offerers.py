from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.permissions import utils as perm_utils
from pcapi.models import api_errors
from pcapi.serialization.decorator import spectree_serialize
import pcapi.utils.regions

from . import blueprint
from . import serialization


@blueprint.backoffice_blueprint.route("offerers/<int:offerer_id>/users", methods=["GET"])
@spectree_serialize(
    response_model=serialization.OffererAttachedUsersResponseModel,
    on_success_status=200,
    api=blueprint.api,
)
@perm_utils.permission_required(perm_models.Permissions.READ_PRO_ENTITY)
def get_offerer_users(offerer_id: int) -> serialization.OffererAttachedUsersResponseModel:
    """Get the list of all (pro) users attached to the offerer"""
    users_offerer: list[offerers_models.UserOfferer] = (
        offerers_models.UserOfferer.query.filter(
            offerers_models.UserOfferer.offererId == offerer_id, offerers_models.UserOfferer.isValidated
        )
        .order_by(offerers_models.UserOfferer.id)
        .all()
    )

    return serialization.OffererAttachedUsersResponseModel(
        data=[serialization.OffererAttachedUser.from_orm(user_offerer.user) for user_offerer in users_offerer]
    )


@blueprint.backoffice_blueprint.route("offerers/<int:offerer_id>", methods=["GET"])
@spectree_serialize(
    response_model=serialization.Response,
    on_success_status=200,
    api=blueprint.api,
)
@perm_utils.permission_required(perm_models.Permissions.READ_PRO_ENTITY)
def get_offerer_basic_info(offerer_id: int) -> serialization.Response:

    offerer_basic_info = offerers_api.get_offerer_basic_info(offerer_id)

    if not offerer_basic_info:
        raise api_errors.ResourceNotFoundError(errors={"offerer_id": "La structure n'existe pas"})

    return serialization.Response(
        data=serialization.OffererBasicInfo(
            id=offerer_basic_info.id,
            name=offerer_basic_info.name,
            isActive=offerer_basic_info.isActive,
            siren=offerer_basic_info.siren,
            region=pcapi.utils.regions.get_region_name_from_postal_code(offerer_basic_info.postalCode),
            bankInformationStatus=serialization.OffererBankInformationStatus(
                **{stat: (offerer_basic_info.bank_informations or {}).get(stat, 0) for stat in ("ko", "ok")}
            ),
            isCollectiveEligible=offerer_basic_info.is_collective_eligible,
        ),
    )


@blueprint.backoffice_blueprint.route("offerers/<int:offerer_id>/total_revenue", methods=["GET"])
@spectree_serialize(
    response_model=serialization.Response,
    on_success_status=200,
    api=blueprint.api,
)
@perm_utils.permission_required(perm_models.Permissions.READ_PRO_ENTITY)
def get_offerer_total_revenue(offerer_id: int) -> serialization.Response:
    total_revenue = offerers_api.get_offerer_total_revenue(offerer_id)

    return serialization.Response(data=total_revenue)


@blueprint.backoffice_blueprint.route("offerers/<int:offerer_id>/offers_stats", methods=["GET"])
@spectree_serialize(
    response_model=serialization.Response,
    on_success_status=200,
    api=blueprint.api,
)
@perm_utils.permission_required(perm_models.Permissions.READ_PRO_ENTITY)
def get_offerer_offers_stats(offerer_id: int) -> serialization.Response:
    # TODO: réduire de le timeout de requête SQL pour ce endpoint
    #  (peu d'intérêt pour des grosses structures pour qui le requête va prendre
    #  de toute façon trop de temps, alors autant ne pas bourriner la DB pour rien)
    offers_stats = offerers_api.get_offerer_offers_stats(offerer_id)

    return serialization.Response(
        data=serialization.OffererOffersStats(
            active=serialization.OffererBaseOffersStats(
                individual=offers_stats.individual_offers["active"] if offers_stats.individual_offers else 0,
                collective=offers_stats.collective_offers["active"] if offers_stats.collective_offers else 0,
            ),
            inactive=serialization.OffererBaseOffersStats(
                individual=offers_stats.individual_offers["inactive"] if offers_stats.individual_offers else 0,
                collective=offers_stats.collective_offers["inactive"] if offers_stats.collective_offers else 0,
            ),
        )
    )


@blueprint.backoffice_blueprint.route("offerers/<int:offerer_id>/validate", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@perm_utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def validate_offerer(offerer_id: int) -> None:
    try:
        offerers_api.validate_offerer_by_id(offerer_id)
    except offerers_exceptions.OffererNotFoundException:
        raise api_errors.ResourceNotFoundError(errors={"offerer_id": "La structure n'existe pas"})
