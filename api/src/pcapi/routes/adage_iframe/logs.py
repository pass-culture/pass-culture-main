import hashlib

from flask import current_app as app

from pcapi.core.educational import utils as educational_utils
from pcapi.core.educational.models import AdageFrontRoles
from pcapi.core.educational.repository import find_educational_institution_by_uai_code
from pcapi.repository.session_management import atomic
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization import logs as serialization
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.serialization.decorator import spectree_serialize


@blueprint.adage_iframe.route("/logs/catalog-view", methods=["POST"])
@atomic()
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_catalog_view(
    authenticated_information: AuthenticatedInformation,
    body: serialization.CatalogViewBody,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)
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


@blueprint.adage_iframe.route("/logs/offer-list-view-switch", methods=["POST"])
@atomic()
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_offer_list_view_switch(
    authenticated_information: AuthenticatedInformation,
    body: serialization.OfferListSwitch,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)
    educational_utils.log_information_for_data_purpose(
        event_name="OfferListSwitch",
        extra_data={
            "source": body.source,
            "from": body.iframeFrom,
            "queryId": body.queryId,
            "isMobile": body.isMobile,
        },
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
        user_email=authenticated_information.email,
    )


@blueprint.adage_iframe.route("/logs/search-button", methods=["POST"])
@atomic()
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_search_button_click(
    authenticated_information: AuthenticatedInformation,
    body: serialization.SearchBody,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)
    extra_data = body.dict()
    extra_data["from"] = extra_data.pop("iframeFrom")
    educational_utils.log_information_for_data_purpose(
        event_name="SearchButtonClicked",
        user_email=authenticated_information.email,
        extra_data=extra_data,
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
    )


@blueprint.adage_iframe.route("/logs/offer-detail", methods=["POST"])
@atomic()
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_offer_details_button_click(
    authenticated_information: AuthenticatedInformation,
    body: serialization.StockIdBody,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)
    educational_utils.log_information_for_data_purpose(
        event_name="OfferDetailButtonClick",
        extra_data={"stockId": body.stockId, "from": body.iframeFrom, "queryId": body.queryId, "vueType": body.vueType},
        user_email=authenticated_information.email,
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
    )


@blueprint.adage_iframe.route("/logs/offer-template-detail", methods=["POST"])
@atomic()
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_offer_template_details_button_click(
    authenticated_information: AuthenticatedInformation,
    body: serialization.OfferIdBody,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)
    educational_utils.log_information_for_data_purpose(
        event_name="TemplateOfferDetailButtonClick",
        extra_data={"offerId": body.offerId, "from": body.iframeFrom, "queryId": body.queryId, "vueType": body.vueType},
        user_email=authenticated_information.email,
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
    )


@blueprint.adage_iframe.route("/logs/booking-modal-button", methods=["POST"])
@atomic()
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_booking_modal_button_click(
    authenticated_information: AuthenticatedInformation,
    body: serialization.StockIdBody,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)
    educational_utils.log_information_for_data_purpose(
        event_name="BookingModalButtonClick",
        extra_data={
            "stockId": body.stockId,
            "from": body.iframeFrom,
            "queryId": body.queryId,
            "isFromNoResult": body.isFromNoResult,
        },
        user_email=authenticated_information.email,
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
    )


@blueprint.adage_iframe.route("/logs/contact-modal-button", methods=["POST"])
@atomic()
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_contact_modal_button_click(
    authenticated_information: AuthenticatedInformation,
    body: serialization.OfferBody,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)
    educational_utils.log_information_for_data_purpose(
        event_name="ContactModalButtonClick",
        extra_data={
            "offerId": body.offerId,
            "playlistId": body.playlistId,
            "from": body.iframeFrom,
            "queryId": body.queryId,
            "isFromNoResult": body.isFromNoResult,
        },
        user_email=authenticated_information.email,
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
    )


