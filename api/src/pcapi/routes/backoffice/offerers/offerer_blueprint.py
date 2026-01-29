import datetime
import typing

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
from werkzeug.exceptions import NotFound

from pcapi.connectors.clickhouse import queries as clickhouse_queries
from pcapi.connectors.dms.models import GraphQLApplicationStates
from pcapi.connectors.entreprise import api as entreprise_api
from pcapi.connectors.entreprise import exceptions as entreprise_exceptions
from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import models as educational_models
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.finance import models as finance_models
from pcapi.core.geography import models as geography_models
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers import models as providers_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.utils import get_or_404
from pcapi.routes.backoffice.bookings import forms as bookings_forms
from pcapi.routes.backoffice.filters import pluralize
from pcapi.routes.backoffice.pro import forms as pro_forms
from pcapi.routes.backoffice.pro.utils import get_connect_as
from pcapi.routes.serialization import address_serialize
from pcapi.routes.serialization import venues_serialize
from pcapi.utils import date as date_utils
from pcapi.utils import regions as regions_utils
from pcapi.utils import siren as siren_utils
from pcapi.utils import urls
from pcapi.utils.transaction_manager import mark_transaction_as_invalid

from .. import utils
from ..forms import empty as empty_forms
from . import forms as offerer_forms


offerer_blueprint = utils.child_backoffice_blueprint(
    "offerer",
    __name__,
    url_prefix="/pro/offerer/<int:offerer_id>",
    permission=perm_models.Permissions.READ_PRO_ENTITY,
)


def _self_redirect(
    offerer_id: int, active_tab: str | None = None, anchor: str | None = None
) -> utils.BackofficeResponse:
    url = url_for("backoffice_web.offerer.get", offerer_id=offerer_id, active_tab=active_tab)
    if anchor:
        url += f"#{anchor}"
    return redirect(url, code=303)


def _load_offerer_data(offerer_id: int) -> sa.engine.Row:
    bank_information_query = sa.select(sa.func.jsonb_object_agg(sa.text("status"), sa.text("number"))).select_from(
        sa.select(
            sa.case((offerers_models.VenueBankAccountLink.id.is_(None), "ko"), else_="ok").label("status"),
            sa.func.count(offerers_models.Venue.id).label("number"),
        )
        .select_from(offerers_models.Venue)
        .outerjoin(
            offerers_models.VenueBankAccountLink,
            sa.and_(
                offerers_models.VenueBankAccountLink.venueId == offerers_models.Venue.id,
                offerers_models.VenueBankAccountLink.timespan.contains(date_utils.get_naive_utc_now()),
            ),
        )
        .filter(
            offerers_models.Venue.managingOffererId == offerer_id,
            offerers_models.Venue.isSoftDeleted.is_(False),
        )
        .group_by(sa.text("status"))
        .subquery()
    )

    adage_query = (
        sa.select(
            sa.func.concat(
                sa.func.coalesce(sa.func.sum(sa.case((offerers_models.Venue.adageId.is_not(None), 1), else_=0)), 0),
                "/",
                sa.func.count(offerers_models.Venue.id),
            )
        )
        .select_from(offerers_models.Venue)
        .filter(
            offerers_models.Venue.managingOffererId == offerers_models.Offerer.id,
            offerers_models.Venue.isSoftDeleted.is_(False),
            offerers_models.Venue.isVirtual.is_(False),
        )
        .correlate(offerers_models.Offerer)
        .scalar_subquery()
    )

    creator_user_offerer_id_query = (
        db.session.query(offerers_models.UserOfferer.id)
        .filter(offerers_models.UserOfferer.offererId == offerers_models.Offerer.id)
        .order_by(offerers_models.UserOfferer.id.asc())
        .limit(1)
        .correlate(offerers_models.Offerer)
        .scalar_subquery()
    )

    has_non_virtual_venues_query = (
        sa.exists()
        .where(offerers_models.Venue.managingOffererId == offerers_models.Offerer.id)
        .where(sa.not_(offerers_models.Venue.isVirtual))
        .where(offerers_models.Venue.isSoftDeleted.is_(False))
    )

    has_offerer_address_query = (
        sa.select(1)
        .select_from(offerers_models.OffererAddress)
        .where(offerers_models.OffererAddress.offererId == offerers_models.Offerer.id)
        .correlate(offerers_models.Offerer)
        .exists()
    )
    if utils.has_current_user_permission(perm_models.Permissions.READ_FRAUDULENT_BOOKING_INFO):
        has_fraudulent_booking_query: sa.sql.selectable.Exists | sa.sql.elements.Null = (
            sa.select(1)
            .select_from(bookings_models.Booking)
            .join(bookings_models.FraudulentBookingTag)
            .where(bookings_models.Booking.offererId == offerers_models.Offerer.id)
            .correlate(offerers_models.Offerer)
            .exists()
        )
    else:
        has_fraudulent_booking_query = sa.null()

    offerer_query = (
        db.session.query(
            offerers_models.Offerer,
            bank_information_query.scalar_subquery().label("bank_information"),
            has_non_virtual_venues_query.label("has_non_virtual_venues"),
            has_offerer_address_query.label("has_offerer_address"),
            has_fraudulent_booking_query.label("has_fraudulent_booking"),
            adage_query.label("adage_information"),
            users_models.User.phoneNumber.label("creator_phone_number"),
        )
        .filter(offerers_models.Offerer.id == offerer_id)
        .outerjoin(offerers_models.UserOfferer, offerers_models.UserOfferer.id == creator_user_offerer_id_query)
        .outerjoin(offerers_models.UserOfferer.user)
        .options(
            sa_orm.with_expression(
                offerers_models.Offerer.department_codes, offerers_models.Offerer.department_codes_expression()
            ),
            sa_orm.with_expression(offerers_models.Offerer.cities, offerers_models.Offerer.cities_expression()),
            sa_orm.joinedload(offerers_models.Offerer.individualSubscription).load_only(
                offerers_models.IndividualOffererSubscription.id
            ),
            sa_orm.joinedload(offerers_models.Offerer.confidenceRule).load_only(
                offerers_models.OffererConfidenceRule.confidenceLevel
            ),
        )
    )

    row = offerer_query.one_or_none()
    if not row:
        raise NotFound()

    return row


