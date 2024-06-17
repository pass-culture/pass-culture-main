import flask
from flask import request
from flask_login import current_user
from flask_login import login_required
import pydantic.v1 as pydantic_v1
import sqlalchemy.orm as sqla_orm

from pcapi.connectors.entreprise import sirene
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions
from pcapi.core.offerers import models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.offerers import validation
from pcapi.core.offerers.models import Venue
from pcapi.models import feature
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import offerers_serialize
from pcapi.routes.serialization import venues_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.workers.update_all_venue_offers_accessibility_job import update_all_venue_offers_accessibility_job
from pcapi.workers.update_all_venue_offers_email_job import update_all_venue_offers_email_job
from pcapi.workers.update_all_venue_offers_withdrawal_details_job import update_all_venue_offers_withdrawal_details_job

from . import blueprint


@private_api.route("/venues/<int:venue_id>", methods=["GET"])
@login_required
@spectree_serialize(response_model=venues_serialize.GetVenueResponseModel, api=blueprint.pro_private_schema)
def get_venue(venue_id: int) -> venues_serialize.GetVenueResponseModel:
    venue = (
        models.Venue.query.filter(models.Venue.id == venue_id)
        .options(sqla_orm.joinedload(models.Venue.contact))
        .options(sqla_orm.joinedload(models.Venue.bankInformation))
        .options(sqla_orm.joinedload(models.Venue.managingOfferer).joinedload(models.Offerer.bankInformation))
        .options(
            sqla_orm.selectinload(models.Venue.pricing_point_links).joinedload(
                models.VenuePricingPointLink.pricingPoint
            )
        )
        .options(sqla_orm.selectinload(models.Venue.reimbursement_point_links))
        .options(sqla_orm.joinedload(models.Venue.collectiveDomains))
        .options(sqla_orm.joinedload(models.Venue.collectiveDmsApplications))
        .options(sqla_orm.joinedload(models.Venue.bankAccountLinks).joinedload(models.VenueBankAccountLink.bankAccount))
    ).one_or_none()
    if not venue:
        flask.abort(404)

    check_user_has_access_to_offerer(current_user, venue.managingOffererId)
    return venues_serialize.GetVenueResponseModel.from_orm(venue)


@private_api.route("/venues", methods=["GET"])
@login_required
@spectree_serialize(response_model=venues_serialize.GetVenueListResponseModel, api=blueprint.pro_private_schema)
def get_venues(query: venues_serialize.VenueListQueryModel) -> venues_serialize.GetVenueListResponseModel:
    if current_user.has_admin_role and not query.offerer_id:
        return venues_serialize.GetVenueListResponseModel(venues=[])

    venue_list = offerers_repository.get_filtered_venues(
        pro_user_id=current_user.id,
        user_is_admin=current_user.has_admin_role,
        active_offerers_only=query.active_offerers_only,
        offerer_id=query.offerer_id,
        validated_offerer=query.validated,
    )
    ids_of_venues_with_offers = (
        offerers_repository.get_ids_of_venues_with_offers(list({venue.managingOffererId for venue in venue_list}))
        if venue_list
        else []
    )
    return venues_serialize.GetVenueListResponseModel(
        venues=[
            venues_serialize.VenueListItemResponseModel.from_orm(venue, ids_of_venues_with_offers)
            for venue in venue_list
        ]
    )


@private_api.route("/venues", methods=["POST"])
@login_required
@spectree_serialize(
    response_model=venues_serialize.VenueResponseModel, on_success_status=201, api=blueprint.pro_private_schema
)
def post_create_venue(body: venues_serialize.PostVenueBodyModel) -> venues_serialize.VenueResponseModel:
    check_user_has_access_to_offerer(current_user, body.managingOffererId)

    if body.siret:
        siret_info = sirene.get_siret(body.siret)
        if not siret_info.active:
            raise ApiErrors(errors={"siret": ["SIRET is no longer active"]})
        body.name = siret_info.name  # type: ignore[assignment]
    validation.check_accessibility_compliance(body)
    venue = offerers_api.create_venue(body)

    return venues_serialize.VenueResponseModel.from_orm(venue)


