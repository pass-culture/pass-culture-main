from datetime import datetime
import decimal
from functools import partial
import logging
import typing

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
from markupsafe import escape
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from werkzeug.exceptions import NotFound

from pcapi.connectors.clickhouse import queries as clickhouse_queries
from pcapi.connectors.entreprise import api as entreprise_api
from pcapi.connectors.entreprise import exceptions as entreprise_exceptions
from pcapi.connectors.entreprise import sirene
from pcapi.core import search
from pcapi.core.bookings import models as bookings_models
from pcapi.core.criteria import models as criteria_models
from pcapi.core.educational import models as educational_models
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import siret_api
from pcapi.core.geography import models as geography_models
from pcapi.core.history import models as history_models
from pcapi.core.history.api import add_action
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers import api as providers_api
from pcapi.core.providers import models as providers_models
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.repository.session_management import mark_transaction_as_invalid
from pcapi.repository.session_management import on_commit
from pcapi.routes.backoffice import autocomplete
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice import search_utils
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.routes.backoffice.pro import forms as pro_forms
from pcapi.routes.backoffice.pro.utils import get_connect_as
from pcapi.utils import regions as regions_utils
from pcapi.utils import string as string_utils
from pcapi.utils import urls
from pcapi.utils.clean_accents import clean_accents
from pcapi.utils.siren import is_valid_siret
from pcapi.utils.string import to_camelcase

from . import forms


logger = logging.getLogger(__name__)

venue_blueprint = utils.child_backoffice_blueprint(
    "venue",
    __name__,
    url_prefix="/pro/venue",
    permission=perm_models.Permissions.READ_PRO_ENTITY,
)


def _can_edit_siret() -> bool:
    return utils.has_current_user_permission(perm_models.Permissions.MOVE_SIRET)


def _get_venues(form: forms.GetVenuesListForm) -> list[offerers_models.Venue]:
    base_query = db.session.query(offerers_models.Venue).options(
        sa_orm.load_only(
            offerers_models.Venue.id,
            offerers_models.Venue.name,
            offerers_models.Venue.publicName,
            offerers_models.Venue.dateCreated,
            offerers_models.Venue.isPermanent,
        ),
        sa_orm.joinedload(offerers_models.Venue.managingOfferer).load_only(offerers_models.Offerer.name),
        sa_orm.joinedload(offerers_models.Venue.criteria).load_only(criteria_models.Criterion.name),
        sa_orm.joinedload(offerers_models.Venue.venueLabel).load_only(offerers_models.VenueLabel.label),
    )

    if form.q.data:
        search_query = form.q.data
        terms = search_utils.split_terms(search_query)

        if all(string_utils.is_numeric(term) for term in terms):
            base_query = base_query.filter(offerers_models.Venue.id.in_([int(term) for term in terms]))
        else:
            name_query = f"%{clean_accents(search_query)}%"
            base_query = base_query.filter(
                sa.or_(
                    sa.func.immutable_unaccent(offerers_models.Venue.name).ilike(name_query),
                    sa.func.immutable_unaccent(offerers_models.Venue.publicName).ilike(name_query),
                )
            )

    if form.venue_label.data:
        base_query = base_query.filter(offerers_models.Venue.venueLabelId.in_(form.venue_label.raw_data))

    if form.department.data or form.regions.data:
        base_query = base_query.outerjoin(offerers_models.Venue.offererAddress).outerjoin(
            offerers_models.OffererAddress.address
        )

        if form.department.data:
            base_query = base_query.filter(geography_models.Address.departmentCode.in_(form.department.data))

        if form.regions.data:
            department_codes: list[str] = []
            for region in form.regions.data:
                department_codes += regions_utils.get_department_codes_for_region(region)
            base_query = base_query.filter(geography_models.Address.departmentCode.in_(department_codes))

    if form.type.data:
        base_query = base_query.filter(offerers_models.Venue.venueTypeCode.in_(form.type.data))

    if form.criteria.data:
        base_query = base_query.outerjoin(offerers_models.Venue.criteria).filter(
            criteria_models.Criterion.id.in_(form.criteria.data)
        )

    if form.offerer.data:
        base_query = base_query.filter(offerers_models.Venue.managingOffererId.in_(form.offerer.data))

    if form.only_validated_offerers.data:
        base_query = base_query.join(offerers_models.Venue.managingOfferer).filter(offerers_models.Offerer.isValidated)

    if form.order.data:
        base_query = base_query.order_by(getattr(getattr(offerers_models.Venue, "id"), form.order.data)())
    # +1 to check if there are more results than requested
    return base_query.limit(form.limit.data + 1).all()


def get_venue(venue_id: int) -> sa.engine.Row:
    if utils.has_current_user_permission(perm_models.Permissions.READ_FRAUDULENT_BOOKING_INFO):
        has_fraudulent_booking_query: sa.sql.selectable.Exists | sa.sql.elements.Null = (
            sa.select(1)
            .select_from(bookings_models.Booking)
            .join(bookings_models.FraudulentBookingTag)
            .where(bookings_models.Booking.venueId == offerers_models.Venue.id)
            .correlate(offerers_models.Venue)
            .exists()
        )
    else:
        has_fraudulent_booking_query = sa.null()

    venue_query = (
        db.session.query(offerers_models.Venue, has_fraudulent_booking_query.label("has_fraudulent_booking"))
        .filter(offerers_models.Venue.id == venue_id)
        .options(
            sa_orm.joinedload(offerers_models.Venue.managingOfferer)
            .joinedload(offerers_models.Offerer.confidenceRule)
            .load_only(offerers_models.OffererConfidenceRule.confidenceLevel),
            sa_orm.joinedload(offerers_models.Venue.contact),
            sa_orm.joinedload(offerers_models.Venue.venueLabel),
            sa_orm.joinedload(offerers_models.Venue.criteria).load_only(criteria_models.Criterion.name),
            sa_orm.joinedload(offerers_models.Venue.venueProviders)
            .load_only(
                providers_models.VenueProvider.id,
                providers_models.VenueProvider.lastSyncDate,
                providers_models.VenueProvider.isActive,
            )
            .joinedload(providers_models.VenueProvider.provider)
            .load_only(
                providers_models.Provider.id,
                providers_models.Provider.name,
                providers_models.Provider.localClass,
                providers_models.Provider.isActive,
            ),
            sa_orm.joinedload(offerers_models.Venue.accessibilityProvider).load_only(
                offerers_models.AccessibilityProvider.externalAccessibilityId
            ),
            sa_orm.joinedload(offerers_models.Venue.confidenceRule).load_only(
                offerers_models.OffererConfidenceRule.confidenceLevel
            ),
            sa_orm.joinedload(offerers_models.Venue.offererAddress).joinedload(offerers_models.OffererAddress.address),
        )
    )

    venue = venue_query.one_or_none()

    if not venue:
        raise NotFound()

    return venue