def _render_offerer_details(offerer_id: int, edit_offerer_form: offerer_forms.EditOffererForm | None = None) -> str:
    row = _load_offerer_data(offerer_id)
    offerer: offerers_models.Offerer = row.Offerer

    if not row:
        raise NotFound()

    bank_information_status = row.bank_information or {}
    if not edit_offerer_form:
        edit_offerer_form = offerer_forms.EditOffererForm(
            name=offerer.name,
            tags=offerer.tags,
        )

    fraud_form = (
        offerer_forms.FraudForm(confidence_level=offerer.confidenceLevel.value if offerer.confidenceLevel else None)
        if utils.has_current_user_permission(perm_models.Permissions.PRO_FRAUD_ACTIONS)
        else None
    )

    search_form = pro_forms.CompactProSearchForm(
        q=request.args.get("q"),
        pro_type=pro_forms.TypeOptions.OFFERER.name,
        departments=(
            request.args.getlist("departments")
            if request.args.get("q") or request.args.getlist("departments")
            else current_user.backoffice_profile.preferences.get("departments", [])
        ),
    )

    show_subscription_tab = (
        offerer.individualSubscription
        and (
            utils.has_current_user_permission(perm_models.Permissions.VALIDATE_OFFERER)
            or utils.has_current_user_permission(perm_models.Permissions.READ_PRO_AE_INFO)
        )
    ) or (
        not offerer.isValidated
        and "auto-entrepreneur" in {tag.name for tag in offerer.tags}
        and utils.has_current_user_permission(perm_models.Permissions.VALIDATE_OFFERER)
    )

    connect_as_offerer = get_connect_as(
        object_type="offerer",
        object_id=offerer_id,
        pc_pro_path=urls.build_pc_pro_offerer_link(offerer),
    )

    connect_as_offer = get_connect_as(
        object_type="offerer",
        object_id=offerer_id,
        pc_pro_path=urls.build_pc_pro_offers_for_offerer_path(offerer),
    )
    connect_as_collective_offer = get_connect_as(
        object_type="offerer",
        object_id=offerer_id,
        pc_pro_path=urls.build_pc_pro_collective_offers_for_offerer_path(offerer),
    )

    return render_template(
        "offerer/get.html",
        search_form=search_form,
        search_dst=url_for("backoffice_web.pro.search_pro"),
        offerer=offerer,
        regions={regions_utils.get_region_name_from_department_code(code) for code in offerer.department_codes or []},
        creator_phone_number=row.creator_phone_number,
        adage_information=row.adage_information,
        bank_information_status=bank_information_status,
        edit_offerer_form=edit_offerer_form,
        suspension_form=offerer_forms.SuspendOffererForm(),
        delete_offerer_form=empty_forms.EmptyForm(),
        fraud_form=fraud_form,
        show_subscription_tab=show_subscription_tab,
        has_offerer_address=row.has_offerer_address,
        has_fraudulent_booking=row.has_fraudulent_booking,
        active_tab=request.args.get("active_tab", "history"),
        connect_as_offerer=connect_as_offerer,
        connect_as_offer=connect_as_offer,
        connect_as_collective_offer=connect_as_collective_offer,
        zendesk_sell_synchronisation_form=(
            empty_forms.EmptyForm()
            if row.has_non_virtual_venues
            and utils.has_current_user_permission(perm_models.Permissions.MANAGE_PRO_ENTITY)
            else None
        ),
    )


@offerer_blueprint.route("", methods=["GET"])
def get(offerer_id: int) -> utils.BackofficeResponse:
    if request.args.get("q") and request.args.get("search_rank"):
        utils.log_backoffice_tracking_data(
            event_name="ConsultCard",
            extra_data={
                "searchType": "ProSearch",
                "searchProType": pro_forms.TypeOptions.OFFERER.name,
                "searchQuery": request.args.get("q"),
                "searchDepartments": ",".join(request.args.get("departments", [])),
                "searchRank": request.args.get("search_rank"),
                "searchNbResults": request.args.get("total_items"),
            },
        )

    return _render_offerer_details(offerer_id)


def _get_stat_urls(offerer: offerers_models.Offerer) -> dict[str, str]:
    urls = {}
    search_params = {
        "search-0-search_field": "OFFERER",
        "search-0-operator": "IN",
        "search-0-offerer": offerer.id,
    }
    if utils.has_current_user_permission(perm_models.Permissions.READ_OFFERS):
        urls["list_offers"] = url_for("backoffice_web.offer.list_offers", **search_params)  # type: ignore [arg-type]
        urls["list_collective_offers"] = url_for(
            "backoffice_web.collective_offer.list_collective_offers",
            **search_params,  # type: ignore [arg-type]
        )
        urls["list_collective_offer_templates"] = url_for(
            "backoffice_web.collective_offer_template.list_collective_offer_templates", offerer=offerer.id
        )
    if utils.has_current_user_permission(perm_models.Permissions.READ_BOOKINGS):
        urls["list_bookings"] = url_for(
            "backoffice_web.individual_bookings.list_individual_bookings", offerer=offerer.id
        )
        urls["list_collective_bookins"] = url_for(
            "backoffice_web.collective_bookings.list_collective_bookings", offerer=offerer.id
        )

    urls["revenue_details"] = url_for("backoffice_web.offerer.get_revenue_details", offerer_id=offerer.id)
    return urls


@offerer_blueprint.route("/stats", methods=["GET"])
def get_stats(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        db.session.query(offerers_models.Offerer)
        .filter_by(id=offerer_id)
        .options(sa_orm.joinedload(offerers_models.Offerer.managedVenues).load_only(offerers_models.Venue.id))
        .one_or_none()
    )
    if not offerer:
        raise NotFound()

    stats = offerers_api.get_venues_stats(venue_ids=(venue.id for venue in offerer.managedVenues))
    return render_template(
        "components/stats/venue_offerer_stats.html",
        urls=_get_stat_urls(offerer),
        stats=stats,
        object=offerer,
    )


@offerer_blueprint.route("/revenue-details", methods=["GET"])
def get_revenue_details(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        db.session.query(offerers_models.Offerer)
        .filter_by(id=offerer_id)
        .options(sa_orm.joinedload(offerers_models.Offerer.managedVenues).load_only(offerers_models.Venue.id))
        .one_or_none()
    )
    if not offerer:
        raise NotFound()

    details: dict[str, dict] = {}
    if offerer.managedVenues:
        try:
            clickhouse_results = clickhouse_queries.AggregatedTotalRevenueQuery().execute(
                {"venue_ids": tuple(venue.id for venue in offerer.managedVenues)}
            )
            future = {"individual": 0.0, "collective": 0.0}
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
            return render_template(
                "components/revenue_details.html",
                information=Markup(
                    "Une erreur s'est produite lors de la lecture des données sur Clickhouse : {error}"
                ).format(error=api_error.errors["clickhouse"]),
                target=offerer,
            )

    return render_template(
        "components/revenue_details.html",
        details=details,
        target=offerer,
    )


