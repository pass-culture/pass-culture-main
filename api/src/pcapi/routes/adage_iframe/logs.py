import pcapi.core.educational.utils as educational_utils
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization import logs as serialization
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.serialization.decorator import spectree_serialize


@blueprint.adage_iframe.route("/logs/catalog-view", methods=["POST"])
@adage_jwt_required
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
def log_catalog_view(
    authenticated_information: AuthenticatedInformation,
    body: serialization.CatalogViewBody,
) -> None:
    educational_utils.log_information_for_data_purpose(
        event_name="CatalogView",
        extra_data={
            "source": body.source,
        },
        user_email=authenticated_information.email,
    )
    return


@blueprint.adage_iframe.route("/logs/search-button", methods=["POST"])
@adage_jwt_required
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
def log_search_button_click(
    authenticated_information: AuthenticatedInformation,
    body: serialization.SearchBody,
) -> None:
    educational_utils.log_information_for_data_purpose(
        event_name="SearchButtonClicked",
        user_email=authenticated_information.email,
        extra_data=body.dict(),
    )
    return


@blueprint.adage_iframe.route("/logs/offer-detail", methods=["POST"])
@adage_jwt_required
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
def log_offer_details_button_click(
    authenticated_information: AuthenticatedInformation,
    body: serialization.StockIdBody,
) -> None:
    educational_utils.log_information_for_data_purpose(
        event_name="OfferDetailButtonClick",
        extra_data={"stockId": body.stockId},
        user_email=authenticated_information.email,
    )
    return


@blueprint.adage_iframe.route("/logs/offer-template-detail", methods=["POST"])
@adage_jwt_required
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
def log_offer_template_details_button_click(
    authenticated_information: AuthenticatedInformation,
    body: serialization.OfferIdBody,
) -> None:
    educational_utils.log_information_for_data_purpose(
        event_name="TemplateOfferDetailButtonClick",
        extra_data={"offerId": body.offerId},
        user_email=authenticated_information.email,
    )
    return


@blueprint.adage_iframe.route("/logs/booking-modal-button", methods=["POST"])
@adage_jwt_required
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
def log_booking_modal_button_click(
    authenticated_information: AuthenticatedInformation,
    body: serialization.StockIdBody,
) -> None:
    educational_utils.log_information_for_data_purpose(
        event_name="BookingModalButtonClick",
        extra_data={"stockId": body.stockId},
        user_email=authenticated_information.email,
    )
    return


@blueprint.adage_iframe.route("/logs/contact-modal-button", methods=["POST"])
@adage_jwt_required
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
def log_contact_modal_button_click(
    authenticated_information: AuthenticatedInformation,
    body: serialization.OfferIdBody,
) -> None:
    educational_utils.log_information_for_data_purpose(
        event_name="ContactModalButtonClick",
        extra_data={"offerId": body.offerId},
        user_email=authenticated_information.email,
    )
    return
