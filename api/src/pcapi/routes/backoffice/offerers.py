import json
import typing
import urllib

import sqlalchemy as sa

from pcapi.core.auth.utils import get_current_user
from pcapi.core.history import repository as history_repository
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.permissions import utils as perm_utils
from pcapi.models import api_errors
from pcapi.models import db
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
        offerers_models.UserOfferer.query.filter(offerers_models.UserOfferer.offererId == offerer_id)
        .options(sa.orm.joinedload(offerers_models.UserOfferer.user))
        .order_by(offerers_models.UserOfferer.id)
        .all()
    )
    return serialization.OffererAttachedUsersResponseModel(
        data=[
            serialization.OffererAttachedUser(
                id=user_offerer.user.id,
                firstName=user_offerer.user.firstName,
                lastName=user_offerer.user.lastName,
                email=user_offerer.user.email,
                phoneNumber=user_offerer.user.phoneNumber,
                user_offerer_id=user_offerer.id,
                validationStatus=user_offerer.validationStatus,
            )
            for user_offerer in users_offerer
        ]
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
            validationStatus=offerer_basic_info.validationStatus,
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
                individual=offers_stats.individual_offers.get("active", 0) if offers_stats.individual_offers else 0,
                collective=offers_stats.collective_offers.get("active", 0) if offers_stats.collective_offers else 0,
            ),
            inactive=serialization.BaseOffersStats(
                individual=offers_stats.individual_offers.get("inactive", 0) if offers_stats.individual_offers else 0,
                collective=offers_stats.collective_offers.get("inactive", 0) if offers_stats.collective_offers else 0,
            ),
        )
    )


@blueprint.backoffice_blueprint.route("offerers/<int:offerer_id>/history", methods=["GET"])
@spectree_serialize(response_model=serialization.HistoryResponseModel, on_success_status=200, api=blueprint.api)
@perm_utils.permission_required(perm_models.Permissions.READ_PRO_ENTITY)
def get_offerer_history(offerer_id: int) -> serialization.HistoryResponseModel:
    history = history_repository.find_all_actions_by_offerer(offerer_id)

    return serialization.HistoryResponseModel(
        data=[
            serialization.HistoryItem(
                type=action.actionType.value,
                date=action.actionDate,
                authorId=action.authorUserId,
                authorName=action.authorUser.publicName if action.authorUser else None,
                comment=action.comment,
                accountId=action.userId,
                accountName=action.user.publicName if action.user else None,
            )
            for action in history
        ]
    )


