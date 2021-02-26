from typing import List

from flask import current_app as app
from flask import jsonify
from flask import request
from flask_login import current_user
from flask_login import login_required

from pcapi.core.offerers.api import create_digital_venue
from pcapi.core.offerers.repository import get_all
from pcapi.core.users.models import User
from pcapi.domain.admin_emails import maybe_send_offerer_validation_email
from pcapi.domain.user_emails import send_ongoing_offerer_attachment_information_email_to_pro
from pcapi.domain.user_emails import send_pro_user_waiting_for_validation_by_admin_email
from pcapi.flask_app import private_api
from pcapi.infrastructure.container import list_offerers_for_pro_user
from pcapi.models import ApiErrors
from pcapi.models import Offerer
from pcapi.models import UserOfferer
from pcapi.repository import repository
from pcapi.repository.offerer_queries import find_by_siren
from pcapi.routes.serialization import as_dict
from pcapi.routes.serialization.offerers_serialize import GetOffererNameResponseModel
from pcapi.routes.serialization.offerers_serialize import GetOffererResponseModel
from pcapi.routes.serialization.offerers_serialize import GetOfferersNamesQueryModel
from pcapi.routes.serialization.offerers_serialize import GetOfferersNamesResponseModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.use_cases.list_offerers_for_pro_user import OfferersRequestParameters
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.includes import OFFERER_INCLUDES
from pcapi.utils.mailing import MailServiceException
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.utils.rest import expect_json_data
from pcapi.utils.rest import load_or_404
from pcapi.utils.rest import login_or_api_key_required


def get_dict_offerer(offerer: Offerer) -> dict:
    offerer.append_user_has_access_attribute(user_id=current_user.id, is_admin=current_user.isAdmin)

    return as_dict(offerer, includes=OFFERER_INCLUDES)


def get_dict_offerers(offerers: List[Offerer]) -> list:
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
    offerers = get_all(
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


# @debt api-migration
@private_api.route("/offerers", methods=["POST"])
@login_or_api_key_required
@expect_json_data
def create_offerer():
    siren = request.json["siren"]
    offerer = find_by_siren(siren)

    if offerer is not None:
        user_offerer = offerer.grant_access(current_user)
        user_offerer.generate_validation_token()
        repository.save(user_offerer)

        try:
            send_ongoing_offerer_attachment_information_email_to_pro(user_offerer)
        except MailServiceException as mail_service_exception:
            app.logger.exception(
                "[send_ongoing_offerer_attachment_information_email_to_pro] " "Mail service failure",
                mail_service_exception,
            )
    else:
        offerer = Offerer()
        offerer.populate_from_dict(request.json)
        digital_venue = create_digital_venue(offerer)
        offerer.generate_validation_token()
        user_offerer = offerer.grant_access(current_user)
        repository.save(offerer, digital_venue, user_offerer)
        user = User.query.filter_by(id=user_offerer.userId).first()

        _send_to_pro_offer_validation_in_progress_email(user, offerer)

    _send_to_pc_admin_offerer_to_validate_email(offerer, user_offerer)

    return jsonify(get_dict_offerer(offerer)), 201


def _send_to_pro_offer_validation_in_progress_email(user: User, offerer: Offerer) -> None:
    try:
        send_pro_user_waiting_for_validation_by_admin_email(user, offerer)
    except MailServiceException as mail_service_exception:
        app.logger.exception(
            "[send_pro_user_waiting_for_validation_by_admin_email] " "Mail service failure", mail_service_exception
        )


def _send_to_pc_admin_offerer_to_validate_email(offerer: Offerer, user_offerer: UserOfferer) -> None:
    try:
        maybe_send_offerer_validation_email(offerer, user_offerer)
    except MailServiceException as mail_service_exception:
        app.logger.exception("[maybe_send_offerer_validation_email] " "Mail service failure", mail_service_exception)
