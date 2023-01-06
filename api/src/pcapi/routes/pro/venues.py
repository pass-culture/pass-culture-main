import flask
from flask import request
from flask_login import current_user
from flask_login import login_required
import pydantic
import sqlalchemy.orm as sqla_orm

import pcapi.core.finance.models as finance_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions
from pcapi.core.offerers import models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.offerers.models import Venue
from pcapi.models import feature
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import as_dict
from pcapi.routes.serialization import offerers_serialize
from pcapi.routes.serialization import venues_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import dehumanize_or_raise
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.utils.rest import load_or_404
from pcapi.workers.update_all_venue_offers_accessibility_job import update_all_venue_offers_accessibility_job
from pcapi.workers.update_all_venue_offers_email_job import update_all_venue_offers_email_job
from pcapi.workers.update_all_venue_offers_withdrawal_details_job import update_all_venue_offers_withdrawal_details_job

from . import blueprint


@private_api.route("/venues/<venue_id>", methods=["GET"])
@login_required
@spectree_serialize(response_model=venues_serialize.GetVenueResponseModel, api=blueprint.pro_private_schema)
def get_venue(venue_id: str) -> venues_serialize.GetVenueResponseModel:
    dehumanized_id = dehumanize(venue_id)
    venue = (
        models.Venue.query.filter(models.Venue.id == dehumanized_id)
        .options(sqla_orm.joinedload(models.Venue.contact))
        .options(sqla_orm.joinedload(models.Venue.bankInformation))
        .options(sqla_orm.joinedload(models.Venue.businessUnit).joinedload(finance_models.BusinessUnit.bankAccount))
        .options(sqla_orm.joinedload(models.Venue.managingOfferer).joinedload(models.Offerer.bankInformation))
        .options(
            sqla_orm.joinedload(models.Venue.pricing_point_links).joinedload(models.VenuePricingPointLink.pricingPoint)
        )
        .options(sqla_orm.joinedload(models.Venue.reimbursement_point_links))
        .options(sqla_orm.joinedload(models.Venue.collectiveDomains))
    ).one_or_none()
    if not venue:
        flask.abort(404)

    check_user_has_access_to_offerer(current_user, venue.managingOffererId)
    return venues_serialize.GetVenueResponseModel.from_orm(venue)


@private_api.route("/venues/<venue_id>/collective-data", methods=["GET"])
@login_required
@spectree_serialize(response_model=venues_serialize.GetCollectiveVenueResponseModel, api=blueprint.pro_private_schema)
def get_venue_collective_data(venue_id: str) -> venues_serialize.GetCollectiveVenueResponseModel:
    dehumanized_id = dehumanize(venue_id)
    venue = (
        models.Venue.query.filter(models.Venue.id == dehumanized_id)
        .options(sqla_orm.joinedload(models.Venue.venueEducationalStatus))
        .options(sqla_orm.joinedload(models.Venue.collectiveDomains))
    ).one_or_none()
    if not venue:
        raise ApiErrors({"offerer": ["Aucun lieu trouvée pour cet id"]}, status_code=404)

    check_user_has_access_to_offerer(current_user, venue.managingOffererId)
    return venues_serialize.GetCollectiveVenueResponseModel.from_orm(venue)


@private_api.route("/venues", methods=["GET"])
@login_required
@spectree_serialize(response_model=venues_serialize.GetVenueListResponseModel, api=blueprint.pro_private_schema)
def get_venues(query: venues_serialize.VenueListQueryModel) -> venues_serialize.GetVenueListResponseModel:
    offerer_id = dehumanize(query.offerer_id) if query.offerer_id else None
    venue_list = offerers_repository.get_filtered_venues(
        pro_user_id=current_user.id,
        user_is_admin=current_user.has_admin_role,
        active_offerers_only=query.active_offerers_only,
        offerer_id=offerer_id,
        validated_offerer=query.validated,
    )

    return venues_serialize.GetVenueListResponseModel(
        venues=[
            venues_serialize.VenueListItemResponseModel(
                id=venue.id,
                nonHumanizedId=venue.id,
                managingOffererId=venue.managingOfferer.id,
                name=venue.name,
                offererName=venue.managingOfferer.name,
                publicName=venue.publicName,
                isVirtual=venue.isVirtual,
                bookingEmail=venue.bookingEmail,
                withdrawalDetails=venue.withdrawalDetails,
                audioDisabilityCompliant=venue.audioDisabilityCompliant,
                mentalDisabilityCompliant=venue.mentalDisabilityCompliant,
                motorDisabilityCompliant=venue.motorDisabilityCompliant,
                visualDisabilityCompliant=venue.visualDisabilityCompliant,
                businessUnitId=venue.businessUnitId,
                siret=venue.siret,
                isBusinessUnitMainVenue=venue.isBusinessUnitMainVenue,
            )
            for venue in venue_list
        ]
    )


