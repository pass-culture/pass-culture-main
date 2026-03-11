from functools import partial

import flask
import pydantic.v1 as pydantic_v1
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from flask import request
from flask_login import current_user
from flask_login import login_required

import pcapi.connectors.entreprise.exceptions as entreprise_exceptions
from pcapi import settings
from pcapi.connectors.entreprise import api as entreprise_api
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions
from pcapi.core.offerers import models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.offerers import validation
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.venues import api as venues_api
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import tasks as offers_tasks
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.models.utils import get_or_404
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import venue_banners_serialize
from pcapi.routes.serialization import venue_collective_serialize
from pcapi.routes.serialization import venue_deprecated_serialization
from pcapi.routes.serialization import venue_finance_serialize
from pcapi.routes.serialization import venue_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils import date as date_utils
from pcapi.utils import siren as siren_utils
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.utils.rest import check_user_has_access_to_venues
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import on_commit

from . import blueprint


@private_api.route("/venues/<int:venue_id>", methods=["GET"])
@login_required
@atomic()
@spectree_serialize(response_model=venue_serialize.GetVenueResponseModel, api=blueprint.pro_private_schema)
def get_venue(venue_id: int) -> venue_serialize.GetVenueResponseModel:
    aliased_venue = sa_orm.aliased(models.Venue)

    venue = (
        db.session.query(models.Venue)
        .filter(models.Venue.id == venue_id)
        .options(sa_orm.joinedload(models.Venue.contact))
        .options(sa_orm.joinedload(models.Venue.managingOfferer))
        .options(sa_orm.joinedload(models.Venue.openingHours))
        .options(
            sa_orm.selectinload(models.Venue.pricing_point_links).joinedload(models.VenuePricingPointLink.pricingPoint)
        )
        .options(sa_orm.joinedload(models.Venue.collectiveDomains))
        .options(sa_orm.joinedload(models.Venue.collectiveDmsApplications))
        .outerjoin(
            models.VenueBankAccountLink,
            sa.and_(
                models.VenueBankAccountLink.venueId == models.Venue.id,
                models.VenueBankAccountLink.timespan.contains(date_utils.get_naive_utc_now()),
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
    ).one_or_none()
    if not venue:
        flask.abort(404)

    check_user_has_access_to_offerer(current_user, venue.managingOffererId)

    has_non_free_offers = offerers_repository.venue_has_non_free_offers(venue.id)
    return venue_serialize.GetVenueResponseModel.build(venue, has_non_free_offers)


@private_api.route("/venues", methods=["GET"])
@login_required
@atomic()
@spectree_serialize(
    response_model=venue_deprecated_serialization.GetVenueListResponseModel,
    api=blueprint.pro_private_schema,
    deprecated=True,
)
def get_venues(query: venue_serialize.VenueListQueryModel) -> venue_deprecated_serialization.GetVenueListResponseModel:
    """[deprecated] please use /lite/venues instead

    This route loads way too much data.
    """
    venue_list = offerers_repository.get_filtered_venues(
        pro_user_id=current_user.id,
        active_offerers_only=query.active_offerers_only,
        offerer_id=query.offerer_id,
        validated_offerer=query.validated,
        with_bank_account=True,
    )
    ids_of_venues_with_offers = (
        offerers_repository.get_ids_of_venues_with_offers(list({venue.managingOffererId for venue in venue_list}))
        if venue_list
        else []
    )

    # FIXME(jbaudet 13/11/2025): use venues_have_non_free_offers once
    # it has been fixed
    # venue_ids = [v.id for v in venue_list]
    # venue_ids_with_non_free_offers = offerers_repository.venues_have_non_free_offers(venue_ids)
    venue_ids_with_non_free_offers: set[int] = set()
    return venue_deprecated_serialization.GetVenueListResponseModel(
        venues=[
            venue_deprecated_serialization.VenueListItemResponseModel.build(
                venue, ids_of_venues_with_offers, venue_ids_with_non_free_offers
            )
            for venue in venue_list
        ]
    )


@private_api.route("/lite/venues", methods=["GET"])
@login_required
@spectree_serialize(response_model=venue_serialize.GetVenueListLiteResponseModel, api=blueprint.pro_private_schema)
def get_venues_lite() -> venue_serialize.GetVenueListLiteResponseModel:
    splitted = venues_api.fetch_user_venues_splitted_based_on_user_offerer_status(current_user.id)
    return venue_serialize.GetVenueListLiteResponseModel.build(splitted.others, splitted.with_pending_validation)


@private_api.route("/venues/<int:venue_id>", methods=["PATCH"])
@login_required
@atomic()
@spectree_serialize(response_model=venue_serialize.GetVenueResponseModel, api=blueprint.pro_private_schema)
def edit_venue(venue_id: int, body: venue_serialize.EditVenueBodyModel) -> venue_serialize.GetVenueResponseModel:
    venue = get_or_404(Venue, venue_id)

    check_user_has_access_to_offerer(current_user, venue.managingOffererId)
    try:
        is_valid_ridet = venue.is_caledonian and body.siret and siren_utils.is_ridet(body.siret)
        if body.siret and not is_valid_ridet and not entreprise_api.get_siret_open_data(body.siret).active:
            raise ApiErrors(errors={"siret": ["SIRET is no longer active"]})
    except entreprise_exceptions.UnknownEntityException:
        if settings.ENFORCE_SIRET_CHECK or not FeatureToggle.DISABLE_SIRET_CHECK.is_active():
            raise

    location_fields = {"street", "banId", "latitude", "longitude", "postalCode", "city", "inseeCode", "isManualEdition"}
    not_venue_fields = location_fields | {
        "isAccessibilityAppliedOnAllOffers",
        "contact",
        "openingHours",
        "culturalDomains",
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
    if "publicName" in modifications and not modifications["publicName"]:
        if venue.publicName == venue.name:
            del modifications["publicName"]
        else:
            modifications["publicName"] = venue.name
    update_location_attrs = body.dict(include=location_fields, exclude_unset=True)
    location_modifications = {
        field: value
        for field, value in update_location_attrs.items()
        if venue.offererAddress.address.field_exists_and_has_changed(field, value)
    }
    validation.check_venue_edition(modifications, venue)
    if "activity" in modifications:
        validation.check_activity_according_to_open_to_public(
            modifications["activity"], modifications.get("isOpenToPublic", venue.isOpenToPublic)
        )

    venue = offerers_api.update_venue(
        venue,
        modifications,
        location_modifications,
        author=current_user,
        contact_data=body.contact,
        opening_hours=body.openingHours,
        cultural_domains=body.culturalDomains,
        is_manual_edition=body.isManualEdition or False,
    )

    if have_accessibility_changes and body.isAccessibilityAppliedOnAllOffers:
        edited_accessibility = {field: getattr(venue, field) for field in accessibility_fields}
        accessibility_payload = offers_tasks.UpdateAllVenueOffersAccessibilityPayload(
            venue_id=venue.id,
            accessibility=edited_accessibility,
        )
        on_commit(
            partial(offers_tasks.update_all_venue_offers_accessibility_task.delay, accessibility_payload.model_dump())
        )

    if body.bookingEmail:
        email_payload = offers_tasks.UpdateAllVenueOffersEmailPayload(
            venue_id=venue.id,
            email=body.bookingEmail,
        )
        on_commit(partial(offers_tasks.update_all_venue_offers_email_task.delay, email_payload.model_dump()))

    has_non_free_offers = offerers_repository.venue_has_non_free_offers(venue.id)
    return venue_serialize.GetVenueResponseModel.build(venue, has_non_free_offers)


@private_api.route("/venues/<int:venue_id>/collective-data", methods=["PATCH"])
@login_required
@atomic()
@spectree_serialize(response_model=venue_serialize.GetVenueResponseModel, api=blueprint.pro_private_schema)
def edit_venue_collective_data(
    venue_id: int, body: venue_collective_serialize.EditVenueCollectiveDataBodyModel
) -> venue_serialize.GetVenueResponseModel:
    venue = get_or_404(Venue, venue_id)

    check_user_has_access_to_offerer(current_user, venue.managingOffererId)

    update_venue_attrs = body.dict(exclude_unset=True)
    venue = offerers_api.update_venue_collective_data(venue, **update_venue_attrs)

    has_non_free_offers = offerers_repository.venue_has_non_free_offers(venue.id)
    return venue_serialize.GetVenueResponseModel.build(venue, has_non_free_offers)


@private_api.route("/venues/<int:venue_id>/pricing-point", methods=["POST"])
@login_required
@atomic()
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def link_venue_to_pricing_point(venue_id: int, body: venue_finance_serialize.LinkVenueToPricingPointBodyModel) -> None:
    venue = get_or_404(Venue, venue_id)
    check_user_has_access_to_offerer(current_user, venue.managingOffererId)
    try:
        offerers_api.link_venue_to_pricing_point(venue, body.pricingPointId)
    except exceptions.CannotLinkVenueToPricingPoint as exc:
        raise ApiErrors({"code": "CANNOT_LINK_VENUE_TO_PRICING_POINT", "message": str(exc)}, status_code=400)


@private_api.route("/venues/<int:venue_id>/banner", methods=["POST"])
@login_required
@atomic()
@spectree_serialize(response_model=venue_serialize.GetVenueResponseModel, on_success_status=201)
def upsert_venue_banner(venue_id: int) -> venue_serialize.GetVenueResponseModel:
    venue = get_or_404(Venue, venue_id)

    check_user_has_access_to_offerer(current_user, venue.managingOffererId)

    try:
        venue_banner = venue_banners_serialize.VenueBannerContentModel.from_request(request)
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

    has_non_free_offers = offerers_repository.venue_has_non_free_offers(venue.id)
    return venue_serialize.GetVenueResponseModel.build(venue, has_non_free_offers)


@private_api.route("/venues/<int:venue_id>/banner", methods=["DELETE"])
@login_required
@atomic()
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def delete_venue_banner(venue_id: int) -> None:
    venue = get_or_404(Venue, venue_id)
    check_user_has_access_to_offerer(current_user, venue.managingOffererId)

    offerers_api.delete_venue_banner(venue)


@private_api.route("/venues-educational-statuses", methods=["GET"])
@login_required
@atomic()
@spectree_serialize(
    on_success_status=200,
    response_model=venue_collective_serialize.VenuesEducationalStatusesResponseModel,
    api=blueprint.pro_private_schema,
)
def get_venues_educational_statuses() -> venue_collective_serialize.VenuesEducationalStatusesResponseModel:
    statuses = offerers_api.get_venues_educational_statuses()
    return venue_collective_serialize.VenuesEducationalStatusesResponseModel(statuses=statuses)


@private_api.route("/venue/<int:venue_id>/offers-statistics", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(response_model=venue_serialize.GetOffersStatsResponseModel, api=blueprint.pro_private_schema)
def get_offers_statistics(venue_id: int) -> venue_serialize.GetOffersStatsResponseModel:
    venue = get_or_404(models.Venue, venue_id)
    check_user_has_access_to_venues(current_user, [venue_id])

    stats = offerers_api.get_offers_stats_by_venue(venue.id)
    return venue_serialize.GetOffersStatsResponseModel(
        published_public_offers=stats.published_public_offers,
        published_educational_offers=stats.published_educational_offers,
        pending_public_offers=stats.pending_public_offers,
        pending_educational_offers=stats.pending_educational_offers,
    )


@private_api.route("/venues/<int:venue_id>/locations", methods=["GET"])
@login_required
@spectree_serialize(
    on_success_status=200,
    api=blueprint.pro_private_schema,
    response_model=venue_serialize.GetVenueAddressesResponseModel,
)
def get_venue_addresses(
    venue_id: int, query: venue_serialize.GetVenueAddressesQueryModel
) -> venue_serialize.GetVenueAddressesResponseModel:
    check_user_has_access_to_venues(current_user, [venue_id])

    model: type[educational_models.CollectiveOfferTemplate | educational_models.CollectiveOffer | offers_models.Offer]
    if query.withOffersOption == venue_serialize.GetVenueAddressesWithOffersOption.COLLECTIVE_OFFER_TEMPLATES_ONLY:
        model = educational_models.CollectiveOfferTemplate
    if query.withOffersOption == venue_serialize.GetVenueAddressesWithOffersOption.COLLECTIVE_OFFERS_ONLY:
        model = educational_models.CollectiveOffer
    if query.withOffersOption == venue_serialize.GetVenueAddressesWithOffersOption.INDIVIDUAL_OFFERS_ONLY:
        model = offers_models.Offer

    results = offerers_repository.get_venue_addresses(venue_id, model)

    venue_addresses = [
        venue_serialize.GetVenueAddressResponseModel(
            id=result.id,
            addressId=result.addressId,
            label=result.label if hasattr(result, "label") and result.label else result.publicName,
            venueId=result.venueId,
            venueName=result.publicName,
            street=result.street,
            postalCode=result.postalCode,
            city=result.city,
            departmentCode=result.departmentCode,
        )
        for result in results
    ]

    return venue_serialize.GetVenueAddressesResponseModel(venue_addresses)