@private_api.route("/venues/<int:venue_id>", methods=["PATCH"])
@login_required
@spectree_serialize(response_model=venues_serialize.GetVenueResponseModel, api=blueprint.pro_private_schema)
def edit_venue(venue_id: int, body: venues_serialize.EditVenueBodyModel) -> venues_serialize.GetVenueResponseModel:
    venue = Venue.query.get_or_404(venue_id)

    check_user_has_access_to_offerer(current_user, venue.managingOffererId)
    has_siret_changed = bool(body.siret and body.siret != venue.siret)
    if body.siret and not sirene.siret_is_active(body.siret, raise_if_non_public=has_siret_changed):
        raise ApiErrors(errors={"siret": ["SIRET is no longer active"]})

    not_venue_fields = {
        "isAccessibilityAppliedOnAllOffers",
        "isEmailAppliedOnAllOffers",
        "isWithdrawalAppliedOnAllOffers",
        "contact",
        "shouldSendMail",
        "openingHours",
    }
    update_venue_attrs = body.dict(exclude=not_venue_fields, exclude_unset=True)
    accessibility_fields = [
        "audioDisabilityCompliant",
        "mentalDisabilityCompliant",
        "motorDisabilityCompliant",
        "visualDisabilityCompliant",
    ]
    have_accessibility_changes = any(
        (field in update_venue_attrs and update_venue_attrs[field] != getattr(venue, field))
        for field in accessibility_fields
    )

    modifications = {
        field: value for field, value in update_venue_attrs.items() if venue.field_exists_and_has_changed(field, value)
    }
    validation.check_venue_edition(modifications, venue)

    have_withdrawal_details_changes = body.withdrawalDetails != venue.withdrawalDetails

    if feature.FeatureToggle.ENABLE_ADDRESS_WRITING_WHILE_CREATING_UPDATING_VENUE.is_active():
        offerers_api.update_venue_location(venue, modifications)

    venue = offerers_api.update_venue(
        venue,
        modifications,
        author=current_user,
        contact_data=body.contact,
        opening_hours=body.openingHours,
    )

    if have_accessibility_changes and body.isAccessibilityAppliedOnAllOffers:
        edited_accessibility = {field: getattr(venue, field) for field in accessibility_fields}
        update_all_venue_offers_accessibility_job.delay(venue, edited_accessibility)

    if have_withdrawal_details_changes and body.isWithdrawalAppliedOnAllOffers:
        update_all_venue_offers_withdrawal_details_job.delay(
            venue, body.withdrawalDetails, send_email_notification=body.shouldSendMail
        )

    if body.bookingEmail and body.isEmailAppliedOnAllOffers:
        update_all_venue_offers_email_job.delay(venue, body.bookingEmail)

    return venues_serialize.GetVenueResponseModel.from_orm(venue)


@private_api.route("/venues/<int:venue_id>/collective-data", methods=["PATCH"])
@login_required
@spectree_serialize(response_model=venues_serialize.GetVenueResponseModel, api=blueprint.pro_private_schema)
def edit_venue_collective_data(
    venue_id: int, body: venues_serialize.EditVenueCollectiveDataBodyModel
) -> venues_serialize.GetVenueResponseModel:
    venue = offerers_api.get_venue_by_id(venue_id)

    check_user_has_access_to_offerer(current_user, venue.managingOffererId)

    update_venue_attrs = body.dict(exclude_unset=True)
    venue = offerers_api.update_venue_collective_data(venue, **update_venue_attrs)

    return venues_serialize.GetVenueResponseModel.from_orm(venue)


@private_api.route("/venues/<int:venue_id>/pricing-point", methods=["POST"])
@login_required
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def link_venue_to_pricing_point(venue_id: int, body: venues_serialize.LinkVenueToPricingPointBodyModel) -> None:
    venue = Venue.query.get_or_404(venue_id)
    check_user_has_access_to_offerer(current_user, venue.managingOffererId)
    try:
        offerers_api.link_venue_to_pricing_point(venue, body.pricingPointId)
    except exceptions.CannotLinkVenueToPricingPoint as exc:
        raise ApiErrors({"code": "CANNOT_LINK_VENUE_TO_PRICING_POINT", "message": str(exc)}, status_code=400)