@offerer_blueprint.route("/suspend", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def suspend_offerer(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        db.session.query(offerers_models.Offerer)
        .filter_by(id=offerer_id)
        .populate_existing()
        .with_for_update(key_share=True)
        .one_or_none()
    )
    if not offerer:
        raise NotFound()

    form = offerer_forms.SuspendOffererForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
    else:
        try:
            offerers_api.suspend_offerer(offerer, current_user, form.comment.data)
        except offerers_exceptions.CannotSuspendOffererWithBookingsException:
            mark_transaction_as_invalid()
            flash("Impossible de suspendre une entité juridique pour laquelle il existe des réservations", "warning")
        else:
            flash(
                Markup("L'entité juridique <b>{offerer_name}</b> ({offerer_id}) a été suspendue").format(
                    offerer_name=offerer.name, offerer_id=offerer_id
                ),
                "success",
            )

    return _self_redirect(offerer.id)


@offerer_blueprint.route("/unsuspend", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def unsuspend_offerer(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        db.session.query(offerers_models.Offerer)
        .filter_by(id=offerer_id)
        .populate_existing()
        .with_for_update(key_share=True)
        .one_or_none()
    )
    if not offerer:
        raise NotFound()

    form = offerer_forms.SuspendOffererForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
    else:
        offerers_api.unsuspend_offerer(offerer, current_user, form.comment.data)
        flash(
            Markup("L'entité juridique <b>{offerer_name}</b> ({offerer_id}) a été réactivée").format(
                offerer_name=offerer.name, offerer_id=offerer_id
            ),
            "success",
        )

    return _self_redirect(offerer.id)


@offerer_blueprint.route("/delete", methods=["POST"])
@utils.permission_required(perm_models.Permissions.DELETE_PRO_ENTITY)
def delete_offerer(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        db.session.query(offerers_models.Offerer)
        .filter_by(id=offerer_id)
        .populate_existing()
        .with_for_update()
        .one_or_none()
    )
    if not offerer:
        raise NotFound()

    offerer_name = offerer.name

    # Get users to update before association info is deleted
    # joined user is no longer available after delete_model()
    emails = offerers_repository.get_emails_by_offerer(offerer)

    try:
        offerers_api.delete_offerer(offerer.id)
    except offerers_exceptions.CannotDeleteOffererWithBookingsException:
        mark_transaction_as_invalid()
        flash("Impossible de supprimer une entité juridique pour laquelle il existe des réservations", "warning")
        return _self_redirect(offerer.id)
    except offerers_exceptions.CannotDeleteOffererLinkedToProvider:
        mark_transaction_as_invalid()
        flash("Impossible de supprimer une entité juridique liée à un provider", "warning")
        return _self_redirect(offerer.id)
    except offerers_exceptions.CannotDeleteOffererWithActiveOrFutureCustomReimbursementRule:
        mark_transaction_as_invalid()
        flash(
            Markup(
                'Impossible de supprimer une entité juridique ayant un <a href="{url}">tarif dérogatoire</a> (passé, actif ou futur)'
            ).format(
                url=url_for("backoffice_web.reimbursement_rules.list_custom_reimbursement_rules", offerer=offerer_id)
            ),
            "warning",
        )
        return _self_redirect(offerer.id)

    for email in emails:
        external_attributes_api.update_external_pro(email)

    flash(
        Markup("L'entité juridique <b>{offerer_name}</b> ({offerer_id}) a été supprimée").format(
            offerer_name=offerer_name, offerer_id=offerer_id
        ),
        "success",
    )
    return redirect(url_for("backoffice_web.pro.search_pro"), code=303)


@offerer_blueprint.route("", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def update_offerer(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        db.session.query(offerers_models.Offerer)
        .filter_by(id=offerer_id)
        .populate_existing()
        .with_for_update(key_share=True)
        .one_or_none()
    )
    if not offerer:
        raise NotFound()

    form = offerer_forms.EditOffererForm()
    if not form.validate():
        mark_transaction_as_invalid()
        msg = Markup(
            """
            <button type="button"
                    class="btn"
                    data-bs-toggle="modal"
                    data-bs-target="#edit-offerer-modal">
                Les données envoyées comportent des erreurs. Afficher
            </button>
            """
        ).format()
        flash(msg, "warning")
        return _render_offerer_details(offerer_id, edit_offerer_form=form), 400

    offerers_api.update_offerer(
        offerer,
        current_user,
        name=form.name.data,
        tags=form.tags.data,
    )

    flash("Les informations ont été mises à jour", "success")
    return _self_redirect(offerer.id)


@offerer_blueprint.route("/fraud", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def update_for_fraud(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        db.session.query(offerers_models.Offerer)
        .filter_by(id=offerer_id)
        .options(sa_orm.joinedload(offerers_models.Offerer.confidenceRule))
        .one_or_none()
    )
    if not offerer:
        raise NotFound()

    form = offerer_forms.FraudForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
    elif offerers_api.update_fraud_info(
        offerer=offerer,
        author_user=current_user,
        confidence_level=(
            offerers_models.OffererConfidenceLevel(form.confidence_level.data) if form.confidence_level.data else None
        ),
        comment=form.comment.data,
    ):
        db.session.flush()
        flash("Les informations ont été mises à jour", "success")

    return _self_redirect(offerer.id)


@offerer_blueprint.route("/history", methods=["GET"])
def get_history(offerer_id: int) -> utils.BackofficeResponse:
    # this should not be necessary but in case there is a huge amount
    # of actions, it is safer to set a limit
    max_actions_count = 50

    filters = [history_models.ActionHistory.offererId == offerer_id]
    if not utils.has_current_user_permission(perm_models.Permissions.PRO_FRAUD_ACTIONS):
        filters.append(
            history_models.ActionHistory.actionType != history_models.ActionType.FRAUD_INFO_MODIFIED,
        )

    actions_history = (
        db.session.query(history_models.ActionHistory)
        .filter(*filters)
        .order_by(history_models.ActionHistory.actionDate.desc())
        .limit(max_actions_count)
        .options(
            sa_orm.joinedload(history_models.ActionHistory.user).load_only(
                users_models.User.id, users_models.User.firstName, users_models.User.lastName
            ),
            sa_orm.joinedload(history_models.ActionHistory.authorUser).load_only(
                users_models.User.id, users_models.User.firstName, users_models.User.lastName
            ),
            # joinedload includes soft-deleted venues
            sa_orm.joinedload(history_models.ActionHistory.venue).load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.isSoftDeleted,
                offerers_models.Venue.publicName,
                offerers_models.Venue.name,
            ),
        )
        .all()
    )

    return render_template(
        "offerer/get/details/history.html",
        actions=actions_history,
        form=offerer_forms.CommentForm(),
        dst=url_for("backoffice_web.offerer.comment_offerer", offerer_id=offerer_id),
    )


@offerer_blueprint.route("/users", methods=["GET"])
def get_pro_users(offerer_id: int) -> utils.BackofficeResponse:
    # All ids which appear in either offerer history or attached users
    # Double join takes 30 seconds on staging, union takes 0.03 s.
    user_ids_subquery = (
        db.session.query(offerers_models.UserOfferer.userId)
        .filter(offerers_models.UserOfferer.offererId == offerer_id)
        .union(
            db.session.query(history_models.ActionHistory.userId).filter(
                history_models.ActionHistory.offererId == offerer_id, history_models.ActionHistory.userId.is_not(None)
            )
        )
        .distinct()
    )

    options = sa_orm.joinedload(offerers_models.OffererInvitation.user).load_only(
        users_models.User.id,
        users_models.User.firstName,
        users_models.User.lastName,
        users_models.User.email,
        users_models.User.isActive,
        users_models.User.roles,
    )

    rows = (
        db.session.query(
            users_models.User.id,
            users_models.User.firstName,
            users_models.User.lastName,
            users_models.User.full_name,
            users_models.User.email,
            users_models.User.isActive,
            users_models.User.roles,
            offerers_models.UserOfferer,
            offerers_models.OffererInvitation,
        )
        .select_from(users_models.User)
        .outerjoin(
            offerers_models.UserOfferer,
            sa.and_(
                offerers_models.UserOfferer.userId == users_models.User.id,
                offerers_models.UserOfferer.offererId == offerer_id,
            ),
        )
        .outerjoin(
            offerers_models.OffererInvitation,
            sa.and_(
                offerers_models.OffererInvitation.offererId == offerers_models.UserOfferer.offererId,
                offerers_models.OffererInvitation.email == users_models.User.email,
            ),
        )
        .options(options)
        .filter(users_models.User.id.in_(user_ids_subquery))
        .order_by(offerers_models.UserOfferer.id, users_models.User.full_name)
        .all()
    )

    users_invited = (
        db.session.query(offerers_models.OffererInvitation)
        .options(options)
        .filter(offerers_models.OffererInvitation.offererId == offerer_id)
        .filter(
            ~sa.exists().where(
                sa.and_(
                    users_models.User.email == offerers_models.OffererInvitation.email,
                    users_models.User.id.in_(user_ids_subquery),
                )
            )
        )
        .order_by(offerers_models.OffererInvitation.id)
        .all()
    )

    kwargs = {}

    if utils.has_current_user_permission(perm_models.Permissions.MANAGE_PRO_ENTITY):
        kwargs.update(
            {
                "invite_user_form": offerer_forms.InviteUserForm(),
                "invite_user_dst": url_for("backoffice_web.offerer.invite_user", offerer_id=offerer_id),
            }
        )

    users_pro = [row for row in rows if row.UserOfferer is not None]

    user_pro = []
    connect_as = {}
    for user in rows:
        if not user.UserOfferer:
            continue
        user_pro.append(user)
        connect_as[user.id] = get_connect_as(
            object_type="user",
            object_id=user.id,
            pc_pro_path="/",
        )

    users_invited_formatted: list[dict] = [
        {
            "id": None,
            "firstName": None,
            "lastName": None,
            "full_name": None,
            "email": user_invited.email,
            "UserOfferer": None,
            "OffererInvitation": user_invited,
            "isActive": False,
            "roles": [],
        }
        for user_invited in users_invited
    ]
    return render_template(
        "offerer/get/details/users.html",
        rows=users_pro + users_invited_formatted,
        connect_as=connect_as,
        admin_role=users_models.UserRole.ADMIN,
        anonymized_role=users_models.UserRole.ANONYMIZED,
        **kwargs,
    )


@offerer_blueprint.route("/users/<int:user_offerer_id>/delete", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def get_delete_user_offerer_form(offerer_id: int, user_offerer_id: int) -> utils.BackofficeResponse:
    user_offerer = (
        db.session.query(offerers_models.UserOfferer)
        .options(
            sa_orm.joinedload(offerers_models.UserOfferer.offerer).load_only(
                offerers_models.Offerer.id,
                offerers_models.Offerer.name,
            ),
        )
        .filter_by(id=user_offerer_id)
        .one_or_none()
    )
    if not user_offerer:
        raise NotFound()

    form = offerer_forms.OptionalCommentForm()

    return render_template(
        "components/dynamic/modal_form.html",
        form=form,
        dst=url_for(
            "backoffice_web.offerer.delete_user_offerer", offerer_id=offerer_id, user_offerer_id=user_offerer.id
        ),
        div_id=f"delete-modal-{user_offerer.id}",  # must be consistent with parameter passed to build_lazy_modal
        title=f"Supprimer le rattachement à {user_offerer.offerer.name.upper()}",
        button_text="Supprimer le rattachement",
        information="Cette action entraîne la suppression du lien utilisateur/entité juridique et non le rejet. Cette action n’envoie aucun mail à l’acteur culturel.",
        ajax_submit=False,
    )


@offerer_blueprint.route("/users/<int:user_offerer_id>/delete", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def delete_user_offerer(offerer_id: int, user_offerer_id: int) -> utils.BackofficeResponse:
    user_offerer = (
        db.session.query(offerers_models.UserOfferer)
        .join(offerers_models.UserOfferer.offerer)
        .join(offerers_models.UserOfferer.user)
        .options(
            sa_orm.contains_eager(offerers_models.UserOfferer.offerer).load_only(
                offerers_models.Offerer.id,
                offerers_models.Offerer.name,
            ),
            sa_orm.contains_eager(offerers_models.UserOfferer.user).load_only(users_models.User.email),
        )
        .filter(
            offerers_models.UserOfferer.offererId == offerer_id,
            offerers_models.UserOfferer.id == user_offerer_id,
        )
        .populate_existing()
        .with_for_update(key_share=True, read=True, of=offerers_models.Offerer)
        .one_or_none()
    )
    if not user_offerer:
        raise NotFound()

    form = offerer_forms.OptionalCommentForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return _self_redirect(offerer_id, active_tab="users", anchor="offerer_details_frame")
    user_email = user_offerer.user.email
    offerer_name = user_offerer.offerer.name

    offerers_api.delete_offerer_attachment(user_offerer, current_user, form.comment.data)

    flash(
        Markup(
            "Le rattachement de <b>{user_email}</b> à l'entité juridique <b>{offerer_name}</b> a été supprimé"
        ).format(user_email=user_email, offerer_name=offerer_name),
        "success",
    )
    return _self_redirect(offerer_id, active_tab="users", anchor="offerer_details_frame")


@offerer_blueprint.route("/invite-user", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def invite_user(offerer_id: int) -> utils.BackofficeResponse:
    offerer = db.session.query(offerers_models.Offerer).filter_by(id=offerer_id).one_or_none()
    if not offerer:
        raise NotFound()

    form = offerer_forms.InviteUserForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return _self_redirect(offerer.id, active_tab="users", anchor="offerer_details_frame")

    try:
        offerers_api.invite_member(offerer, form.email.data, current_user)
    except offerers_exceptions.EmailAlreadyInvitedException:
        mark_transaction_as_invalid()
        flash("Une invitation a déjà été envoyée à ce collaborateur", "warning")
    except offerers_exceptions.UserAlreadyAttachedToOffererException:
        mark_transaction_as_invalid()
        flash("Ce collaborateur est déjà rattaché à l'entité juridique", "warning")
    else:
        flash(Markup("L'invitation a été envoyée à <b>{email}</b>").format(email=form.email.data), "info")

    return _self_redirect(offerer.id, active_tab="users", anchor="offerer_details_frame")


@offerer_blueprint.route("/invitation/<int:invitation_id>/resend", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def resend_invitation(offerer_id: int, invitation_id: int) -> utils.BackofficeResponse:
    invitation = (
        db.session.query(offerers_models.OffererInvitation)
        .filter(
            offerers_models.OffererInvitation.id == invitation_id,
            offerers_models.OffererInvitation.offererId == offerer_id,
        )
        .options(sa_orm.joinedload(offerers_models.OffererInvitation.offerer, innerjoin=True))
        .one_or_none()
    )
    if not invitation:
        raise NotFound()

    try:
        offerers_api.invite_member_again(invitation.offerer, invitation.email)
    except offerers_exceptions.InviteAgainImpossibleException:
        mark_transaction_as_invalid()
        flash(Markup("L'invitation de <b>{email}</b> est déjà acceptée").format(email=invitation.email), "warning")
    else:
        flash(Markup("L'invitation a été renvoyée à <b>{email}</b>").format(email=invitation.email), "info")

    return _self_redirect(invitation.offerer.id, active_tab="users", anchor="offerer_details_frame")


@offerer_blueprint.route("/invitation/<int:invitation_id>/delete", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def delete_invitation(offerer_id: int, invitation_id: int) -> utils.BackofficeResponse:
    invitation = (
        db.session.query(offerers_models.OffererInvitation)
        .filter(
            offerers_models.OffererInvitation.id == invitation_id,
            offerers_models.OffererInvitation.offererId == offerer_id,
            offerers_models.OffererInvitation.status == offerers_models.InvitationStatus.PENDING,
        )
        .one_or_none()
    )
    if not invitation:
        raise NotFound()

    email = invitation.email

    db.session.delete(invitation)
    db.session.flush()

    flash(Markup("L'invitation de <b>{email}</b> a été supprimée").format(email=email), "success")
    return _self_redirect(offerer_id, active_tab="users", anchor="offerer_details_frame")


@offerer_blueprint.route("/venues", methods=["GET"])
def get_managed_venues(offerer_id: int) -> utils.BackofficeResponse:
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

    rows = (
        db.session.query(
            offerers_models.Venue,
            has_fraudulent_booking_query.label("has_fraudulent_booking"),
        )
        .filter_by(managingOffererId=offerer_id)
        .outerjoin(
            offerers_models.VenueBankAccountLink,
            sa.and_(
                offerers_models.VenueBankAccountLink.venueId == offerers_models.Venue.id,
                offerers_models.VenueBankAccountLink.timespan.contains(date_utils.get_naive_utc_now()),
            ),
        )
        .options(
            sa_orm.load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.isSoftDeleted,
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.siret,
                offerers_models.Venue.venueTypeCode,
                offerers_models.Venue.isPermanent,
                offerers_models.Venue.isOpenToPublic,
                offerers_models.Venue.isVirtual,
                offerers_models.Venue.managingOffererId,
            ),
            sa_orm.joinedload(offerers_models.Venue.collectiveDmsApplications).load_only(
                educational_models.CollectiveDmsApplication.state,
                educational_models.CollectiveDmsApplication.lastChangeDate,
                educational_models.CollectiveDmsApplication.application,
                educational_models.CollectiveDmsApplication.procedure,
            ),
            sa_orm.joinedload(offerers_models.Venue.registration).load_only(
                offerers_models.VenueRegistration.target,
                offerers_models.VenueRegistration.webPresence,
            ),
            sa_orm.contains_eager(offerers_models.Venue.bankAccountLinks)
            .joinedload(offerers_models.VenueBankAccountLink.bankAccount)
            .load_only(finance_models.BankAccount.id, finance_models.BankAccount.label),
            sa_orm.selectinload(offerers_models.Venue.venueProviders)
            .load_only(providers_models.VenueProvider.isActive)
            .joinedload(providers_models.VenueProvider.provider)
            .load_only(
                providers_models.Provider.id,
                providers_models.Provider.name,
                providers_models.Provider.isActive,
            ),
        )
        .order_by(offerers_models.Venue.common_name)
        .all()
    )

    connect_as = {}
    for row in rows:
        connect_as[row.Venue.id] = get_connect_as(
            object_type="venue",
            object_id=row.Venue.id,
            pc_pro_path=urls.build_pc_pro_venue_path(row.Venue),
        )

    return render_template(
        "offerer/get/details/managed_venues.html",
        offerer_id=offerer_id,
        rows=rows,
        connect_as=connect_as,
    )


def _render_get_create_venue_without_siret_form(form: pro_forms.CreateVenueWithoutSIRETForm, offerer_id: int) -> str:
    return render_template(
        "components/dynamic/modal_form.html",
        information="Ce formulaire permet de créer un nouveau partenaire culturel rattaché au SIRET choisi.",
        form=form,
        dst=url_for("backoffice_web.offerer.create_venue", offerer_id=offerer_id),
        div_id="create-venue-modal",  # must be consistent with parameter passed to build_lazy_modal
        title="Créer un partenaire culturel sans SIRET",
        button_text="Créer le partenaire culturel",
        ajax_submit=False,
    )


@offerer_blueprint.route("/create-without-siret", methods=["GET"])
@utils.permission_required(perm_models.Permissions.CREATE_PRO_ENTITY)
def get_create_venue_without_siret_form(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        db.session.query(offerers_models.Offerer)
        .options(sa_orm.joinedload(offerers_models.Offerer.managedVenues))
        .filter(offerers_models.Offerer.id == offerer_id)
        .one_or_none()
    )
    if not offerer:
        raise NotFound()
    form = pro_forms.CreateVenueWithoutSIRETForm(offerer)
    return _render_get_create_venue_without_siret_form(form, offerer_id)


@offerer_blueprint.route("/create-without-siret", methods=["POST"])
@utils.permission_required(perm_models.Permissions.CREATE_PRO_ENTITY)
def create_venue(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        db.session.query(offerers_models.Offerer)
        .options(sa_orm.joinedload(offerers_models.Offerer.managedVenues))
        .filter(offerers_models.Offerer.id == offerer_id)
        .one_or_none()
    )
    if not offerer:
        raise NotFound()
    form = pro_forms.CreateVenueWithoutSIRETForm(offerer)
    if not form.validate():
        mark_transaction_as_invalid()
        return _render_get_create_venue_without_siret_form(form, offerer_id), 400

    attachment_venue = (
        db.session.query(offerers_models.Venue)
        .filter(
            offerers_models.Venue.id == form.attachement_venue.data,
            offerers_models.Venue.managingOffererId == offerer_id,
        )
        .one_or_none()
    )
    if not attachment_venue:
        raise NotFound()
    assert attachment_venue.offererAddress

    attachment_address = attachment_venue.offererAddress.address

    address_body_model = address_serialize.LocationBodyModel(
        street=offerers_schemas.VenueAddress(attachment_address.street),
        city=offerers_schemas.VenueCity(attachment_address.city),
        postalCode=offerers_schemas.VenuePostalCode(attachment_address.postalCode),
        inseeCode=offerers_schemas.VenueInseeCode(attachment_address.inseeCode),
        latitude=float(attachment_address.latitude),
        longitude=float(attachment_address.longitude),
        banId=attachment_address.banId,
        label=None,
    )

    venue_creation_info = venues_serialize.PostVenueBodyModel(
        activity=attachment_venue.activity,
        # TODO(xordoquy): rename to location ?
        address=address_body_model,
        comment=offerers_schemas.VenueComment(
            "Partenaire culturel sans SIRET car dépend du SIRET d'un autre partenaire culturel"
        ),
        culturalDomains=[domain.name for domain in attachment_venue.collectiveDomains],
        siret=None,
        bookingEmail=offerers_schemas.VenueBookingEmail(attachment_venue.bookingEmail),
        managingOffererId=offerer_id,
        name=offerers_schemas.VenueName(form.public_name.data),
        publicName=offerers_schemas.VenuePublicName(form.public_name.data),
        venueLabelId=None,
        venueTypeCode=attachment_venue.venueTypeCode.name,
        withdrawalDetails=None,
        description=None,
        contact=None,
        audioDisabilityCompliant=None,
        mentalDisabilityCompliant=None,
        motorDisabilityCompliant=None,
        visualDisabilityCompliant=None,
        isOpenToPublic=False,
    )
    venue = offerers_api.create_venue(venue_creation_info, current_user, address=attachment_address)
    db.session.add(venue)
    offerers_api.link_venue_to_pricing_point(venue, attachment_venue.id)

    flash(Markup("Le partenaire culturel <b>{name}</b> a été créé").format(name=venue.common_name), "success")
    return redirect(url_for("backoffice_web.venue.get", venue_id=venue.id), code=303)


@offerer_blueprint.route("/addresses", methods=["GET"])
def get_offerer_addresses(offerer_id: int) -> utils.BackofficeResponse:
    offerer_addresses = (
        db.session.query(
            geography_models.Address.id,
            geography_models.Address.street,
            geography_models.Address.postalCode,
            geography_models.Address.city,
            geography_models.Address.banId,
            geography_models.Address.latitude,
            geography_models.Address.longitude,
            sa.func.array_agg(
                sa.func.coalesce(
                    sa.func.nullif(offerers_models.OffererAddress.label, ""),
                    sa.func.nullif(offerers_models.Venue.publicName, ""),
                    offerers_models.Venue.name,
                )
            ).label("titles"),
        )
        .select_from(geography_models.Address)
        .join(offerers_models.OffererAddress)
        .outerjoin(offerers_models.OffererAddress.venue)
        .filter(offerers_models.OffererAddress.offererId == offerer_id)
        .group_by(
            geography_models.Address.id,
            geography_models.Address.street,
            geography_models.Address.postalCode,
            geography_models.Address.city,
            geography_models.Address.banId,
            geography_models.Address.latitude,
            geography_models.Address.longitude,
        )
        .order_by(geography_models.Address.street)
        .all()
    )

    return render_template(
        "offerer/get/details/addresses.html",
        offerer_id=offerer_id,
        offerer_addresses=offerer_addresses,
    )


@offerer_blueprint.route("/collective-dms-applications", methods=["GET"])
def get_collective_dms_applications(offerer_id: int) -> utils.BackofficeResponse:
    collective_dms_applications = (
        db.session.query(educational_models.CollectiveDmsApplication)
        .filter(
            sa.select(offerers_models.Offerer.siren).filter(offerers_models.Offerer.id == offerer_id).scalar_subquery()
            == educational_models.CollectiveDmsApplication.siren
        )
        .options(
            sa_orm.load_only(
                educational_models.CollectiveDmsApplication.siret,
                educational_models.CollectiveDmsApplication.state,
                educational_models.CollectiveDmsApplication.depositDate,
                educational_models.CollectiveDmsApplication.lastChangeDate,
                educational_models.CollectiveDmsApplication.application,
                educational_models.CollectiveDmsApplication.procedure,
            ),
            sa_orm.joinedload(educational_models.CollectiveDmsApplication.venue).load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.isSoftDeleted,
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.siret,
            ),
        )
        .order_by(educational_models.CollectiveDmsApplication.depositDate.desc())
    )

    return render_template(
        "offerer/get/details/collective_dms_applications.html",
        collective_dms_applications=collective_dms_applications,
    )


@offerer_blueprint.route("/bank-accounts", methods=["GET"])
def get_bank_accounts(offerer_id: int) -> utils.BackofficeResponse:
    rows = (
        db.session.query(
            finance_models.BankAccount,
            sa.func.lower(finance_models.BankAccountStatusHistory.timespan).label("date_last_status_update"),
        )
        .outerjoin(
            finance_models.BankAccountStatusHistory,
            finance_models.BankAccountStatusHistory.bankAccountId == finance_models.BankAccount.id,
        )
        .filter(
            finance_models.BankAccount.offererId == offerer_id,
            sa.func.upper(finance_models.BankAccountStatusHistory.timespan).is_(None),
        )
        .options(
            sa_orm.load_only(
                finance_models.BankAccount.id,
                finance_models.BankAccount.label,
                finance_models.BankAccount.status,
                finance_models.BankAccount.offererId,
            ),
        )
        .order_by(finance_models.BankAccount.id.desc())
        .all()
    )
    connect_as = {}

    for row in rows:
        connect_as[row.BankAccount.id] = get_connect_as(
            object_id=row.BankAccount.id,
            object_type="bank_account",
            pc_pro_path=urls.build_pc_pro_bank_account_path(row.BankAccount),
        )
    return render_template(
        "offerer/get/details/bank_accounts.html",
        rows=rows,
        connect_as=connect_as,
    )


@offerer_blueprint.route("/comment", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def comment_offerer(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        db.session.query(offerers_models.Offerer)
        .filter_by(id=offerer_id)
        .populate_existing()
        .with_for_update(key_share=True, read=True)
        .one_or_none()
    )
    if not offerer:
        raise NotFound()

    form = offerer_forms.CommentForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
    else:
        offerers_api.add_comment_to_offerer(offerer, current_user, comment=form.comment.data)
        flash("Le commentaire a été enregistré", "success")

    return _self_redirect(offerer.id)


@offerer_blueprint.route("/individual-subscription", methods=["GET"])
@utils.permission_required_in([perm_models.Permissions.VALIDATE_OFFERER, perm_models.Permissions.READ_PRO_AE_INFO])
def get_individual_subscription(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        db.session.query(offerers_models.Offerer)
        .filter_by(id=offerer_id)
        .options(
            sa_orm.load_only(offerers_models.Offerer.id),
            sa_orm.joinedload(offerers_models.Offerer.individualSubscription),
            sa_orm.joinedload(offerers_models.Offerer.managedVenues)
            .load_only(offerers_models.Venue.id)
            .joinedload(offerers_models.Venue.collectiveDmsApplications)
            .load_only(
                educational_models.CollectiveDmsApplication.state,
                educational_models.CollectiveDmsApplication.lastChangeDate,
            ),
            sa_orm.joinedload(offerers_models.Offerer.tags),
        )
        .one_or_none()
    )

    if not offerer:
        raise NotFound()

    read_only = not utils.has_current_user_permission(perm_models.Permissions.VALIDATE_OFFERER)

    individual_subscription = offerer.individualSubscription
    if individual_subscription and individual_subscription.isEmailSent:
        form = offerer_forms.IndividualOffererSubscriptionForm(
            is_criminal_record_received=individual_subscription.isCriminalRecordReceived,
            date_criminal_record_received=individual_subscription.dateCriminalRecordReceived,
            is_certificate_received=individual_subscription.isCertificateReceived,
            certificate_details=individual_subscription.certificateDetails,
            is_experience_received=individual_subscription.isExperienceReceived,
            experience_details=individual_subscription.experienceDetails,
            has_1yr_experience=individual_subscription.has1yrExperience,
            has_4yr_experience=individual_subscription.has5yrExperience,
            is_certificate_valid=individual_subscription.isCertificateValid,
            read_only=read_only,
        )
    else:
        form = None

    adage_statuses = [venue.dms_adage_status for venue in offerer.managedVenues]
    for value in (
        GraphQLApplicationStates.accepted.value,
        GraphQLApplicationStates.refused.value,
        GraphQLApplicationStates.on_going.value,
    ):
        if value in adage_statuses:
            adage_decision = value
            break
    else:
        adage_decision = None

    return render_template(
        "offerer/get/details/individual_subscription.html",
        individual_subscription=individual_subscription,
        adage_decision=adage_decision,
        has_adage_tag=any(tag.name == "adage" for tag in offerer.tags),
        form=form,
        dst=url_for("backoffice_web.offerer.update_individual_subscription", offerer_id=offerer_id),
        create_dst=url_for("backoffice_web.offerer.create_individual_subscription", offerer_id=offerer_id),
        read_only=read_only,
    )


@offerer_blueprint.route("/send-individual-subscription-email", methods=["POST"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def create_individual_subscription(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        db.session.query(offerers_models.Offerer)
        .options(
            sa_orm.joinedload(offerers_models.Offerer.UserOfferers)
            .joinedload(offerers_models.UserOfferer.user)
            .load_only(users_models.User.email),
            sa_orm.joinedload(offerers_models.Offerer.individualSubscription),
        )
        .filter(offerers_models.Offerer.id == offerer_id)
        .one_or_none()
    )

    if not offerer:
        raise NotFound()

    if not offerer.individualSubscription:
        db.session.add(
            offerers_models.IndividualOffererSubscription(
                offererId=offerer_id, isEmailSent=True, dateEmailSent=date_utils.get_naive_utc_now()
            )
        )
    elif not offerer.individualSubscription.isEmailSent:
        offerer.individualSubscription.isEmailSent = True
        offerer.individualSubscription.dateEmailSent = date_utils.get_naive_utc_now()
        db.session.add(offerer.individualSubscription)

    transactional_mails.send_offerer_individual_subscription_reminder(offerer.UserOfferers[0].user.email)

    return _self_redirect(offerer_id, active_tab="subscription")


@offerer_blueprint.route("/individual-subscription", methods=["POST"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def update_individual_subscription(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        db.session.query(offerers_models.Offerer)
        .filter_by(id=offerer_id)
        .options(
            sa_orm.joinedload(offerers_models.Offerer.individualSubscription).load_only(
                offerers_models.IndividualOffererSubscription.id
            )
        )
        .one_or_none()
    )

    if not offerer:
        raise NotFound()

    form = offerer_forms.IndividualOffererSubscriptionForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return _self_redirect(offerer_id, active_tab="subscription")

    db.session.query(offerers_models.IndividualOffererSubscription).filter_by(offererId=offerer_id).update(
        {
            "isCriminalRecordReceived": form.is_criminal_record_received.data,
            "dateCriminalRecordReceived": form.date_criminal_record_received.data,
            "isCertificateReceived": form.is_certificate_received.data,
            "certificateDetails": form.certificate_details.data or None,
            "isExperienceReceived": form.is_experience_received.data,
            "experienceDetails": form.experience_details.data or None,
            "has1yrExperience": form.has_1yr_experience.data,
            "has5yrExperience": form.has_4yr_experience.data,
            "isCertificateValid": form.is_certificate_valid.data,
        },
        synchronize_session=False,
    )
    db.session.flush()

    return _self_redirect(offerer_id, active_tab="subscription")


@offerer_blueprint.route("/api-entreprise", methods=["GET"])
@utils.permission_required(perm_models.Permissions.READ_PRO_ENTREPRISE_INFO)
def get_entreprise_info(offerer_id: int) -> utils.BackofficeResponse:
    offerer = get_or_404(offerers_models.Offerer, offerer_id)

    if not siren_utils.is_valid_siren(offerer.siren):
        mark_transaction_as_invalid()
        return render_template("offerer/get/details/entreprise_info.html", is_invalid_siren=True, offerer=offerer)

    data: dict[str, typing.Any] = {}
    siren_info = None

    try:
        siren_info = entreprise_api.get_siren(offerer.siren, with_address=True, raise_if_non_public=False)
        data["siren_info"] = siren_info
    except entreprise_exceptions.UnknownEntityException:
        mark_transaction_as_invalid()
        data["siren_error"] = "Ce SIREN est inconnu dans la base de données Sirene, y compris dans les non-diffusibles"
    except entreprise_exceptions.EntrepriseException as error:
        mark_transaction_as_invalid()
        data["siren_error"] = str(error) or "Une erreur s'est produite lors de l'appel à API Entreprise"

    # Only data from INSEE is retrieved in this endpoint.
    # Then other endpoints below will be called asynchronously, so that we have one API call per endpoint.
    # This ensures that a long API call does not block other information or makes the current endpoint timeout.

    # I don't have a list but corporate taxes do not apply at least to "Entreprise Individuelle" and public structures
    if siren_info and siren_info.legal_category_code:
        data["show_dgfip_card"] = not (
            entreprise_api.siren_is_individual_or_public(siren_info)
            or (siren_info.creation_date and siren_info.creation_date.year >= datetime.date.today().year)
        )

    return render_template("offerer/get/details/entreprise_info.html", offerer=offerer, **data)


@offerer_blueprint.route("/api-entreprise/rcs", methods=["GET"])
@utils.permission_required(perm_models.Permissions.READ_PRO_ENTREPRISE_INFO)
def get_entreprise_rcs_info(offerer_id: int) -> utils.BackofficeResponse:
    offerer = get_or_404(offerers_models.Offerer, offerer_id)

    if not siren_utils.is_valid_siren(offerer.siren):
        raise NotFound()

    data: dict[str, typing.Any] = {}

    try:
        data["rcs_info"] = entreprise_api.get_rcs(offerer.siren)
    except entreprise_exceptions.EntrepriseException as error:
        mark_transaction_as_invalid()
        data["rcs_error"] = str(error) or "Une erreur s'est produite lors de l'appel à API Entreprise"

    return render_template("offerer/get/details/entreprise_info_rcs.html", **data)


@offerer_blueprint.route("/api-entreprise/urssaf", methods=["GET"])
@utils.permission_required(perm_models.Permissions.READ_PRO_SENSITIVE_INFO)
def get_entreprise_urssaf_info(offerer_id: int) -> utils.BackofficeResponse:
    offerer = get_or_404(offerers_models.Offerer, offerer_id)

    if not siren_utils.is_valid_siren(offerer.siren):
        raise NotFound()

    data: dict[str, typing.Any] = {}

    try:
        data["urssaf_info"] = entreprise_api.get_urssaf(offerer.siren)
    except entreprise_exceptions.EntrepriseException as error:
        mark_transaction_as_invalid()
        data["urssaf_error"] = str(error) or "Une erreur s'est produite lors de l'appel à API Entreprise"
    else:
        history_api.add_action(
            history_models.ActionType.OFFERER_ATTESTATION_CHECKED,
            author=current_user,
            offerer=offerer,
            provider="URSSAF",
        )
        db.session.flush()

    return render_template("offerer/get/details/entreprise_info_urssaf.html", **data)


@offerer_blueprint.route("/api-entreprise/dgfip", methods=["GET"])
@utils.permission_required(perm_models.Permissions.READ_PRO_SENSITIVE_INFO)
def get_entreprise_dgfip_info(offerer_id: int) -> utils.BackofficeResponse:
    offerer = get_or_404(offerers_models.Offerer, offerer_id)

    if not siren_utils.is_valid_siren(offerer.siren):
        raise NotFound()

    data: dict[str, typing.Any] = {}

    try:
        data["dgfip_info"] = entreprise_api.get_dgfip(offerer.siren)
    except entreprise_exceptions.EntrepriseException as error:
        mark_transaction_as_invalid()
        data["dgfip_error"] = str(error) or "Une erreur s'est produite lors de l'appel à API Entreprise"
    else:
        history_api.add_action(
            history_models.ActionType.OFFERER_ATTESTATION_CHECKED,
            author=current_user,
            offerer=offerer,
            provider="DGFIP",
        )
        db.session.flush()

    return render_template("offerer/get/details/entreprise_info_dgfip.html", **data)


@offerer_blueprint.route("/close", methods=["GET"])
@utils.permission_required(perm_models.Permissions.CLOSE_OFFERER)
def get_close_offerer_form(offerer_id: int) -> utils.BackofficeResponse:
    offerer = get_or_404(offerers_models.Offerer, offerer_id)

    form = offerer_forms.OffererClosureForm()
    info = None

    count_individual_bookings = len(offerers_api.get_individual_bookings_to_cancel_on_offerer_closure(offerer.id))
    count_collective_bookings = len(offerers_api.get_collective_bookings_to_cancel_on_offerer_closure(offerer.id))

    if count_individual_bookings or count_collective_bookings:
        info = Markup("<p>La fermeture de l'entité juridique entraînera l'annulation automatique de :<p><ul>")
        if count_individual_bookings:
            info += Markup(
                """<li><b>{count}</b> <a href="{url}" target="_blank" class="link-primary">réservation{s} individuelle{s}</a></li>"""
            ).format(
                count=count_individual_bookings,
                url=url_for(
                    "backoffice_web.individual_bookings.list_individual_bookings",
                    offerer=offerer_id,
                    status=[bookings_forms.BookingStatus.BOOKED.name, bookings_forms.BookingStatus.CONFIRMED.name],
                ),
                s=pluralize(count_individual_bookings),
            )
        if count_collective_bookings:
            info += Markup(
                """<li><b>{count}</b> <a href="{url}" target="_blank" class="link-primary">réservation{s} collective{s}</a></li>"""
            ).format(
                count=count_collective_bookings,
                url=url_for(
                    "backoffice_web.collective_bookings.list_collective_bookings",
                    offerer=offerer_id,
                    status=[
                        bookings_forms.CollectiveBookingStatus.PENDING.name,
                        bookings_forms.CollectiveBookingStatus.CONFIRMED.name,
                    ],
                ),
                s=pluralize(count_collective_bookings),
            )
        info += Markup("</ul>")

    return render_template(
        "components/dynamic/modal_form.html",
        info=info,
        form=form,
        dst=url_for("backoffice_web.offerer.close_offerer", offerer_id=offerer.id),
        div_id=f"close-modal-{offerer.id}",  # must be consistent with parameter passed to build_lazy_modal
        title=f"Fermer l'entité juridique {offerer.name.upper()}",
        button_text="Fermer l'entité juridique",
        ajax_submit=False,
    )


@offerer_blueprint.route("/close", methods=["POST"])
@utils.permission_required(perm_models.Permissions.CLOSE_OFFERER)
def close_offerer(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        db.session.query(offerers_models.Offerer)
        .filter_by(id=offerer_id)
        .populate_existing()
        .with_for_update(key_share=True)
        .one_or_none()
    )
    if not offerer:
        raise NotFound()

    if not offerer.isValidated:
        flash("Seule une entité juridique validée peut être fermée", "warning")
        return _self_redirect(offerer.id)

    form = offerer_forms.OffererClosureForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return _self_redirect(offerer.id)

    offerers_api.close_offerer(
        offerer,
        is_manual=True,
        author_user=current_user,
        comment=form.comment.data,
        zendesk_id=form.zendesk_id.data,
        drive_link=form.drive_link.data,
    )

    flash(Markup("L'entité juridique <b>{name}</b> a été fermée").format(name=offerer.name), "success")
    return _self_redirect(offerer.id)