@blueprint.adage_iframe.route("/logs/consult-playlist-element", methods=["POST"])
@atomic()
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_consult_playlist_element(
    authenticated_information: AuthenticatedInformation,
    body: serialization.PlaylistBody,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)
    educational_utils.log_information_for_data_purpose(
        event_name="ConsultPlaylistElement",
        extra_data={
            "offerId": body.offerId if body.playlistType == serialization.AdagePlaylistType.OFFER else None,
            "venueId": body.venueId if body.playlistType == serialization.AdagePlaylistType.VENUE else None,
            "domainId": body.domainId if body.playlistType == serialization.AdagePlaylistType.DOMAIN else None,
            "index": body.index,
            "playlistId": body.playlistId,
            "from": body.iframeFrom,
            "queryId": body.queryId,
        },
        user_email=authenticated_information.email,
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
    )


@blueprint.adage_iframe.route("/logs/fav-offer/", methods=["POST"])
@atomic()
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_fav_offer_button_click(
    authenticated_information: AuthenticatedInformation,
    body: serialization.OfferFavoriteBody,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)
    educational_utils.log_information_for_data_purpose(
        event_name="FavOfferButtonClick",
        extra_data={
            "offerId": body.offerId,
            "from": body.iframeFrom,
            "queryId": body.queryId,
            "isFavorite": body.isFavorite,
            "isFromNoResult": body.isFromNoResult,
            "vueType": body.vueType,
            "playlistId": body.playlistId,
        },
        user_email=authenticated_information.email,
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
    )


@blueprint.adage_iframe.route("/logs/has-seen-whole-playlist/", methods=["POST"])
@atomic()
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_has_seen_whole_playlist(
    authenticated_information: AuthenticatedInformation,
    body: serialization.PlaylistBody,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)
    educational_utils.log_information_for_data_purpose(
        event_name="HasSeenWholePlaylist",
        extra_data={
            "playlistId": body.playlistId,
            "from": body.iframeFrom,
            "queryId": body.queryId,
        },
        user_email=authenticated_information.email,
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
    )


@blueprint.adage_iframe.route("/logs/header-link-click/", methods=["POST"])
@atomic()
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_header_link_click(
    authenticated_information: AuthenticatedInformation,
    body: serialization.AdageHeaderLogBody,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)
    educational_utils.log_information_for_data_purpose(
        event_name="HeaderLinkClick",
        extra_data={"header_link_name": body.header_link_name.value, "from": body.iframeFrom, "queryId": body.queryId},
        user_email=authenticated_information.email,
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
    )


@blueprint.adage_iframe.route("/logs/request-popin-dismiss", methods=["POST"])
@atomic()
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_request_form_popin_dismiss(
    authenticated_information: AuthenticatedInformation,
    body: serialization.CollectiveRequestBody,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)
    extra_data = body.dict()
    extra_data["from"] = extra_data.pop("iframeFrom")
    educational_utils.log_information_for_data_purpose(
        event_name="RequestPopinDismiss",
        extra_data=extra_data,
        user_email=authenticated_information.email,
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
    )


@blueprint.adage_iframe.route("/logs/tracking-filter", methods=["POST"])
@atomic()
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_tracking_filter(
    authenticated_information: AuthenticatedInformation,
    body: serialization.TrackingFilterBody,
) -> None:
    extra_data = body.dict()

    # It seems that this route is spammed sometimes by the front end
    # client (dozens of requests within a couple of seconds for the
    # same user). Therefore, we will compute a payload's hash and
    # store it 5s inside redis (if the key is already known, request
    # has already been logged).
    hashed_data = hashlib.new("md5", data=str(extra_data).encode("utf-8")).hexdigest()
    key = f"adage_iframe_tracking_filter_{hashed_data}"
    if app.redis_client.incr(key) == 1:
        # the key did not exist and has been created -> expire in 5s
        # incr is only used to perform exists & set.
        app.redis_client.expire(key, 5)
    else:
        return

    institution = find_educational_institution_by_uai_code(authenticated_information.uai)
    extra_data["from"] = extra_data.pop("iframeFrom")
    educational_utils.log_information_for_data_purpose(
        event_name="TrackingFilter",
        extra_data=extra_data,
        user_email=authenticated_information.email,
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
    )