@private_api.route("/venues", methods=["POST"])
@login_required
@spectree_serialize(
    response_model=venues_serialize.VenueResponseModel, on_success_status=201, api=blueprint.pro_private_schema
)
def post_create_venue(body: venues_serialize.PostVenueBodyModel) -> venues_serialize.VenueResponseModel:
    dehumanized_managing_offerer_id = dehumanize(body.managingOffererId)
    check_user_has_access_to_offerer(current_user, dehumanized_managing_offerer_id)  # type: ignore [arg-type]
    venue = offerers_api.create_venue(body)

    return venues_serialize.VenueResponseModel.from_orm(venue)


@private_api.route("/venues/<venue_id>", methods=["PATCH"])
@login_required
@spectree_serialize(response_model=venues_serialize.GetVenueResponseModel, api=blueprint.pro_private_schema)
def edit_venue(venue_id: str, body: venues_serialize.EditVenueBodyModel) -> venues_serialize.GetVenueResponseModel:
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
    venue = offerers_api.update_venue(venue, contact_data=body.contact, **update_venue_attrs)
    venue_attrs = as_dict(venue)

    if have_accessibility_changes and body.isAccessibilityAppliedOnAllOffers:
        edited_accessibility = {field: venue_attrs[field] for field in accessibility_fields}
        update_all_venue_offers_accessibility_job.delay(venue, edited_accessibility)

    if have_withdrawal_details_changes and body.isWithdrawalAppliedOnAllOffers:
        update_all_venue_offers_withdrawal_details_job.delay(venue, body.withdrawalDetails)

    if body.bookingEmail and body.isEmailAppliedOnAllOffers:
        update_all_venue_offers_email_job.delay(venue, body.bookingEmail)

    return venues_serialize.GetVenueResponseModel.from_orm(venue)


@private_api.route("/venues/<venue_id>/collective-data", methods=["PATCH"])
@login_required
@spectree_serialize(response_model=venues_serialize.GetVenueResponseModel, api=blueprint.pro_private_schema)
def edit_venue_collective_data(
    venue_id: str, body: venues_serialize.EditVenueCollectiveDataBodyModel
) -> venues_serialize.GetVenueResponseModel:
    dehumanized_venue_id = dehumanize_or_raise(venue_id)
    venue = offerers_api.get_venue_by_id(dehumanized_venue_id)

    check_user_has_access_to_offerer(current_user, venue.managingOffererId)

    update_venue_attrs = body.dict(exclude_unset=True)
    venue = offerers_api.update_venue_collective_data(venue, **update_venue_attrs)

    return venues_serialize.GetVenueResponseModel.from_orm(venue)


@private_api.route("/venues/<venue_id>/pricing-point", methods=["POST"])
@login_required
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def link_venue_to_pricing_point(venue_id: str, body: venues_serialize.LinkVenueToPricingPointBodyModel) -> None:
    if not feature.FeatureToggle.ENABLE_NEW_BANK_INFORMATIONS_CREATION.is_active():
        raise feature.DisabledFeatureError("This function is behind a deactivated feature flag.")
    venue = load_or_404(Venue, venue_id)
    check_user_has_access_to_offerer(current_user, venue.managingOffererId)
    try:
        offerers_api.link_venue_to_pricing_point(venue, body.pricingPointId)
    except exceptions.CannotLinkVenueToPricingPoint as exc:
        raise ApiErrors({"code": "CANNOT_LINK_VENUE_TO_PRICING_POINT", "message": str(exc)}, status_code=400)


