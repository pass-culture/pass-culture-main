import logging

from flask_login import current_user
from flask_login import login_required
import sqlalchemy.orm as sqla_orm

import pcapi.core.educational.exceptions as educational_exceptions
from pcapi.core.offerers import api
from pcapi.core.offerers import repository
from pcapi.core.offerers.exceptions import ApiKeyCountMaxReached
from pcapi.core.offerers.exceptions import ApiKeyDeletionDenied
from pcapi.core.offerers.exceptions import ApiKeyPrefixGenerationError
from pcapi.core.offerers.exceptions import MissingOffererIdQueryParameter
import pcapi.core.offerers.models as offerers_models
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import transaction
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import offerers_serialize
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


N_VENUES_THRESHOLD_TO_SHOW_OFFER_COUNT = 20


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

    # UserOfferer is already JOINed, by get_all_offerers_for_user, if current_user does not have the admin role
    if current_user.has_admin_role:
        option = sqla_orm.joinedload(offerers_models.Offerer.UserOfferers)
    else:
        option = sqla_orm.contains_eager(offerers_models.Offerer.UserOfferers)
    offerers_query = offerers_query.options(option)

    offerers_query = offerers_query.options(
        sqla_orm.joinedload(offerers_models.Offerer.managedVenues).load_only(
            offerers_models.Venue.id,
            offerers_models.Venue.isVirtual,
        ),
        sqla_orm.load_only(
            offerers_models.Offerer.id,
            offerers_models.Offerer.name,
            offerers_models.Offerer.siren,
            offerers_models.Offerer.validationToken,
        ),
    )

    offerers_query = offerers_query.order_by(offerers_models.Offerer.name, offerers_models.Offerer.id)
    offerers_query = offerers_query.distinct(offerers_models.Offerer.name, offerers_models.Offerer.id)
    offerers_query = offerers_query.paginate(  # type: ignore [attr-defined]
        query.page,
        error_out=False,
        per_page=query.paginate,
    )

    offerers = offerers_query.items  # type: ignore [attr-defined]

    # Counting offers for large venues is costly. To avoid doing that
    # too much, we don't count offers for offerers that have many
    # venues (because most large offerers have venues with many
    # offers). Instead, we save a negative number, for which the
    # frontend has custom logic.
    offer_counts = {}
    venue_ids = set()
    for offerer in offerers:
        if len(offerer.managedVenues) >= N_VENUES_THRESHOLD_TO_SHOW_OFFER_COUNT:
            offer_counts.update({venue.id: -1 for venue in offerer.managedVenues})
        else:
            venue_ids |= {venue.id for venue in offerer.managedVenues}
    offer_counts.update(repository.get_offer_counts_by_venue(venue_ids))

    return GetOfferersListResponseModel(
        offerers=[
            offerers_serialize.GetOfferersResponseModel.from_orm(
                offerer,
                current_user,
                offer_counts,
            )
            for offerer in offerers
        ],
        nbTotalResults=offerers_query.total,  # type: ignore [attr-defined]
        user=current_user,
    )


@private_api.route("/offerers/names", methods=["GET"])
@login_required
@spectree_serialize(response_model=GetOfferersNamesResponseModel, api=blueprint.pro_private_schema)
def list_offerers_names(query: GetOfferersNamesQueryModel) -> GetOfferersNamesResponseModel:
    offerers = repository.get_all_offerers_for_user(
        user=current_user,
        validated=query.validated,
        include_non_validated_user_offerers=not query.validated_for_user,
    )
    offerers = offerers.order_by(offerers_models.Offerer.name, offerers_models.Offerer.id)
    offerers = offerers.distinct(offerers_models.Offerer.name, offerers_models.Offerer.id)

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
    check_user_has_access_to_offerer(current_user, dehumanize(offerer_id))  # type: ignore [arg-type]
    offerer = load_or_404(offerers_models.Offerer, offerer_id)
    return GetOffererResponseModel.from_orm(offerer)


@private_api.route("/offerers/<offerer_id>/api_keys", methods=["POST"])
@login_required
@spectree_serialize(response_model=GenerateOffererApiKeyResponse, api=blueprint.pro_private_schema)
def generate_api_key_route(offerer_id: str) -> GenerateOffererApiKeyResponse:
    check_user_has_access_to_offerer(current_user, dehumanize(offerer_id))  # type: ignore [arg-type]
    offerer = load_or_404(offerers_models.Offerer, offerer_id)
    try:
        clear_key = api.generate_and_save_api_key(offerer.id)  # type: ignore [attr-defined]
    except ApiKeyCountMaxReached:
        raise ApiErrors({"api_key_count_max": "Le nombre de clés maximal a été atteint"})
    except ApiKeyPrefixGenerationError:
        raise ApiErrors({"api_key": "Could not generate api key"})

    return GenerateOffererApiKeyResponse(apiKey=clear_key)


@private_api.route("/offerers/api_keys/<api_key_prefix>", methods=["DELETE"])
@login_required
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def delete_api_key(api_key_prefix: str):  # type: ignore [no-untyped-def]
    with transaction():
        try:
            api.delete_api_key_by_user(current_user, api_key_prefix)
        except sqla_orm.exc.NoResultFound:
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
def can_offerer_create_educational_offer(humanized_offerer_id: str):  # type: ignore [no-untyped-def]
    try:
        api.can_offerer_create_educational_offer(dehumanize(humanized_offerer_id))
    except educational_exceptions.CulturalPartnerNotFoundException:
        logger.info("This offerer has not been found in Adage", extra={"offerer_id": humanized_offerer_id})
        raise ApiErrors({"offerer": "not found in adage"}, 404)
    except educational_exceptions.AdageException:
        logger.info("Api call failed", extra={"offerer_id": humanized_offerer_id})
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
    return offerers_serialize.ReimbursementPointListResponseModel(
        __root__=[
            offerers_serialize.ReimbursementPointResponseModel(
                venueId=reimbursement_point.id,
                venueName=reimbursement_point.publicName or reimbursement_point.name,
                siret=reimbursement_point.siret,
                iban=reimbursement_point.iban,
                bic=reimbursement_point.bic,
            )
            for reimbursement_point in reimbursement_points
        ],
    )