@private_api.route("/venues/<int:venue_id>/banner", methods=["POST"])
@login_required
@spectree_serialize(response_model=venues_serialize.GetVenueResponseModel, on_success_status=201)
def upsert_venue_banner(venue_id: int) -> venues_serialize.GetVenueResponseModel:
    venue = Venue.query.get_or_404(venue_id)

    check_user_has_access_to_offerer(current_user, venue.managingOffererId)

    try:
        venue_banner = venues_serialize.VenueBannerContentModel.from_request(request)
    except exceptions.InvalidVenueBannerContent as err:
        content = {"code": "INVALID_BANNER_CONTENT", "message": str(err)}
        raise ApiErrors(content, status_code=400)
    except exceptions.VenueBannerTooBig as err:
        content = {"code": "BANNER_TOO_BIG", "message": str(err)}
        raise ApiErrors(content, status_code=400)
    except pydantic_v1.ValidationError as err:
        locations = ", ".join(str(loc) for e in err.errors() for loc in e["loc"])
        content = {"code": "INVALID_BANNER_PARAMS", "message": locations}
        raise ApiErrors(content, status_code=400)

    offerers_api.save_venue_banner(
        user=current_user,
        venue=venue,
        content=venue_banner.content,
        image_credit=venue_banner.image_credit,  # type: ignore[arg-type]
        crop_params=venue_banner.crop_params,
    )

    return venues_serialize.GetVenueResponseModel.from_orm(venue)


@private_api.route("/venues/<int:venue_id>/banner", methods=["DELETE"])
@login_required
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def delete_venue_banner(venue_id: int) -> None:
    venue = Venue.query.get_or_404(venue_id)
    check_user_has_access_to_offerer(current_user, venue.managingOffererId)

    offerers_api.delete_venue_banner(venue)


@private_api.route("/venues/<int:venue_id>/stats", methods=["GET"])
@login_required
@spectree_serialize(
    on_success_status=200, response_model=venues_serialize.VenueStatsResponseModel, api=blueprint.pro_private_schema
)
def get_venue_stats(venue_id: int) -> venues_serialize.VenueStatsResponseModel:
    venue: Venue = Venue.query.get_or_404(venue_id)
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
    return venues_serialize.VenuesEducationalStatusesResponseModel(statuses=statuses)  # type: ignore[arg-type]


@private_api.route("/venues/<int:venue_id>/dashboard", methods=["GET"])
@login_required
@spectree_serialize(
    on_success_status=200, response_model=offerers_serialize.OffererStatsResponseModel, api=blueprint.pro_private_schema
)
def get_venue_stats_dashboard_url(venue_id: str) -> offerers_serialize.OffererStatsResponseModel:
    venue: Venue = Venue.query.get_or_404(venue_id)
    check_user_has_access_to_offerer(current_user, venue.managingOffererId)
    url = offerers_api.get_metabase_stats_iframe_url(venue.managingOfferer, venues=[venue])
    return offerers_serialize.OffererStatsResponseModel(dashboardUrl=url)


@private_api.route("/venues/siret/<siret>", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=venues_serialize.GetVenuesOfOffererFromSiretResponseModel, api=blueprint.pro_private_schema
)
def get_venues_of_offerer_from_siret(siret: str) -> venues_serialize.GetVenuesOfOffererFromSiretResponseModel:
    offerer, db_venues = offerers_repository.find_venues_of_offerer_from_siret(siret)
    venue_with_siret = next((v for v in db_venues if v.siret == siret), None)
    if venue_with_siret:
        db_venues.insert(0, db_venues.pop(db_venues.index(venue_with_siret)))
    return venues_serialize.GetVenuesOfOffererFromSiretResponseModel(
        offererSiren=offerer.siren if offerer else None,
        offererName=offerer.name if offerer else None,
        venues=[venues_serialize.VenueOfOffererFromSiretResponseModel.from_orm(venue) for venue in db_venues],
    )