@private_api.route("/venues/<venue_id>/banner", methods=["POST"])
@login_required
@spectree_serialize(response_model=venues_serialize.GetVenueResponseModel, on_success_status=201)
def upsert_venue_banner(venue_id: str) -> venues_serialize.GetVenueResponseModel:
    venue = load_or_404(Venue, venue_id)

    check_user_has_access_to_offerer(current_user, venue.managingOffererId)

    try:
        venue_banner = venues_serialize.VenueBannerContentModel.from_request(request)
    except exceptions.InvalidVenueBannerContent as err:
        content = {"code": "INVALID_BANNER_CONTENT", "message": str(err)}
        raise ApiErrors(content, status_code=400)
    except exceptions.VenueBannerTooBig as err:
        content = {"code": "BANNER_TOO_BIG", "message": str(err)}
        raise ApiErrors(content, status_code=400)
    except pydantic.ValidationError as err:
        locations = ", ".join([loc for e in err.errors() for loc in e["loc"]])  # type: ignore [misc]
        content = {"code": "INVALID_BANNER_PARAMS", "message": locations}
        raise ApiErrors(content, status_code=400)

    offerers_api.save_venue_banner(
        user=current_user,
        venue=venue,
        content=venue_banner.content,
        image_credit=venue_banner.image_credit,  # type: ignore [arg-type]
        crop_params=venue_banner.crop_params,
    )

    return venues_serialize.GetVenueResponseModel.from_orm(venue)


@private_api.route("/venues/<venue_id>/banner", methods=["DELETE"])
@login_required
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def delete_venue_banner(venue_id: str) -> None:
    venue = load_or_404(Venue, venue_id)
    check_user_has_access_to_offerer(current_user, venue.managingOffererId)

    offerers_api.delete_venue_banner(venue)


@private_api.route("/venues/<humanized_venue_id>/stats", methods=["GET"])
@login_required
@spectree_serialize(
    on_success_status=200, response_model=venues_serialize.VenueStatsResponseModel, api=blueprint.pro_private_schema
)
def get_venue_stats(humanized_venue_id: str) -> venues_serialize.VenueStatsResponseModel:
    venue: Venue = load_or_404(Venue, humanized_venue_id)
    check_user_has_access_to_offerer(current_user, venue.managingOffererId)

    (
        active_bookings_quantity,
        validated_bookings_count,
        active_offers_count,
        sold_out_offers_count,
    ) = offerers_repository.get_venue_stats(venue.id)

    return venues_serialize.VenueStatsResponseModel(
        activeBookingsQuantity=active_bookings_quantity,
        validatedBookingsQuantity=validated_bookings_count,
        activeOffersCount=active_offers_count,
        soldOutOffersCount=sold_out_offers_count,
    )


@private_api.route("/venues-educational-statuses", methods=["GET"])
@login_required
@spectree_serialize(
    on_success_status=200,
    response_model=venues_serialize.VenuesEducationalStatusesResponseModel,
    api=blueprint.pro_private_schema,
)
def get_venues_educational_statuses() -> venues_serialize.VenuesEducationalStatusesResponseModel:
    statuses = offerers_api.get_venues_educational_statuses()
    return venues_serialize.VenuesEducationalStatusesResponseModel(statuses=statuses)


@private_api.route("/venues/<humanized_venue_id>/dashboard", methods=["GET"])
@login_required
@spectree_serialize(
    on_success_status=200, response_model=offerers_serialize.OffererStatsResponseModel, api=blueprint.pro_private_schema
)
def get_venue_stats_dashboard_url(humanized_venue_id: str) -> offerers_serialize.OffererStatsResponseModel:
    venue: Venue = load_or_404(Venue, humanized_venue_id)
    check_user_has_access_to_offerer(current_user, venue.managingOffererId)
    url = offerers_api.get_metabase_stats_iframe_url(venue.managingOfferer, venues=[venue])
    return offerers_serialize.OffererStatsResponseModel(dashboardUrl=url)
