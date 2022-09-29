import typing

from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.permissions import utils as perm_utils
from pcapi.models import api_errors
from pcapi.repository import repository
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils import db as db_utils
from pcapi.utils import regions as regions_utils

from . import blueprint
from . import serialization
from . import utils


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
    response_model=serialization.OffererBasicInfoResponseModel,
    on_success_status=200,
    api=blueprint.api,
)
@perm_utils.permission_required(perm_models.Permissions.READ_PRO_ENTITY)
def get_offerer_basic_info(offerer_id: int) -> serialization.OffererBasicInfoResponseModel:

    offerer_basic_info = offerers_api.get_offerer_basic_info(offerer_id)

    if not offerer_basic_info:
        raise api_errors.ResourceNotFoundError(errors={"offerer_id": "La structure n'existe pas"})

    return serialization.OffererBasicInfoResponseModel(
        data=serialization.OffererBasicInfo(
            id=offerer_basic_info.id,
            name=offerer_basic_info.name,
            isActive=offerer_basic_info.isActive,
            siren=offerer_basic_info.siren,
            region=regions_utils.get_region_name_from_postal_code(offerer_basic_info.postalCode),
            bankInformationStatus=serialization.OffererBankInformationStatus(
                **{stat: (offerer_basic_info.bank_informations or {}).get(stat, 0) for stat in ("ko", "ok")}
            ),
            isCollectiveEligible=offerer_basic_info.is_collective_eligible,
        ),
    )


@blueprint.backoffice_blueprint.route("offerers/<int:offerer_id>/total_revenue", methods=["GET"])
@spectree_serialize(
    response_model=serialization.OffererTotalRevenueResponseModel,
    on_success_status=200,
    api=blueprint.api,
)
@perm_utils.permission_required(perm_models.Permissions.READ_PRO_ENTITY)
def get_offerer_total_revenue(offerer_id: int) -> serialization.OffererTotalRevenueResponseModel:
    total_revenue = offerers_api.get_offerer_total_revenue(offerer_id)

    return serialization.OffererTotalRevenueResponseModel(data=total_revenue)


@blueprint.backoffice_blueprint.route("offerers/<int:offerer_id>/offers_stats", methods=["GET"])
@spectree_serialize(
    response_model=serialization.OffererOfferStatsResponseModel,
    on_success_status=200,
    api=blueprint.api,
)
@perm_utils.permission_required(perm_models.Permissions.READ_PRO_ENTITY)
def get_offerer_offers_stats(offerer_id: int) -> serialization.OffererOfferStatsResponseModel:
    # TODO: réduire de le timeout de requête SQL pour ce endpoint
    #  (peu d'intérêt pour des grosses structures pour qui le requête va prendre
    #  de toute façon trop de temps, alors autant ne pas bourriner la DB pour rien)
    offers_stats = offerers_api.get_offerer_offers_stats(offerer_id)

    return serialization.OffererOfferStatsResponseModel(
        data=serialization.OffersStats(
            active=serialization.BaseOffersStats(
                individual=offers_stats.individual_offers["active"] if offers_stats.individual_offers else 0,
                collective=offers_stats.collective_offers["active"] if offers_stats.collective_offers else 0,
            ),
            inactive=serialization.BaseOffersStats(
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


@blueprint.backoffice_blueprint.route("offerers/tags", methods=["GET"])
@spectree_serialize(response_model=serialization.OffererTagsResponseModel, on_success_status=200, api=blueprint.api)
@perm_utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def get_offerers_tags_list() -> serialization.OffererTagsResponseModel:
    tags = offerers_models.OffererTag.query.order_by(offerers_models.OffererTag.label).all()
    return serialization.OffererTagsResponseModel(data=[serialization.OffererTagItem.from_orm(tag) for tag in tags])


@blueprint.backoffice_blueprint.route("offerers/<int:offerer_id>/tags/<string:tag_name>", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@perm_utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def add_tag_to_offerer(offerer_id: int, tag_name: str) -> None:
    tag = offerers_models.OffererTag.query.filter(offerers_models.OffererTag.name == tag_name).one_or_none()

    if tag is None:
        raise api_errors.ResourceNotFoundError(errors={"tag_name": "Le tag n'existe pas"})

    # save() method checks unique constraints and raises ApiErrors (400) in case of already existing mapping
    offerer_tag_mapping = offerers_models.OffererTagMapping(offererId=offerer_id, tagId=tag.id)
    repository.save(offerer_tag_mapping)


@blueprint.backoffice_blueprint.route("offerers/<int:offerer_id>/tags/<string:tag_name>", methods=["DELETE"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@perm_utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def remove_tag_from_offerer(offerer_id: int, tag_name: str) -> None:
    mapping_to_delete = (
        offerers_models.OffererTagMapping.query.join(offerers_models.OffererTag)
        .filter(
            offerers_models.OffererTagMapping.offererId == offerer_id,
            offerers_models.OffererTag.name == tag_name,
        )
        .one_or_none()
    )

    if mapping_to_delete is None:
        raise api_errors.ResourceNotFoundError(errors={"tag_name": "L'association structure - tag n'existe pas"})

    repository.delete(mapping_to_delete)


@blueprint.backoffice_blueprint.route("offerers/to_be_validated", methods=["GET"])
@spectree_serialize(
    response_model=serialization.Response,
    on_success_status=200,
    api=blueprint.api,
)
@perm_utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def list_offerers_to_be_validated(query: serialization.PaginableQuery) -> serialization.PaginatedResponse:
    offerers = offerers_api.list_offerers_to_be_validated()

    sorts = query.sort.split(",") if query.sort else []
    sorted_offerers = utils.sort_query(offerers, db_utils.get_ordering_clauses(offerers_models.Offerer, sorts))
    paginated_offerers = sorted_offerers.paginate(
        page=query.page,
        per_page=query.perPage,
    )

    response = typing.cast(
        serialization.ListOffererToBeValidatedResponseModel,
        utils.build_paginated_response(
            response_model=serialization.ListOffererToBeValidatedResponseModel,
            pages=paginated_offerers.pages,
            total=paginated_offerers.total,
            page=paginated_offerers.page,
            sort=query.sort,
            data=[
                serialization.OffererToBeValidated(
                    id=offerer.id,
                    name=offerer.name,
                    status="",  # TODO
                    step="",  # TODO
                    siren=offerer.siren,
                    address=offerer.address,
                    postalCode=offerer.postalCode,
                    city=offerer.city,
                    owner=f"{offerer.UserOfferers[0].user.firstName} {offerer.UserOfferers[0].user.lastName}",
                    phoneNumber=offerer.UserOfferers[0].user.phoneNumber,
                    email=offerer.UserOfferers[0].user.email,
                    lastComment=None,  # TODO
                )
                for offerer in paginated_offerers.items
            ],
        ),
    )

    return response