@blueprint.adage_iframe.route("/logs/sat-survey", methods=["POST"])
@atomic()
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_open_satisfaction_survey(
    authenticated_information: AuthenticatedInformation,
    body: serialization.AdageBaseModel,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)
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


@blueprint.adage_iframe.route("/logs/tracking-autocompletion", methods=["POST"])
@atomic()
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_tracking_autocomplete_suggestion_click(
    authenticated_information: AuthenticatedInformation,
    body: serialization.TrackingAutocompleteSuggestionBody,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)
    educational_utils.log_information_for_data_purpose(
        event_name="logAutocompleteSuggestionClicked",
        extra_data={
            "from": body.iframeFrom,
            "queryId": body.queryId,
            "suggestionType": body.suggestionType.value,
            "suggestionValue": body.suggestionValue,
        },
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
        user_email=authenticated_information.email,
    )


@blueprint.adage_iframe.route("/logs/tracking-map", methods=["POST"])
@atomic()
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_tracking_map(
    authenticated_information: AuthenticatedInformation,
    body: serialization.AdageBaseModel,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)
    educational_utils.log_information_for_data_purpose(
        event_name="adageMapClicked",
        extra_data={"from": body.iframeFrom, "queryId": body.queryId, "isFromNoResult": body.isFromNoResult},
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
        user_email=authenticated_information.email,
    )


@blueprint.adage_iframe.route("/logs/playlist", methods=["POST"])
@atomic()
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_has_seen_all_playlist(
    authenticated_information: AuthenticatedInformation,
    body: serialization.AdageBaseModel,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)
    educational_utils.log_information_for_data_purpose(
        event_name="HasSeenAllPlaylist",
        extra_data={
            "from": body.iframeFrom,
            "queryId": body.queryId,
        },
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
        user_email=authenticated_information.email,
    )


@blueprint.adage_iframe.route("/logs/search-show-more", methods=["POST"])
@atomic()
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_search_show_more(
    authenticated_information: AuthenticatedInformation,
    body: serialization.TrackingShowMoreBody,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)
    educational_utils.log_information_for_data_purpose(
        event_name="SearchShowMore",
        extra_data={"source": body.source, "from": body.iframeFrom, "queryId": body.queryId, "type": body.type},
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
        user_email=authenticated_information.email,
    )


@blueprint.adage_iframe.route("/logs/tracking-cta-share", methods=["POST"])
@atomic()
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_tracking_cta_share(
    authenticated_information: AuthenticatedInformation,
    body: serialization.TrackingCTAShareBody,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)
    extra_data = body.dict()
    extra_data["from"] = extra_data.pop("iframeFrom")
    educational_utils.log_information_for_data_purpose(
        event_name="TrackingCTAShare",
        extra_data=extra_data,
        user_email=authenticated_information.email,
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
    )


@blueprint.adage_iframe.route("/logs/contact-url-click", methods=["POST"])
@atomic()
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_contact_url_click(
    authenticated_information: AuthenticatedInformation,
    body: serialization.OfferIdBody,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)
    educational_utils.log_information_for_data_purpose(
        event_name="ContactUrlClick",
        extra_data={
            "offerId": body.offerId,
            "from": body.iframeFrom,
            "queryId": body.queryId,
            "isFromNoResult": body.isFromNoResult,
        },
        user_email=authenticated_information.email,
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
    )


@blueprint.adage_iframe.route("/logs/highlight-banner", methods=["POST"])
@atomic()
@spectree_serialize(api=blueprint.api, on_error_statuses=[404], on_success_status=204)
@adage_jwt_required
def log_open_highlight_banner(
    authenticated_information: AuthenticatedInformation,
    body: serialization.HighlightBannerBody,
) -> None:
    institution = find_educational_institution_by_uai_code(authenticated_information.uai)
    educational_utils.log_information_for_data_purpose(
        event_name="OpenHighlightBanner",
        extra_data={"from": body.iframeFrom, "queryId": body.queryId, "banner": body.banner},
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
        user_email=authenticated_information.email,
    )