def render_venue_details(venue_row: sa.engine.Row, edit_venue_form: forms.EditVirtualVenueForm | None = None) -> str:
    venue = venue_row.Venue
    region = ""
    if venue.offererAddress:
        region = (
            regions_utils.get_region_name_from_postal_code(venue.offererAddress.address.postalCode)
            if venue.offererAddress.address.postalCode
            else ""
        )

    if not edit_venue_form:
        if venue.isVirtual:
            edit_venue_form = forms.EditVirtualVenueForm(
                booking_email=venue.bookingEmail,
                phone_number=venue.contact.phone_number if venue.contact else None,
            )
        else:
            assert venue.offererAddress  # physical venues should have an address
            edit_venue_form = forms.EditVenueForm(
                venue=venue,
                name=venue.name,
                public_name=venue.publicName,
                siret=venue.siret,
                city=venue.offererAddress.address.city,
                postal_address_autocomplete=(
                    f"{venue.offererAddress.address.street}, {venue.offererAddress.address.postalCode} {venue.offererAddress.address.city}"
                    if venue.offererAddress.address.street is not None
                    and venue.offererAddress.address.city is not None
                    and venue.offererAddress.address.postalCode is not None
                    else None
                ),
                postal_code=venue.offererAddress.address.postalCode,
                street=venue.offererAddress.address.street,
                ban_id=venue.offererAddress.address.banId,
                insee_code=venue.offererAddress.address.inseeCode,
                acceslibre_url=venue.external_accessibility_url,
                booking_email=venue.bookingEmail,
                phone_number=venue.contact.phone_number if venue.contact else None,
                is_permanent=venue.isPermanent,
                latitude=venue.offererAddress.address.latitude,
                longitude=venue.offererAddress.address.longitude,
                venue_type_code=venue.venueTypeCode.name,
            )
            edit_venue_form.siret.flags.disabled = not _can_edit_siret()
        edit_venue_form.tags.choices = [(criterion.id, criterion.name) for criterion in venue.criteria]

    delete_form = empty_forms.EmptyForm()

    fraud_form = (
        forms.FraudForm(confidence_level=venue.confidenceLevel.value if venue.confidenceLevel else None)
        if utils.has_current_user_permission(perm_models.Permissions.PRO_FRAUD_ACTIONS)
        else None
    )

    search_form = pro_forms.CompactProSearchForm(
        q=request.args.get("q"),
        pro_type=pro_forms.TypeOptions.VENUE.name,
        departments=(
            request.args.getlist("departments")
            if request.args.get("q") or request.args.getlist("departments")
            else current_user.backoffice_profile.preferences.get("departments", [])
        ),
    )

    connect_as = get_connect_as(
        object_type="venue",
        object_id=venue.id,
        pc_pro_path=urls.build_pc_pro_venue_path(venue),
    )

    return render_template(
        "venue/get.html",
        search_form=search_form,
        search_dst=url_for("backoffice_web.pro.search_pro"),
        venue=venue,
        has_fraudulent_booking=venue_row.has_fraudulent_booking,
        address=venue.offererAddress.address if venue.offererAddress else None,
        edit_venue_form=edit_venue_form,
        region=region,
        delete_form=delete_form,
        fraud_form=fraud_form,
        active_tab=request.args.get("active_tab", "history"),
        connect_as=connect_as,
        zendesk_sell_synchronisation_form=(
            empty_forms.EmptyForm()
            if venue.isOpenToPublic
            and not venue.isVirtual
            and utils.has_current_user_permission(perm_models.Permissions.MANAGE_PRO_ENTITY)
            else None
        ),
    )


