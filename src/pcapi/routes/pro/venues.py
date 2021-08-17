from flask import request
from flask_login import current_user
from flask_login import login_required

from pcapi.core.bookings.repository import get_legacy_active_bookings_quantity_for_venue
from pcapi.core.bookings.repository import get_legacy_validated_bookings_quantity_for_venue
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.repository import get_active_offers_count_for_venue
from pcapi.core.offers.repository import get_sold_out_offers_count_for_venue
from pcapi.models.feature import FeatureToggle
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import as_dict
from pcapi.routes.serialization import venues_serialize
from pcapi.routes.serialization.venues_serialize import EditVenueBodyModel
from pcapi.routes.serialization.venues_serialize import GetVenueListResponseModel
from pcapi.routes.serialization.venues_serialize import GetVenueResponseModel
from pcapi.routes.serialization.venues_serialize import PostVenueBodyModel
from pcapi.routes.serialization.venues_serialize import VenueListItemResponseModel
from pcapi.routes.serialization.venues_serialize import VenueListQueryModel
from pcapi.routes.serialization.venues_serialize import VenueResponseModel
from pcapi.routes.serialization.venues_serialize import VenueStatsResponseModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.utils.rest import load_or_404
from pcapi.workers.update_all_venue_offers_accessibility_job import update_all_venue_offers_accessibility_job
from pcapi.workers.update_all_venue_offers_email_job import update_all_venue_offers_email_job
from pcapi.workers.update_all_venue_offers_withdrawal_details_job import update_all_venue_offers_withdrawal_details_job


@private_api.route("/venues/<venue_id>", methods=["GET"])
@login_required
@spectree_serialize(response_model=GetVenueResponseModel)
def get_venue(venue_id: str) -> GetVenueResponseModel:
    venue = load_or_404(Venue, venue_id)
    check_user_has_access_to_offerer(current_user, venue.managingOffererId)

    return GetVenueResponseModel.from_orm(venue)


@private_api.route("/venues", methods=["GET"])
@login_required
@spectree_serialize(response_model=GetVenueListResponseModel)
def get_venues(query: VenueListQueryModel) -> GetVenueListResponseModel:
    venue_list = offerers_repository.get_filtered_venues(
        pro_user_id=current_user.id,
        user_is_admin=current_user.isAdmin,
        active_offerers_only=query.active_offerers_only,
        offerer_id=query.offerer_id,
        validated_offerer=query.validated,
        validated_offerer_for_user=query.validated_for_user,
    )

    return GetVenueListResponseModel(
        venues=[
            VenueListItemResponseModel(
                id=venue.id,
                managingOffererId=venue.managingOfferer.id,
                name=venue.name,
                offererName=venue.managingOfferer.name,
                publicName=venue.publicName,
                isVirtual=venue.isVirtual,
                bookingEmail=venue.bookingEmail,
                withdrawalDetails=venue.withdrawalDetails,
            )
            for venue in venue_list
        ]
    )


@private_api.route("/venues", methods=["POST"])
@login_required
@spectree_serialize(response_model=VenueResponseModel, on_success_status=201)
def post_create_venue(body: PostVenueBodyModel) -> VenueResponseModel:
    dehumanized_managing_offerer_id = dehumanize(body.managingOffererId)
    check_user_has_access_to_offerer(current_user, dehumanized_managing_offerer_id)
    venue = offerers_api.create_venue(body)

    return VenueResponseModel.from_orm(venue)


@private_api.route("/venues/<venue_id>", methods=["PATCH"])
@login_required
@spectree_serialize(response_model=GetVenueResponseModel)
def edit_venue(venue_id: str, body: EditVenueBodyModel) -> GetVenueResponseModel:
    venue = load_or_404(Venue, venue_id)

    check_user_has_access_to_offerer(current_user, venue.managingOffererId)
    not_venue_fields = {
        "isAccessibilityAppliedOnAllOffers",
        "isEmailAppliedOnAllOffers",
        "isWithdrawalAppliedOnAllOffers",
        "contact",
    }
    update_venue_attrs = body.dict(exclude=not_venue_fields, exclude_unset=True)
    venue_attrs = as_dict(venue)
    accessibility_fields = [
        "audioDisabilityCompliant",
        "mentalDisabilityCompliant",
        "motorDisabilityCompliant",
        "visualDisabilityCompliant",
    ]
    have_accessibility_changes = any(
        (field in update_venue_attrs and update_venue_attrs[field] != venue_attrs[field])
        for field in accessibility_fields
    )
    have_withdrawal_details_changes = body.withdrawalDetails != venue.withdrawalDetails
    venue = offerers_api.update_venue(venue, body.contact, **update_venue_attrs)

    if have_accessibility_changes and body.isAccessibilityAppliedOnAllOffers:
        edited_accessibility = edited_accessibility = {
            field: update_venue_attrs[field]
            for field in accessibility_fields
            if field in update_venue_attrs and update_venue_attrs[field] != venue_attrs[field]
        }
        update_all_venue_offers_accessibility_job.delay(venue, edited_accessibility)

    if FeatureToggle.ENABLE_VENUE_WITHDRAWAL_DETAILS.is_active():
        if have_withdrawal_details_changes and body.isWithdrawalAppliedOnAllOffers:
            update_all_venue_offers_withdrawal_details_job.delay(venue, body.withdrawalDetails)

    if body.bookingEmail and body.isEmailAppliedOnAllOffers:
        update_all_venue_offers_email_job.delay(venue, body.bookingEmail)

    return GetVenueResponseModel.from_orm(venue)


@private_api.route("/venues/<venue_id>/banner", methods=["POST"])
@login_required
@spectree_serialize(on_success_status=204)
def upsert_venue_banner(venue_id: str) -> None:
    venue = load_or_404(Venue, venue_id)

    check_user_has_access_to_offerer(current_user, venue.managingOffererId)

    venue_banner = venues_serialize.VenueBannerContentModel.from_request(request)

    offerers_api.save_venue_banner(
        user=current_user,
        venue=venue,
        content=venue_banner.content,
        content_type=venue_banner.content_type,
        file_name=venue_banner.file_name,
    )


@private_api.route("/venues/<humanized_venue_id>/stats", methods=["GET"])
@login_required
@spectree_serialize(on_success_status=200, response_model=VenueStatsResponseModel)
def get_venue_stats(humanized_venue_id: str) -> VenueStatsResponseModel:
    venue = load_or_404(Venue, humanized_venue_id)
    check_user_has_access_to_offerer(current_user, venue.managingOffererId)

    active_bookings_quantity = get_legacy_active_bookings_quantity_for_venue(venue.id)
    validated_bookings_count = get_legacy_validated_bookings_quantity_for_venue(venue.id)
    active_offers_count = get_active_offers_count_for_venue(venue.id)
    sold_out_offers_count = get_sold_out_offers_count_for_venue(venue.id)

    return VenueStatsResponseModel(
        activeBookingsQuantity=active_bookings_quantity,
        validatedBookingsQuantity=validated_bookings_count,
        activeOffersCount=active_offers_count,
        soldOutOffersCount=sold_out_offers_count,
    )