@blueprint.backoffice_blueprint.route("users_offerers/<int:user_offerer_id>/validate", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@perm_utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def validate_offerer_attachment(user_offerer_id: int) -> None:
    author_user = get_current_user()
    try:
        offerers_api.validate_offerer_attachment_by_id(user_offerer_id, author_user)
    except offerers_exceptions.UserOffererNotFoundException:
        raise api_errors.ResourceNotFoundError(errors={"user_offerer_id": "Le rattachement n'existe pas"})
    except offerers_exceptions.UserOffererAlreadyValidatedException:
        raise api_errors.ApiErrors(errors={"user_offerer_id": "Le rattachement est déjà validé"})


@blueprint.backoffice_blueprint.route("users_offerers/<int:user_offerer_id>/pending", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@perm_utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def set_offerer_attachment_pending(user_offerer_id: int, body: serialization.OptionalCommentRequest) -> None:
    author_user = get_current_user()
    try:
        offerers_api.set_offerer_attachment_pending(user_offerer_id, author_user, comment=body.comment)
    except offerers_exceptions.UserOffererNotFoundException:
        raise api_errors.ResourceNotFoundError(errors={"user_offerer_id": "Le rattachement n'existe pas"})


@blueprint.backoffice_blueprint.route("users_offerers/<int:user_offerer_id>/reject", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@perm_utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def reject_offerer_attachment(user_offerer_id: int, body: serialization.OptionalCommentRequest) -> None:
    author_user = get_current_user()
    try:
        offerers_api.reject_offerer_attachment(user_offerer_id, author_user, comment=body.comment)
    except offerers_exceptions.UserOffererNotFoundException:
        raise api_errors.ResourceNotFoundError(errors={"user_offerer_id": "Le rattachement n'existe pas"})


@blueprint.backoffice_blueprint.route("users_offerers/<int:user_offerer_id>/comment", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@perm_utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def comment_offerer_attachment(user_offerer_id: int, body: serialization.CommentRequest) -> None:
    author_user = get_current_user()
    try:
        offerers_api.add_comment_to_offerer_attachment(user_offerer_id, author_user, comment=body.comment)
    except offerers_exceptions.UserOffererNotFoundException:
        raise api_errors.ResourceNotFoundError(errors={"user_offerer_id": "La rattachement n'existe pas"})


@blueprint.backoffice_blueprint.route("offerers/<int:offerer_id>/validate", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@perm_utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def validate_offerer(offerer_id: int) -> None:
    author_user = get_current_user()
    try:
        offerers_api.validate_offerer_by_id(offerer_id, author_user)
    except offerers_exceptions.OffererNotFoundException:
        raise api_errors.ResourceNotFoundError(errors={"offerer_id": "La structure n'existe pas"})
    except offerers_exceptions.OffererAlreadyValidatedException:
        raise api_errors.ApiErrors(errors={"offerer_id": "La structure est déjà validée"})


@blueprint.backoffice_blueprint.route("offerers/<int:offerer_id>/reject", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@perm_utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def reject_offerer(offerer_id: int, body: serialization.OptionalCommentRequest) -> None:
    author_user = get_current_user()
    try:
        offerers_api.reject_offerer(offerer_id, author_user, comment=body.comment)
    except offerers_exceptions.OffererNotFoundException:
        raise api_errors.ResourceNotFoundError(errors={"offerer_id": "La structure n'existe pas"})
    except offerers_exceptions.OffererAlreadyRejectedException:
        raise api_errors.ApiErrors(errors={"offerer_id": "La structure est déjà rejetée"})


@blueprint.backoffice_blueprint.route("offerers/<int:offerer_id>/pending", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@perm_utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def set_offerer_pending(offerer_id: int, body: serialization.OptionalCommentRequest) -> None:
    author_user = get_current_user()
    try:
        offerers_api.set_offerer_pending(offerer_id, author_user, comment=body.comment)
    except offerers_exceptions.OffererNotFoundException:
        raise api_errors.ResourceNotFoundError(errors={"offerer_id": "La structure n'existe pas"})


@blueprint.backoffice_blueprint.route("offerers/<int:offerer_id>/comment", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@perm_utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def comment_offerer(offerer_id: int, body: serialization.CommentRequest) -> None:
    author_user = get_current_user()
    try:
        offerers_api.add_comment_to_offerer(offerer_id, author_user, comment=body.comment)
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


@blueprint.backoffice_blueprint.route("offerers/stats", methods=["GET"])
@spectree_serialize(response_model=serialization.OfferersStatsResponseModel, on_success_status=200, api=blueprint.api)
@perm_utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def get_offerers_stats() -> serialization.OfferersStatsResponseModel:
    stats = offerers_api.get_offerers_stats()

    return serialization.OfferersStatsResponseModel(
        data={status.name: stats.get(status, 0) for status in offerers_models.ValidationStatus}
    )


def _get_serialized_offerer_last_comment(offerer: offerers_models.Offerer) -> serialization.Comment | None:
    if offerer.action_history:
        actions_with_comment = list(filter(lambda a: bool(a.comment), offerer.action_history))
        if actions_with_comment:
            last = sorted(actions_with_comment, key=lambda a: a.actionDate, reverse=True)[0]
            return serialization.Comment(
                date=last.actionDate,
                author=f"{last.authorUser.firstName} {last.authorUser.lastName}" if last.authorUser else None,
                content=last.comment,
            )

    return None


def _get_offerer_status(offerer: offerers_models.Offerer) -> str:
    if offerer.validationStatus is not None:
        return offerer.validationStatus.value
    if offerer.validationToken is None:
        return offerers_models.ValidationStatus.VALIDATED.value
    return offerers_models.ValidationStatus.NEW.value


@blueprint.backoffice_blueprint.route("offerers/to_be_validated", methods=["GET"])
@spectree_serialize(
    response_model=serialization.ListOffererToBeValidatedResponseModel,
    on_success_status=200,
    api=blueprint.api,
)
@perm_utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def list_offerers_to_be_validated(
    query: serialization.OffererToBeValidatedQuery,
) -> serialization.ListOffererToBeValidatedResponseModel:
    filters = []
    if query.filter:
        filters = json.loads(urllib.parse.unquote_plus(query.filter))
    offerers = offerers_api.list_offerers_to_be_validated(filters)

    sorts = urllib.parse.unquote_plus(query.sort or "[]")
    try:
        sorted_offerers = utils.sort_query(
            offerers,
            db_utils.get_ordering_clauses_from_json(offerers_models.Offerer, sorts),
            default_ordering=offerers_models.Offerer.id,
        )
    except db_utils.BadSortError as err:
        raise api_errors.ApiErrors(errors={"sort": f"unable to process provided sorting options: {err}"})
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
                    status=_get_offerer_status(offerer),
                    step=None,  # TODO
                    siren=offerer.siren,
                    address=offerer.address,
                    postalCode=offerer.postalCode,
                    city=offerer.city,
                    owner=(
                        f"{offerer.UserOfferers[0].user.firstName} {offerer.UserOfferers[0].user.lastName}"
                        if offerer.UserOfferers
                        else None
                    ),
                    phoneNumber=(offerer.UserOfferers[0].user.phoneNumber if offerer.UserOfferers else None),
                    email=(offerer.UserOfferers[0].user.email if offerer.UserOfferers else None),
                    lastComment=_get_serialized_offerer_last_comment(offerer),
                    isTopActor=offerers_api.is_top_actor(offerer),
                )
                for offerer in paginated_offerers.items
            ],
        ),
    )

    return response


@blueprint.backoffice_blueprint.route("offerers/<int:offerer_id>/is_top_actor", methods=["PUT"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@perm_utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def toggle_top_actor(offerer_id: int, body: serialization.IsTopActorRequest) -> None:
    try:
        tag = offerers_models.OffererTag.query.filter(offerers_models.OffererTag.name == "top-acteur").one()
    except sa.exc.NoResultFound:
        raise api_errors.ResourceNotFoundError(errors={"global": "Le tag top-acteur n'existe pas"})

    # Add the tag if it doesn't already exist
    if body.isTopActor:
        try:
            db.session.add(offerers_models.OffererTagMapping(offererId=offerer_id, tagId=tag.id))
            db.session.commit()
        except sa.exc.IntegrityError:
            # Already in database
            db.session.rollback()

    # Remove the tag if it exists
    else:
        offerers_models.OffererTagMapping.query.filter(
            offerers_models.OffererTagMapping.offererId == offerer_id,
            offerers_models.OffererTagMapping.tagId == tag.id,
        ).delete()
        db.session.commit()
