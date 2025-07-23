import datetime

import flask
import pydantic.v1 as pydantic_v1
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from flask import request
from flask_login import current_user
from flask_login import login_required

import pcapi.connectors.entreprise.exceptions as entreprise_exceptions
from pcapi import settings
from pcapi.connectors.entreprise import sirene
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions
from pcapi.core.offerers import models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.offerers import validation
from pcapi.core.offerers.models import Venue
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.models.utils import get_or_404
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import offerers_serialize
from pcapi.routes.serialization import venues_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.workers.update_all_venue_offers_accessibility_job import update_all_venue_offers_accessibility_job
from pcapi.workers.update_all_venue_offers_email_job import update_all_venue_offers_email_job

from . import blueprint


@private_api.route("/venues/<int:venue_id>", methods=["GET"])
@login_required
@spectree_serialize(response_model=venues_serialize.GetVenueResponseModel, api=blueprint.pro_private_schema)
def get_venue(venue_id: int) -> venues_serialize.GetVenueResponseModel:
    aliased_venue = sa_orm.aliased(models.Venue)

    venue = (
        db.session.query(models.Venue)
        .filter(models.Venue.id == venue_id)
        .options(sa_orm.joinedload(models.Venue.contact))
        .options(sa_orm.joinedload(models.Venue.managingOfferer))
        .options(
            sa_orm.selectinload(models.Venue.pricing_point_links).joinedload(models.VenuePricingPointLink.pricingPoint)
        )
        .options(sa_orm.joinedload(models.Venue.collectiveDomains))
        .options(sa_orm.joinedload(models.Venue.collectiveDmsApplications))
        .outerjoin(
            models.VenueBankAccountLink,
            sa.and_(
                models.VenueBankAccountLink.venueId == models.Venue.id,
                models.VenueBankAccountLink.timespan.contains(datetime.datetime.utcnow()),
            ),
        )
        .outerjoin(models.VenueBankAccountLink.bankAccount)
        .options(
            sa_orm.contains_eager(models.Venue.bankAccountLinks)
            .contains_eager(models.VenueBankAccountLink.bankAccount)
            # Avoid N+1 query and avoid cartesian product to load linkedVenues:
            .selectinload(finance_models.BankAccount.venueLinks)
            .joinedload(models.VenueBankAccountLink.venue.of_type(aliased_venue))
            .load_only(aliased_venue.id, aliased_venue.name, aliased_venue.publicName),
        )
        .options(sa_orm.joinedload(models.Venue.offererAddress).joinedload(models.OffererAddress.address))
        .options(sa_orm.selectinload(models.Venue.openingHours))
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


@private_api.route("/venues/<int:venue_id>", methods=["PATCH"])
@login_required
@spectree_serialize(response_model=venues_serialize.GetVenueResponseModel, api=blueprint.pro_private_schema)
def edit_venue(venue_id: int, body: venues_serialize.EditVenueBodyModel) -> venues_serialize.GetVenueResponseModel:
    venue = get_or_404(Venue, venue_id)

    check_user_has_access_to_offerer(current_user, venue.managingOffererId)
    has_siret_changed = bool(body.siret and body.siret != venue.siret)
    try:
        if body.siret and not sirene.siret_is_active(body.siret, raise_if_non_public=has_siret_changed):
            raise ApiErrors(errors={"siret": ["SIRET is no longer active"]})
    except entreprise_exceptions.UnknownEntityException:
        if settings.ENFORCE_SIRET_CHECK or not FeatureToggle.DISABLE_SIRET_CHECK.is_active():
            raise

    not_venue_fields = {
        "isAccessibilityAppliedOnAllOffers",
        "isManualEdition",
        "contact",
        "openingHours",
        "inseeCode",
    }
    location_fields = {"street", "banId", "latitude", "longitude", "postalCode", "city", "inseeCode", "isManualEdition"}
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
    update_location_attrs = body.dict(include=location_fields, exclude_unset=True)
    location_modifications = {
        field: value
        for field, value in update_location_attrs.items()
        if venue.offererAddress and venue.offererAddress.address.field_exists_and_has_changed(field, value)
    }
    validation.check_venue_edition(modifications, venue)

    venue = offerers_api.update_venue(
        venue,
        modifications,
        location_modifications,
        author=current_user,
        contact_data=body.contact,
        opening_hours=body.openingHours,
        is_manual_edition=body.isManualEdition or False,
    )

    if have_accessibility_changes and body.isAccessibilityAppliedOnAllOffers:
        edited_accessibility = {field: getattr(venue, field) for field in accessibility_fields}
        update_all_venue_offers_accessibility_job.delay(venue, edited_accessibility)

    if body.bookingEmail:
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
    venue = get_or_404(Venue, venue_id)
    check_user_has_access_to_offerer(current_user, venue.managingOffererId)
    try:
        offerers_api.link_venue_to_pricing_point(venue, body.pricingPointId)
    except exceptions.CannotLinkVenueToPricingPoint as exc:
        raise ApiErrors({"code": "CANNOT_LINK_VENUE_TO_PRICING_POINT", "message": str(exc)}, status_code=400)


@private_api.route("/venues/<int:venue_id>/banner", methods=["POST"])
@login_required
@spectree_serialize(response_model=venues_serialize.GetVenueResponseModel, on_success_status=201)
def upsert_venue_banner(venue_id: int) -> venues_serialize.GetVenueResponseModel:
    venue = get_or_404(Venue, venue_id)

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
    venue = get_or_404(Venue, venue_id)
    check_user_has_access_to_offerer(current_user, venue.managingOffererId)

    offerers_api.delete_venue_banner(venue)


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
    venue: Venue = get_or_404(Venue, venue_id)
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
