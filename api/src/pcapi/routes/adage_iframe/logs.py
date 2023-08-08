from pcapi.core.educational.repository import find_educational_institution_by_uai_code
import pcapi.core.educational.utils as educational_utils
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization import logs as serialization
from pcapi.routes.adage_iframe.serialization.adage_authentication import AdageFrontRoles
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.serialization.decorator import spectree_serialize


@blueprint.adage_iframe.route("/logs/catalog-view", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_catalog_view(
    authenticated_information: AuthenticatedInformation,
    body: serialization.CatalogViewBody,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)  # type: ignore [arg-type]
    educational_utils.log_information_for_data_purpose(
        event_name="CatalogView",
        extra_data={
            "source": body.source,
            "from": body.iframeFrom,
            "queryId": body.queryId,
        },
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
        user_email=authenticated_information.email,
    )
    return


@blueprint.adage_iframe.route("/logs/search-button", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_search_button_click(
    authenticated_information: AuthenticatedInformation,
    body: serialization.SearchBody,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)  # type: ignore [arg-type]
    extra_data = body.dict()
    extra_data["from"] = extra_data.pop("iframeFrom")
    educational_utils.log_information_for_data_purpose(
        event_name="SearchButtonClicked",
        user_email=authenticated_information.email,
        extra_data=extra_data,
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
    )
    return


@blueprint.adage_iframe.route("/logs/offer-detail", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_offer_details_button_click(
    authenticated_information: AuthenticatedInformation,
    body: serialization.StockIdBody,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)  # type: ignore [arg-type]
    educational_utils.log_information_for_data_purpose(
        event_name="OfferDetailButtonClick",
        extra_data={"stockId": body.stockId, "from": body.iframeFrom, "queryId": body.queryId},
        user_email=authenticated_information.email,
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
    )
    return


@blueprint.adage_iframe.route("/logs/offer-template-detail", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_offer_template_details_button_click(
    authenticated_information: AuthenticatedInformation,
    body: serialization.OfferIdBody,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)  # type: ignore [arg-type]
    educational_utils.log_information_for_data_purpose(
        event_name="TemplateOfferDetailButtonClick",
        extra_data={"offerId": body.offerId, "from": body.iframeFrom, "queryId": body.queryId},
        user_email=authenticated_information.email,
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
    )
    return


@blueprint.adage_iframe.route("/logs/booking-modal-button", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_booking_modal_button_click(
    authenticated_information: AuthenticatedInformation,
    body: serialization.StockIdBody,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)  # type: ignore [arg-type]
    educational_utils.log_information_for_data_purpose(
        event_name="BookingModalButtonClick",
        extra_data={"stockId": body.stockId, "from": body.iframeFrom, "queryId": body.queryId},
        user_email=authenticated_information.email,
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
    )
    return


@blueprint.adage_iframe.route("/logs/contact-modal-button", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_contact_modal_button_click(
    authenticated_information: AuthenticatedInformation,
    body: serialization.OfferIdBody,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)  # type: ignore [arg-type]
    educational_utils.log_information_for_data_purpose(
        event_name="ContactModalButtonClick",
        extra_data={
            "offerId": body.offerId,
            "from": body.iframeFrom,
            "queryId": body.queryId,
        },
        user_email=authenticated_information.email,
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
    )
    return


@blueprint.adage_iframe.route("/logs/fav-offer/", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_fav_offer_button_click(
    authenticated_information: AuthenticatedInformation,
    body: serialization.OfferIdBody,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)  # type: ignore [arg-type]
    educational_utils.log_information_for_data_purpose(
        event_name="FavOfferButtonClick",
        extra_data={"offerId": body.offerId, "from": body.iframeFrom, "queryId": body.queryId},
        user_email=authenticated_information.email,
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
    )
    return


@blueprint.adage_iframe.route("/logs/header-link-click/", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_header_link_click(
    authenticated_information: AuthenticatedInformation,
    body: serialization.AdageHeaderLogBody,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)  # type: ignore [arg-type]
    educational_utils.log_information_for_data_purpose(
        event_name="HeaderLinkClick",
        extra_data={"header_link_name": body.header_link_name.value, "from": body.iframeFrom, "queryId": body.queryId},
        user_email=authenticated_information.email,
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
    )


@blueprint.adage_iframe.route("/logs/request-popin-dismiss", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_request_form_popin_dismiss(
    authenticated_information: AuthenticatedInformation,
    body: serialization.CollectiveRequestBody,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)  # type: ignore [arg-type]
    extra_data = body.dict()
    extra_data["from"] = extra_data.pop("iframeFrom")
    educational_utils.log_information_for_data_purpose(
        event_name="RequestPopinDismiss",
        extra_data=extra_data,
        user_email=authenticated_information.email,
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
    )
    return


@blueprint.adage_iframe.route("/logs/tracking-filter", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_tracking_filter(
    authenticated_information: AuthenticatedInformation,
    body: serialization.TrackingFilterBody,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)  # type: ignore [arg-type]
    extra_data = body.dict()
    extra_data["from"] = extra_data.pop("iframeFrom")
    educational_utils.log_information_for_data_purpose(
        event_name="TrackingFilter",
        extra_data=extra_data,
        user_email=authenticated_information.email,
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
    )
    return


@blueprint.adage_iframe.route("/logs/sat-survey", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_open_satisfaction_survey(
    authenticated_information: AuthenticatedInformation,
    body: serialization.AdageBaseModel,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)  # type: ignore [arg-type]
    educational_utils.log_information_for_data_purpose(
        event_name="OpenSatisfactionSurvey",
        extra_data={
            "from": body.iframeFrom,
            "queryId": body.queryId,
        },
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
        user_email=authenticated_information.email,
    )
    return