@venue_blueprint.route("", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def list_venues() -> utils.BackofficeResponse:
    form = forms.GetVenuesListForm(formdata=utils.get_query_params())

    if not form.validate():
        mark_transaction_as_invalid()
        return render_template("venue/list.html", rows=[], form=form), 400

    if form.is_empty():
        mark_transaction_as_invalid()
        return render_template("venue/list.html", rows=[], form=form)

    venues = _get_venues(form)
    venues = utils.limit_rows(venues, form.limit.data)

    autocomplete.prefill_criteria_choices(form.criteria)
    autocomplete.prefill_offerers_choices(form.offerer)

    form_url = partial(url_for, ".list_venues", **form.raw_data)
    date_created_sort_url = form_url(order="desc" if form.order.data == "asc" else "asc")

    return render_template("venue/list.html", rows=venues, form=form, date_created_sort_url=date_created_sort_url)


@venue_blueprint.route("/<int:venue_id>", methods=["GET"])
def get(venue_id: int) -> utils.BackofficeResponse:
    venue_row = get_venue(venue_id)

    if request.args.get("q") and request.args.get("search_rank"):
        utils.log_backoffice_tracking_data(
            event_name="ConsultCard",
            extra_data={
                "searchType": "ProSearch",
                "searchProType": pro_forms.TypeOptions.VENUE.name,
                "searchQuery": request.args.get("q"),
                "searchDepartments": ",".join(request.args.get("departments", [])),
                "searchRank": request.args.get("search_rank"),
                "searchNbResults": request.args.get("total_items"),
            },
        )

    return render_venue_details(venue_row)


# mypy doesn't like nested dict
@typing.no_type_check
def get_stats_data(venue_id: int) -> dict:
    PLACEHOLDER = -1
    offers_stats = offerers_api.get_venue_offers_stats(venue_id, max_offer_count=1000)

    is_collective_too_big = offers_stats["collective_offer"]["active"] == -1
    is_collective_too_big = is_collective_too_big or offers_stats["collective_offer_template"]["active"] == -1
    is_individual_too_big = offers_stats["offer"]["active"] == -1

    stats = {
        "active": {},
        "inactive": {},
        "total_revenue": PLACEHOLDER,
        "placeholder": PLACEHOLDER,
    }

    if is_collective_too_big:
        stats["active"]["collective"] = PLACEHOLDER
        stats["inactive"]["collective"] = PLACEHOLDER
        stats["active"]["total"] = PLACEHOLDER
        stats["inactive"]["total"] = PLACEHOLDER
    else:
        stats["active"]["collective"] = (
            offers_stats["collective_offer"]["active"] + offers_stats["collective_offer_template"]["active"]
        )
        stats["inactive"]["collective"] = (
            offers_stats["collective_offer"]["inactive"] + offers_stats["collective_offer_template"]["inactive"]
        )
    if is_individual_too_big:
        stats["active"]["individual"] = PLACEHOLDER
        stats["inactive"]["individual"] = PLACEHOLDER
        stats["active"]["total"] = PLACEHOLDER
        stats["inactive"]["total"] = PLACEHOLDER
    else:
        stats["active"]["individual"] = offers_stats["offer"]["active"]
        stats["inactive"]["individual"] = offers_stats["offer"]["inactive"]

    if not (is_collective_too_big or is_individual_too_big):
        stats["active"]["total"] = stats["active"]["collective"] + stats["active"]["individual"]
        stats["inactive"]["total"] = stats["inactive"]["collective"] + stats["inactive"]["individual"]

    if FeatureToggle.WIP_ENABLE_CLICKHOUSE_IN_BO.is_active():
        try:
            clickhouse_results = clickhouse_queries.TotalExpectedRevenueQuery().execute((venue_id,))
            stats["total_revenue"] = clickhouse_results[0].expected_revenue
        except ApiErrors:
            stats["total_revenue"] = PLACEHOLDER
    elif not (is_collective_too_big or is_individual_too_big):
        stats["total_revenue"] = offerers_api.get_venue_total_revenue(venue_id)

    return stats


@venue_blueprint.route("/<int:venue_id>/stats", methods=["GET"])
def get_stats(venue_id: int) -> utils.BackofficeResponse:
    venue_query = (
        db.session.query(offerers_models.Venue)
        .filter(offerers_models.Venue.id == venue_id)
        .options(
            sa_orm.joinedload(offerers_models.Venue.pricing_point_links).joinedload(
                offerers_models.VenuePricingPointLink.pricingPoint
            )
        )
        .outerjoin(
            offerers_models.VenueBankAccountLink,
            sa.and_(
                offerers_models.Venue.id == offerers_models.VenueBankAccountLink.venueId,
                offerers_models.VenueBankAccountLink.timespan.contains(datetime.utcnow()),
            ),
        )
        .outerjoin(offerers_models.VenueBankAccountLink.bankAccount)
        .options(
            sa_orm.contains_eager(offerers_models.Venue.bankAccountLinks)
            .load_only(offerers_models.VenueBankAccountLink.timespan)
            .contains_eager(offerers_models.VenueBankAccountLink.bankAccount)
            .load_only(finance_models.BankAccount.id, finance_models.BankAccount.label),
            sa_orm.joinedload(offerers_models.Venue.managingOfferer).load_only(
                offerers_models.Offerer.siren, offerers_models.Offerer.postalCode
            ),
        )
    )

    venue = venue_query.one_or_none()
    if not venue:
        raise NotFound()

    data = get_stats_data(venue.id)

    return render_template(
        "venue/get/stats.html",
        venue=venue,
        stats=data,
        pricing_point=venue.current_pricing_point,
    )


@venue_blueprint.route("/<int:venue_id>/revenue-details", methods=["GET"])
def get_revenue_details(venue_id: int) -> utils.BackofficeResponse:
    venue = (
        db.session.query(offerers_models.Venue)
        .filter_by(id=venue_id)
        .options(
            sa_orm.load_only(offerers_models.Venue.id),
            sa_orm.joinedload(offerers_models.Venue.managingOfferer).load_only(
                offerers_models.Offerer.siren, offerers_models.Offerer.postalCode
            ),
        )
        .one_or_none()
    )

    if not venue:
        raise NotFound()

    if FeatureToggle.WIP_ENABLE_CLICKHOUSE_IN_BO.is_active():
        try:
            clickhouse_results = clickhouse_queries.AggregatedTotalRevenueQuery().execute((venue_id,))
            details: dict[str, dict] = {}
            future = {"individual": decimal.Decimal(0.0), "collective": decimal.Decimal(0.0)}
            for aggregated_revenue in clickhouse_results:
                details[str(aggregated_revenue.year)] = {
                    "individual": aggregated_revenue.revenue.individual,
                    "collective": aggregated_revenue.revenue.collective,
                }
                future["individual"] += (
                    aggregated_revenue.expected_revenue.individual - aggregated_revenue.revenue.individual
                )
                future["collective"] += (
                    aggregated_revenue.expected_revenue.collective - aggregated_revenue.revenue.collective
                )
            if sum(future.values()) > 0:
                details["En cours"] = future
        except ApiErrors as api_error:
            mark_transaction_as_invalid()
            return render_template(
                "components/revenue_details.html",
                information=Markup(
                    "Une erreur s'est produite lors de la lecture des données sur Clickhouse : {error}"
                ).format(error=api_error.errors["clickhouse"]),
                target=venue,
            )
    else:
        details = offerers_repository.get_revenues_per_year(venueId=venue_id)

    return render_template(
        "components/revenue_details.html",
        details=details,
        target=venue,
    )


def _fetch_venue_provider(venue_id: int, provider_id: int) -> providers_models.VenueProvider:
    venue_provider = (
        db.session.query(providers_models.VenueProvider)
        .filter(
            providers_models.VenueProvider.providerId == provider_id,
            providers_models.VenueProvider.venueId == venue_id,
        )
        .options(
            sa_orm.joinedload(providers_models.VenueProvider.venue).load_only(offerers_models.Venue.id),
            sa_orm.joinedload(providers_models.VenueProvider.provider).load_only(providers_models.Provider.localClass),
        )
        .one_or_none()
    )

    if venue_provider is None:
        raise NotFound()

    return venue_provider


@venue_blueprint.route("/<int:venue_id>/provider/<int:provider_id>/active", methods=["POST"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def toggle_venue_provider_is_active(venue_id: int, provider_id: int) -> utils.BackofficeResponse:
    venue_provider = _fetch_venue_provider(venue_id, provider_id)

    set_active = not venue_provider.isActive
    providers_api.activate_or_deactivate_venue_provider(
        venue_provider, set_active, author=current_user, send_email=False
    )
    db.session.flush()

    flash(
        Markup("La synchronisation du partenaire culturel avec le provider a été {verb}.").format(
            verb="réactivée" if set_active else "mise en pause"
        ),
        "info",
    )

    return redirect(url_for("backoffice_web.venue.get", venue_id=venue_id), code=303)


@venue_blueprint.route("/<int:venue_id>/provider/<int:provider_id>/delete", methods=["POST"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def delete_venue_provider(venue_id: int, provider_id: int) -> utils.BackofficeResponse:
    venue_provider = _fetch_venue_provider(venue_id, provider_id)

    if venue_provider.isFromAllocineProvider:
        flash("Impossible de supprimer le lien entre le partenaire culturel et Allociné.", "warning")
        mark_transaction_as_invalid()
        return redirect(url_for("backoffice_web.venue.get", venue_id=venue_id), code=303)

    providers_api.delete_venue_provider(venue_provider, author=current_user, send_email=False)
    flash("Le lien entre le partenaire culturel et le provider a été supprimé.", "info")

    return redirect(url_for("backoffice_web.venue.get", venue_id=venue_id), code=303)


def get_venue_with_history(venue_id: int) -> offerers_models.Venue:
    history_filter = history_models.ActionHistory.venueId == venue_id
    if not utils.has_current_user_permission(perm_models.Permissions.PRO_FRAUD_ACTIONS):
        history_filter = sa.and_(
            history_filter, history_models.ActionHistory.actionType != history_models.ActionType.FRAUD_INFO_MODIFIED
        )

    venue = (
        db.session.query(offerers_models.Venue)
        .filter(offerers_models.Venue.id == venue_id)
        .outerjoin(history_models.ActionHistory, history_filter)
        .options(
            sa_orm.contains_eager(offerers_models.Venue.action_history).joinedload(history_models.ActionHistory.user),
            sa_orm.contains_eager(offerers_models.Venue.action_history).joinedload(
                history_models.ActionHistory.authorUser
            ),
        )
        .one_or_none()
    )

    if not venue:
        raise NotFound()

    return venue


@venue_blueprint.route("/<int:venue_id>/history", methods=["GET"])
def get_history(venue_id: int) -> utils.BackofficeResponse:
    venue = get_venue_with_history(venue_id)
    actions = sorted(venue.action_history, key=lambda action: action.actionDate, reverse=True)

    form = forms.CommentForm()
    dst = url_for("backoffice_web.venue.comment_venue", venue_id=venue.id)

    return render_template(
        "venue/get/history.html",
        venue=venue,
        actions=actions,
        dst=dst,
        form=form,
    )


@venue_blueprint.route("/<int:venue_id>/protected-info", methods=["GET"])
@utils.permission_required(perm_models.Permissions.READ_PRO_ENTREPRISE_INFO)
def get_entreprise_info(venue_id: int) -> utils.BackofficeResponse:
    venue = db.session.query(offerers_models.Venue).get_or_404(venue_id)

    if not venue.siret:
        raise NotFound()

    if not is_valid_siret(venue.siret):
        mark_transaction_as_invalid()
        return render_template("venue/get/entreprise_info.html", is_invalid_siret=True, venue=venue)

    siret_info = None
    siret_error = None

    try:
        siret_info = entreprise_api.get_siret(venue.siret, raise_if_non_public=False)
    except entreprise_exceptions.UnknownEntityException:
        mark_transaction_as_invalid()
        siret_error = "Ce SIRET est inconnu dans la base de données Sirene, y compris dans les non-diffusibles"
    except entreprise_exceptions.SireneException:
        mark_transaction_as_invalid()
        siret_error = "Une erreur s'est produite lors de l'appel à API Entreprise"

    return render_template("venue/get/entreprise_info.html", siret_info=siret_info, siret_error=siret_error)


@venue_blueprint.route("/<int:venue_id>/collective-dms-applications", methods=["GET"])
def get_collective_dms_applications(venue_id: int) -> utils.BackofficeResponse:
    collective_dms_applications = (
        db.session.query(educational_models.CollectiveDmsApplication)
        .filter(
            educational_models.CollectiveDmsApplication.siret
            == sa.select(offerers_models.Venue.siret).filter(offerers_models.Venue.id == venue_id).scalar_subquery()
        )
        .options(
            sa_orm.load_only(
                educational_models.CollectiveDmsApplication.state,
                educational_models.CollectiveDmsApplication.depositDate,
                educational_models.CollectiveDmsApplication.lastChangeDate,
                educational_models.CollectiveDmsApplication.application,
                educational_models.CollectiveDmsApplication.procedure,
            ),
        )
        .order_by(educational_models.CollectiveDmsApplication.depositDate.desc())
    )

    return render_template(
        "venue/get/collective_dms_applications.html",
        collective_dms_applications=collective_dms_applications,
    )


@venue_blueprint.route("/<int:venue_id>/delete", methods=["POST"])
@utils.permission_required(perm_models.Permissions.DELETE_PRO_ENTITY)
def delete_venue(venue_id: int) -> utils.BackofficeResponse:
    venue = (
        db.session.query(offerers_models.Venue)
        .filter_by(id=venue_id)
        .populate_existing()
        .with_for_update()
        .one_or_none()
    )
    if not venue:
        raise NotFound()

    venue_name = venue.name

    emails = offerers_repository.get_emails_by_venue(venue)

    try:
        offerers_api.delete_venue(venue.id)
    except offerers_exceptions.CannotDeleteVenueWithBookingsException:
        mark_transaction_as_invalid()
        flash("Impossible de supprimer un partenaire culturel pour lequel il existe des réservations", "warning")
        return redirect(url_for("backoffice_web.venue.get", venue_id=venue.id), code=303)
    except offerers_exceptions.CannotDeleteVenueUsedAsPricingPointException:
        mark_transaction_as_invalid()
        flash(
            "Impossible de supprimer un partenaire culturel utilisé comme point de valorisation d'un autre partenaire culturel",
            "warning",
        )
        return redirect(url_for("backoffice_web.venue.get", venue_id=venue.id), code=303)
    except offerers_exceptions.CannotDeleteVenueWithActiveOrFutureCustomReimbursementRule:
        mark_transaction_as_invalid()
        flash(
            Markup(
                'Impossible de supprimer un point de valorisation ayant un <a href="{url}">tarif dérogatoire</a> (passé, actif ou futur)'
            ).format(url=url_for("backoffice_web.reimbursement_rules.list_custom_reimbursement_rules", venue=venue_id)),
            "warning",
        )
        return redirect(url_for("backoffice_web.venue.get", venue_id=venue.id), code=303)

    for email in emails:
        external_attributes_api.update_external_pro(email)

    flash(
        Markup("Le partenaire culturel {venue_name} ({venue_id}) a été supprimé").format(
            venue_name=venue_name, venue_id=venue_id
        ),
        "success",
    )
    return redirect(url_for("backoffice_web.pro.search_pro"), code=303)


@venue_blueprint.route("/<int:venue_id>", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def update_venue(venue_id: int) -> utils.BackofficeResponse:
    venue_row = get_venue(venue_id)
    venue: offerers_models.Venue = venue_row.Venue

    if venue.isVirtual:
        form = forms.EditVirtualVenueForm()
    else:
        form = forms.EditVenueForm(venue)

    if not form.validate():
        mark_transaction_as_invalid()
        msg = Markup(
            """
            <button type="button"
                    class="btn"
                    data-bs-toggle="modal"
                    data-bs-target="#edit-venue-modal">
                Les données envoyées comportent des erreurs. Afficher
            </button>
            """
        ).format()
        flash(msg, "warning")
        return render_venue_details(venue_row, form), 400

    attrs = {
        to_camelcase(field.name): field.data
        for field in form
        if field.name and hasattr(venue, to_camelcase(field.name))
    }

    venue_was_permanent = venue.isPermanent
    new_permanent = attrs.get("isPermanent")
    update_siret = False
    unavailable_sirene = False
    if not venue.isVirtual and venue.siret != form.siret.data:
        new_siret = form.siret.data

        if not _can_edit_siret():
            flash(
                f"Vous ne pouvez pas {'modifier' if venue.siret else 'ajouter'} le SIRET d'un partenaire culturel. Contactez le support pro N2.",
                "warning",
            )
            mark_transaction_as_invalid()
            return render_venue_details(venue_row, form), 400

        if venue.siret:
            if not new_siret:
                flash("Vous ne pouvez pas retirer le SIRET d'un partenaire culturel.", "warning")
                mark_transaction_as_invalid()
                return render_venue_details(venue_row, form), 400
        elif new_siret:
            # Remove comment because of constraint check_has_siret_xor_comment_xor_isVirtual
            attrs["comment"] = None

        if new_siret and offerers_repository.find_venue_by_siret(new_siret):
            flash(
                Markup("Un autre partenaire culturel existe déjà avec le SIRET {siret}").format(siret=new_siret),
                "warning",
            )
            mark_transaction_as_invalid()
            return render_venue_details(venue_row, form), 400

        existing_pricing_point_id = venue.current_pricing_point_id
        if existing_pricing_point_id and venue.id != existing_pricing_point_id:
            flash(
                f"Ce partenaire culturel a déjà un point de valorisation "
                f"(Venue.id={existing_pricing_point_id}). "
                f"Définir un SIRET impliquerait qu'il devienne son propre point de valorisation, "
                f"mais le changement de point de valorisation n'est pas autorisé",
                "warning",
            )
            mark_transaction_as_invalid()
            return render_venue_details(venue_row, form), 400

        try:
            if not sirene.siret_is_active(new_siret):
                flash("Ce SIRET n'est plus actif, on ne peut pas l'attribuer à ce partenaire culturel", "warning")
                mark_transaction_as_invalid()
                return render_venue_details(venue_row, form), 400
        except entreprise_exceptions.SireneException:
            unavailable_sirene = True

        update_siret = True

    if form.phone_number.data or venue.contact:
        contact_data = offerers_schemas.VenueContactModel(
            phone_number=form.phone_number.data,
            # Use existing values, if any, to ensure that no data (website
            # for example) will be erased by mistake
            email=venue.contact.email if venue.contact else None,  # type: ignore[arg-type]
            website=venue.contact.website if venue.contact else None,
            social_medias=venue.contact.social_medias if venue.contact else None,
        )
    else:
        contact_data = None

    location_fields = {"street", "banId", "latitude", "longitude", "postalCode", "city", "inseeCode", "isManualEdition"}
    update_location_attrs = {
        to_camelcase(field.name): field.data
        for field in form
        if field.name and to_camelcase(field.name) in location_fields
    }
    location_modifications = {}
    if venue.offererAddress:
        location_modifications = {
            field: value
            for field, value in update_location_attrs.items()
            if venue.offererAddress.address.field_exists_and_has_changed(field, value)
        }
    criteria = (
        db.session.query(criteria_models.Criterion).filter(criteria_models.Criterion.id.in_(form.tags.data)).all()
    )
    modifications = {field: value for field, value in attrs.items() if venue.field_exists_and_has_changed(field, value)}

    try:
        offerers_api.update_venue(
            venue,
            modifications,
            location_modifications,
            author=current_user,
            contact_data=contact_data,
            criteria=criteria,
            external_accessibility_url=form.acceslibre_url.data if hasattr(form, "acceslibre_url") else "",
            is_manual_edition=((not venue.isVirtual) and form.is_manual_address.data == "on"),
        )
    except sa.exc.IntegrityError as err:
        # mostly errors about address / offerer_address tables
        logger.exception(
            "IntegrityError when updating venue: %s", str(err), extra={"venue_id": venue_id, "exc": str(err)}
        )
        flash(Markup("Une erreur s'est produite : {message}").format(message=str(err)), "warning")
        mark_transaction_as_invalid()
        # Redirect because we can't fetch data in the current request:
        # This Session's transaction has been rolled back due to a previous exception during flush
        return redirect(url_for(".get", venue_id=venue_id))
    except ApiErrors as api_errors:
        for error_key, error_details in api_errors.errors.items():
            for error_detail in error_details:
                flash(
                    Markup("[{error_key}] {error_detail}").format(error_key=error_key, error_detail=error_detail),
                    "warning",
                )
        mark_transaction_as_invalid()
        return redirect(url_for(".get", venue_id=venue_id))

    if not venue_was_permanent and new_permanent and venue.thumbCount == 0:
        transactional_mails.send_permanent_venue_needs_picture(venue)

    if update_siret:
        if unavailable_sirene:
            flash("Ce SIRET n'a pas pu être vérifié, mais la modification a néanmoins été effectuée", "warning")
        if not existing_pricing_point_id:
            offerers_api.link_venue_to_pricing_point(venue, pricing_point_id=venue.id)

    flash("Les informations ont été mises à jour", "success")
    return redirect(url_for("backoffice_web.venue.get", venue_id=venue.id), code=303)


@venue_blueprint.route("/<int:venue_id>/fraud", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def update_for_fraud(venue_id: int) -> utils.BackofficeResponse:
    venue = (
        db.session.query(offerers_models.Venue)
        .filter_by(id=venue_id)
        .options(sa_orm.joinedload(offerers_models.Venue.confidenceRule))
        .one_or_none()
    )
    if not venue:
        raise NotFound()

    form = forms.FraudForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
    elif offerers_api.update_fraud_info(
        venue=venue,
        author_user=current_user,
        confidence_level=(
            offerers_models.OffererConfidenceLevel(form.confidence_level.data) if form.confidence_level.data else None
        ),
        comment=form.comment.data,
    ):
        flash("Les informations ont été mises à jour", "success")

    return redirect(url_for("backoffice_web.venue.get", venue_id=venue.id), code=303)


@venue_blueprint.route("/<int:venue_id>/comment", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def comment_venue(venue_id: int) -> utils.BackofficeResponse:
    venue = (
        db.session.query(offerers_models.Venue)
        .filter_by(id=venue_id)
        .with_for_update(key_share=True, read=True)
        .one_or_none()
    )
    if not venue:
        raise NotFound()

    form = forms.CommentForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        mark_transaction_as_invalid()
    else:
        offerers_api.add_comment_to_venue(venue, current_user, comment=form.comment.data)
        flash("Le commentaire a été enregistré", "success")

    return redirect(url_for("backoffice_web.venue.get", venue_id=venue_id), code=303)


@venue_blueprint.route("/batch-edit-form", methods=["GET", "POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def get_batch_edit_venues_form() -> utils.BackofficeResponse:
    form = forms.BatchEditVenuesForm()
    if form.object_ids.data:
        if not form.validate():
            flash(utils.build_form_error_msg(form), "warning")
            mark_transaction_as_invalid()
            return redirect(request.referrer or url_for(".list_venues"), code=303)

        venues = (
            db.session.query(offerers_models.Venue)
            .filter(offerers_models.Venue.id.in_(form.object_ids_list))
            .options(
                sa_orm.load_only(offerers_models.Venue.id),
                sa_orm.joinedload(offerers_models.Venue.criteria).load_only(
                    criteria_models.Criterion.id, criteria_models.Criterion.name
                ),
            )
            .all()
        )
        criteria = set.intersection(*[set(venue.criteria) for venue in venues])

        if len(criteria) > 0:
            form.criteria.choices = [(criterion.id, criterion.name) for criterion in criteria]

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for(".batch_edit_venues"),
        div_id="batch-edit-venues-modal",
        title="Édition des partenaires culturels",
        button_text="Enregistrer les modifications",
    )


@venue_blueprint.route("/batch-edit", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def batch_edit_venues() -> utils.BackofficeResponse:
    form = forms.BatchEditVenuesForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        mark_transaction_as_invalid()
        return redirect(request.referrer or url_for(".list_venues"), code=303)

    venues = (
        db.session.query(offerers_models.Venue)
        .filter(offerers_models.Venue.id.in_(form.object_ids_list))
        .populate_existing()
        .with_for_update(key_share=True)
        .all()
    )

    updated_criteria_venues = _update_venues_criteria(venues=venues, criteria_ids=form.criteria.data)
    updated_permanent_venues = []
    if form.all_permanent.data:
        updated_permanent_venues = _update_permanent_venues(venues=venues, is_permanent=True)
    elif form.all_not_permanent.data:
        updated_permanent_venues = _update_permanent_venues(venues=venues, is_permanent=False)

    updated_venues = list(set(updated_criteria_venues + updated_permanent_venues))

    db.session.add_all(updated_venues)
    db.session.flush()

    on_commit(
        partial(
            search.async_index_venue_ids,
            [v.id for v in updated_venues],
            reason=search.IndexationReason.VENUE_BATCH_UPDATE,
        )
    )

    flash("Les partenaires culturels ont été modifiés", "success")
    return redirect(request.referrer or url_for(".list_venues"), code=303)


def _update_venues_criteria(
    venues: list[offerers_models.Venue], criteria_ids: list[int]
) -> list[offerers_models.Venue]:
    new_criteria = (
        db.session.query(criteria_models.Criterion).filter(criteria_models.Criterion.id.in_(criteria_ids)).all()
    )

    previous_criteria = set.intersection(*(set(venue.criteria) for venue in venues))
    deleted_criteria = previous_criteria.difference(new_criteria)

    changed_venues = []

    for venue in venues:
        if venue.criteria == new_criteria:
            continue
        if venue.criteria:
            venue.criteria.extend(criterion for criterion in new_criteria if criterion not in venue.criteria)
            for criterion in deleted_criteria:
                venue.criteria.remove(criterion)
        else:
            venue.criteria = new_criteria
        changed_venues.append(venue)

    return changed_venues


def _update_permanent_venues(venues: list[offerers_models.Venue], is_permanent: bool) -> list[offerers_models.Venue]:
    venues_to_update = [venue for venue in venues if venue.isPermanent != is_permanent]

    for venue in venues_to_update:
        add_action(
            history_models.ActionType.INFO_MODIFIED,
            author=current_user,
            venue=venue,
            modified_info={"isPermanent": {"old_info": venue.isPermanent, "new_info": is_permanent}},
        )
        venue.isPermanent = is_permanent
        if is_permanent and venue.thumbCount == 0:
            transactional_mails.send_permanent_venue_needs_picture(venue)

    return venues_to_update


def _load_venue_for_removing_pricing_point(venue_id: int) -> offerers_models.Venue:
    venue = (
        db.session.query(offerers_models.Venue)
        .filter(offerers_models.Venue.id == venue_id)
        .options(
            sa_orm.load_only(offerers_models.Venue.name, offerers_models.Venue.publicName, offerers_models.Venue.siret),
            sa_orm.joinedload(offerers_models.Venue.pricing_point_links)
            .joinedload(offerers_models.VenuePricingPointLink.pricingPoint)
            .load_only(offerers_models.Venue.name, offerers_models.Venue.publicName, offerers_models.Venue.siret),
        )
        .one_or_none()
    )

    if not venue:
        raise NotFound()

    return venue


def _render_remove_pricing_point_content(
    venue: offerers_models.Venue, form: forms.RemovePricingPointForm | None = None, error: str | None = None
) -> utils.BackofficeResponse:
    current_pricing_point = venue.current_pricing_point

    kwargs = {}
    if form:
        kwargs.update(
            {
                "form": form,
                "dst": url_for("backoffice_web.venue.remove_pricing_point", venue_id=venue.id),
                "button_text": "Confirmer",
            }
        )
    additional_data = {}
    additional_data["Partenaire culturel"] = venue.name
    additional_data.update(
        {
            "Venue ID": str(venue.id),
            "SIRET": venue.siret or "Pas de SIRET",
            "CA de l'année": filters.format_amount(siret_api.get_yearly_revenue(venue.id)),
            "Point de valorisation": current_pricing_point.name if current_pricing_point else "Aucun",
            "SIRET de valorisation": (
                current_pricing_point.siret if current_pricing_point and current_pricing_point.siret else "Aucun"
            ),
        }
    )
    return (
        render_template(
            "components/turbo/modal_form.html",
            div_id="remove-venue-pricing-point",  # must be consistent with parameter passed to build_lazy_modal
            title="Détacher le point de valorisation",
            additional_data=additional_data.items(),
            alert=error,
            **kwargs,
        ),
        400 if error or (form and form.errors) else 200,
    )


@venue_blueprint.route("/<int:venue_id>/remove-pricing-point", methods=["GET"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def get_remove_pricing_point_form(venue_id: int) -> utils.BackofficeResponse:
    venue = _load_venue_for_removing_pricing_point(venue_id)

    try:
        siret_api.check_can_remove_pricing_point(venue)
    except siret_api.CheckError as exc:
        mark_transaction_as_invalid()
        return _render_remove_pricing_point_content(venue, error=str(exc))

    form = forms.RemovePricingPointForm()
    return _render_remove_pricing_point_content(venue, form=form)


@venue_blueprint.route("/<int:venue_id>/remove-pricing-point", methods=["POST"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def remove_pricing_point(venue_id: int) -> utils.BackofficeResponse:
    venue = _load_venue_for_removing_pricing_point(venue_id)

    form = forms.RemovePricingPointForm()
    if not form.validate():
        mark_transaction_as_invalid()
        return _render_remove_pricing_point_content(venue, form=form)

    try:
        siret_api.remove_pricing_point_link(
            venue,
            form.comment.data,
            override_revenue_check=bool(form.override_revenue_check.data),
            author_user_id=current_user.id,
        )
    except siret_api.CheckError as exc:
        mark_transaction_as_invalid()
        return _render_remove_pricing_point_content(venue, form=form, error=str(exc))

    return redirect(url_for("backoffice_web.venue.get", venue_id=venue_id), code=303)


@venue_blueprint.route("/<int:venue_id>/set-pricing-point", methods=["GET"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def get_set_pricing_point_form(venue_id: int) -> utils.BackofficeResponse:
    aliased_venue = sa_orm.aliased(offerers_models.Venue)
    venue = (
        db.session.query(offerers_models.Venue)
        .filter(offerers_models.Venue.id == venue_id)
        .join(offerers_models.Venue.managingOfferer)
        .outerjoin(
            aliased_venue,
            sa.and_(
                aliased_venue.managingOffererId == offerers_models.Offerer.id,
                aliased_venue.siret.is_not(None),
            ),
        )
        .options(
            sa_orm.contains_eager(offerers_models.Venue.managingOfferer)
            .contains_eager(offerers_models.Offerer.managedVenues.of_type(aliased_venue))
            .load_only(
                aliased_venue.id,
                aliased_venue.siret,
                aliased_venue.name,
            )
        )
        .one_or_none()
    )

    if not venue:
        raise NotFound()

    form = forms.PricingPointForm(venue=venue)

    return render_template(
        "components/turbo/modal_form.html",
        div_id="set-venue-pricing-point",  # must be consistent with parameter passed to build_lazy_modal
        title="Attribuer un point de valorisation",
        form=form,
        dst=url_for("backoffice_web.venue.set_pricing_point", venue_id=venue.id),
        button_text="Confirmer",
    )


@venue_blueprint.route("/<int:venue_id>/set-pricing-point", methods=["POST"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def set_pricing_point(venue_id: int) -> utils.BackofficeResponse:
    aliased_venue = sa_orm.aliased(offerers_models.Venue)
    venue = (
        db.session.query(offerers_models.Venue)
        .filter(offerers_models.Venue.id == venue_id)
        .join(offerers_models.Venue.managingOfferer)
        .outerjoin(
            aliased_venue,
            sa.and_(
                aliased_venue.managingOffererId == offerers_models.Offerer.id,
                aliased_venue.siret.is_not(None),
            ),
        )
        .options(
            sa_orm.contains_eager(offerers_models.Venue.managingOfferer)
            .contains_eager(offerers_models.Offerer.managedVenues.of_type(aliased_venue))
            .load_only(
                aliased_venue.id,
                aliased_venue.siret,
                aliased_venue.name,
            )
        )
        .one_or_none()
    )

    if not venue:
        raise NotFound()

    form = forms.PricingPointForm(venue=venue)
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        mark_transaction_as_invalid()
        return redirect(url_for("backoffice_web.venue.get", venue_id=venue_id), code=303)
    try:
        offerers_api.link_venue_to_pricing_point(venue, form.new_pricing_point.data)
        flash("Ce partenaire culturel a été lié à un point de valorisation", "info")
    except ApiErrors as exc:
        mark_transaction_as_invalid()
        if not exc.errors or "pricingPointId" not in exc.errors:
            flash(escape(str(exc.errors)) if exc.errors else "Erreur inconue", "warning")
        else:
            flash(escape(exc.errors["pricingPointId"][0]), "warning")
    except offerers_exceptions.CannotLinkVenueToPricingPoint:
        mark_transaction_as_invalid()
        flash("Ce partenaire culturel est déja lié à un point de valorisation", "warning")
    return redirect(url_for("backoffice_web.venue.get", venue_id=venue_id), code=303)


REMOVE_SIRET_TITLE = "Supprimer le SIRET d'un partenaire culturel"


def _load_venue_for_removing_siret(venue_id: int) -> offerers_models.Venue:
    venue = (
        db.session.query(offerers_models.Venue)
        .filter(offerers_models.Venue.id == venue_id)
        .options(
            sa_orm.load_only(offerers_models.Venue.name, offerers_models.Venue.publicName, offerers_models.Venue.siret),
            sa_orm.joinedload(offerers_models.Venue.managingOfferer)
            .load_only(offerers_models.Offerer.id, offerers_models.Offerer.name)
            .joinedload(offerers_models.Offerer.managedVenues)
            .load_only()
            .load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.siret,
            ),
        )
        .one_or_none()
    )

    if not venue:
        raise NotFound()

    return venue


def _render_remove_siret_content(
    venue: offerers_models.Venue,
    form: forms.RemoveSiretForm | None = None,
    error: str | None = None,
    info: str | None = None,
) -> utils.BackofficeResponse:
    kwargs = {}
    if form:
        kwargs.update(
            {
                "form": form,
                "dst": url_for("backoffice_web.venue.remove_siret", venue_id=venue.id),
                "button_text": "Confirmer",
            }
        )
    additional_data = {
        "Entité juridique": venue.managingOfferer.name,
        "Offerer ID": venue.managingOfferer.id,
    }
    additional_data["Partenaire culturel"] = venue.name
    additional_data.update(
        {
            "Venue ID": venue.id,
            "SIRET": venue.siret or "Pas de SIRET",
            "CA de l'année": filters.format_amount(siret_api.get_yearly_revenue(venue.id)),
        }
    )

    active_custom_reimbursement_rule_exists = db.session.query(
        db.session.query(finance_models.CustomReimbursementRule)
        .filter(
            finance_models.CustomReimbursementRule.venueId == venue.id,
            sa.or_(
                sa.func.upper(finance_models.CustomReimbursementRule.timespan).is_(None),
                sa.func.upper(finance_models.CustomReimbursementRule.timespan) >= datetime.utcnow(),
            ),
        )
        .exists()
    ).scalar()
    if active_custom_reimbursement_rule_exists:
        info = "Ce partenaire culturel est associé à au moins un tarif dérogatoire actif ou futur. Confirmer l'action mettra automatiquement fin à ce tarif dérogatoire."

    return (
        render_template(
            "components/turbo/modal_form.html",
            div_id="remove-venue-siret",  # must be consistent with parameter passed to build_lazy_modal
            title=REMOVE_SIRET_TITLE,
            additional_data=additional_data.items(),
            alert=error,
            info=info,
            **kwargs,
        ),
        400 if error or (form and form.errors) else 200,
    )


@venue_blueprint.route("/<int:venue_id>/remove-siret", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MOVE_SIRET)
def get_remove_siret_form(venue_id: int) -> utils.BackofficeResponse:
    venue = _load_venue_for_removing_siret(venue_id)

    try:
        siret_api.check_can_remove_siret(
            venue, "comment", override_revenue_check=True, check_offerer_has_other_siret=True
        )
    except siret_api.CheckError as exc:
        mark_transaction_as_invalid()
        return _render_remove_siret_content(venue, error=str(exc))

    form = forms.RemoveSiretForm(venue)
    return _render_remove_siret_content(venue, form=form)


@venue_blueprint.route("/<int:venue_id>/remove-siret", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MOVE_SIRET)
def remove_siret(venue_id: int) -> utils.BackofficeResponse:
    venue = _load_venue_for_removing_siret(venue_id)

    form = forms.RemoveSiretForm(venue)
    if not form.validate():
        mark_transaction_as_invalid()
        return _render_remove_siret_content(venue, form=form)

    try:
        siret_api.remove_siret(
            venue,
            form.comment.data,
            override_revenue_check=bool(form.override_revenue_check.data),
            new_pricing_point_id=form.new_pricing_point.data,
            author_user_id=current_user.id,
        )
    except siret_api.CheckError as exc:
        mark_transaction_as_invalid()
        return _render_remove_siret_content(venue, form=form, error=str(exc))

    return redirect(url_for("backoffice_web.venue.get", venue_id=venue_id), code=303)
