import datetime
import typing

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.connectors.dms.models import GraphQLApplicationStates
from pcapi.connectors.entreprise import api as entreprise_api
from pcapi.connectors.entreprise import exceptions as entreprise_exceptions
from pcapi.core.educational import models as educational_models
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.finance import models as finance_models
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.routes.backoffice.pro import forms as pro_forms
from pcapi.utils import regions as regions_utils
from pcapi.utils.siren import is_valid_siren

from . import forms as offerer_forms
from . import serialization
from .. import utils
from ..forms import empty as empty_forms


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
                offerers_models.VenueBankAccountLink.timespan.contains(datetime.datetime.utcnow()),
            ),
        )
        .filter(
            offerers_models.Venue.managingOffererId == offerer_id,
        )
        .group_by(sa.text("status"))
        .subquery()
    )

    adage_query = (
        sa.select(
            sa.func.concat(
                sa.func.coalesce(sa.func.sum(sa.case([(offerers_models.Venue.adageId.is_not(None), 1)], else_=0)), 0),
                "/",
                sa.func.count(offerers_models.Venue.id),
            )
        )
        .select_from(offerers_models.Venue)
        .filter(
            offerers_models.Venue.managingOffererId == offerers_models.Offerer.id,
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
        .where(~offerers_models.Venue.isVirtual)
    )

    has_offerer_address_query = (
        sa.select(1)
        .select_from(offerers_models.OffererAddress)
        .where(offerers_models.OffererAddress.offererId == offerers_models.Offerer.id)
        .correlate(offerers_models.Offerer)
        .exists()
    )

    has_new_nav_users_subquery = (
        sa.select(1)
        .select_from(offerers_models.UserOfferer)
        .join(
            users_models.UserProNewNavState,
            sa.and_(
                users_models.UserProNewNavState.userId == offerers_models.UserOfferer.userId,
                users_models.UserProNewNavState.newNavDate < datetime.datetime.utcnow(),
            ),
        )
        .where(
            offerers_models.UserOfferer.offererId == offerers_models.Offerer.id,
        )
        .correlate(offerers_models.Offerer)
        .exists()
    )

    has_old_nav_users_subquery = (
        sa.select(1)
        .select_from(offerers_models.UserOfferer)
        .outerjoin(
            users_models.UserProNewNavState,
            users_models.UserProNewNavState.userId == offerers_models.UserOfferer.userId,
        )
        .where(
            offerers_models.UserOfferer.offererId == offerers_models.Offerer.id,
            users_models.UserProNewNavState.newNavDate.is_(None),
        )
        .correlate(offerers_models.Offerer)
        .exists()
    )

    offerer_query = (
        db.session.query(
            offerers_models.Offerer,
            bank_information_query.scalar_subquery().label("bank_information"),
            has_non_virtual_venues_query.label("has_non_virtual_venues"),
            has_offerer_address_query.label("has_offerer_address"),
            adage_query.label("adage_information"),
            users_models.User.phoneNumber.label("creator_phone_number"),  # type: ignore[attr-defined]
        )
        .filter(offerers_models.Offerer.id == offerer_id)
        .outerjoin(offerers_models.UserOfferer, offerers_models.UserOfferer.id == creator_user_offerer_id_query)
        .outerjoin(offerers_models.UserOfferer.user)
        .options(
            sa.orm.joinedload(offerers_models.Offerer.individualSubscription).load_only(
                offerers_models.IndividualOffererSubscription.id
            ),
            sa.orm.with_expression(offerers_models.Offerer.hasNewNavUsers, has_new_nav_users_subquery),
            sa.orm.with_expression(offerers_models.Offerer.hasOldNavUsers, has_old_nav_users_subquery),
            sa.orm.joinedload(offerers_models.Offerer.confidenceRule).load_only(
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

    bank_information = row.bank_information or {}
    bank_information_status = serialization.OffererBankInformationStatus(
        ok=bank_information.get("ok", 0), ko=bank_information.get("ko", 0)
    )
    if not edit_offerer_form:
        edit_offerer_form = offerer_forms.EditOffererForm(
            name=offerer.name,
            postal_address_autocomplete=(
                f"{offerer.street}, {offerer.postalCode} {offerer.city}"
                if offerer.street is not None and offerer.city is not None and offerer.postalCode is not None
                else None
            ),
            city=offerer.city,
            postal_code=offerer.postalCode,
            street=offerer.street,
            tags=offerer.tags,
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

    return render_template(
        "offerer/get.html",
        search_form=search_form,
        search_dst=url_for("backoffice_web.pro.search_pro"),
        offerer=offerer,
        region=regions_utils.get_region_name_from_postal_code(offerer.postalCode),
        creator_phone_number=row.creator_phone_number,
        adage_information=row.adage_information,
        bank_information_status=bank_information_status,
        edit_offerer_form=edit_offerer_form,
        suspension_form=offerer_forms.SuspendOffererForm(),
        delete_offerer_form=empty_forms.EmptyForm(),
        show_subscription_tab=show_subscription_tab,
        has_offerer_address=row.has_offerer_address,
        active_tab=request.args.get("active_tab", "history"),
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


@typing.no_type_check
def get_stats_data(offerer_id: int) -> dict:
    PLACEHOLDER = -1
    offers_stats = offerers_api.get_offerer_offers_stats(offerer_id, max_offer_count=1000)
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
        stats["total_revenue"] = offerers_api.get_offerer_total_revenue(offerer_id)

    return stats


@offerer_blueprint.route("/stats", methods=["GET"])
def get_stats(offerer_id: int) -> utils.BackofficeResponse:
    data = get_stats_data(offerer_id)
    return render_template(
        "offerer/get/stats.html",
        stats=data,
        offerer_id=offerer_id,
    )


@offerer_blueprint.route("/revenue-details", methods=["GET"])
def get_revenue_details(offerer_id: int) -> utils.BackofficeResponse:
    details = offerers_repository.get_revenues_per_year(offererId=offerer_id)
    return render_template(
        "components/revenue_details.html",
        details=details,
    )


@offerer_blueprint.route("/suspend", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def suspend_offerer(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        offerers_models.Offerer.query.filter_by(id=offerer_id)
        .populate_existing()
        .with_for_update(key_share=True)
        .one_or_none()
    )
    if not offerer:
        raise NotFound()

    form = offerer_forms.SuspendOffererForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
    else:
        try:
            offerers_api.suspend_offerer(offerer, current_user, form.comment.data)
        except offerers_exceptions.CannotSuspendOffererWithBookingsException:
            flash("Impossible de suspendre une structure juridique pour laquelle il existe des réservations", "warning")
        else:
            flash(
                Markup("La structure <b>{offerer_name}</b> ({offerer_id}) a été suspendue").format(
                    offerer_name=offerer.name, offerer_id=offerer_id
                ),
                "success",
            )

    return _self_redirect(offerer.id)


@offerer_blueprint.route("/unsuspend", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def unsuspend_offerer(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        offerers_models.Offerer.query.filter_by(id=offerer_id)
        .populate_existing()
        .with_for_update(key_share=True)
        .one_or_none()
    )
    if not offerer:
        raise NotFound()

    form = offerer_forms.SuspendOffererForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
    else:
        offerers_api.unsuspend_offerer(offerer, current_user, form.comment.data)
        flash(
            Markup("La structure <b>{offerer_name}</b> ({offerer_id}) a été réactivée").format(
                offerer_name=offerer.name, offerer_id=offerer_id
            ),
            "success",
        )

    return _self_redirect(offerer.id)


@offerer_blueprint.route("/delete", methods=["POST"])
@utils.permission_required(perm_models.Permissions.DELETE_PRO_ENTITY)
def delete_offerer(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.filter_by(id=offerer_id).populate_existing().with_for_update().one_or_none()
    if not offerer:
        raise NotFound()

    offerer_name = offerer.name

    # Get users to update before association info is deleted
    # joined user is no longer available after delete_model()
    emails = offerers_repository.get_emails_by_offerer(offerer)

    try:
        offerers_api.delete_offerer(offerer.id)
    except offerers_exceptions.CannotDeleteOffererWithBookingsException:
        flash("Impossible de supprimer une structure juridique pour laquelle il existe des réservations", "warning")
        return _self_redirect(offerer.id)

    for email in emails:
        external_attributes_api.update_external_pro(email)

    flash(
        Markup("La structure <b>{offerer_name}</b> ({offerer_id}) a été supprimée").format(
            offerer_name=offerer_name, offerer_id=offerer_id
        ),
        "success",
    )
    return redirect(url_for("backoffice_web.pro.search_pro"), code=303)


@offerer_blueprint.route("", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def update_offerer(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        offerers_models.Offerer.query.filter_by(id=offerer_id)
        .populate_existing()
        .with_for_update(key_share=True)
        .one_or_none()
    )
    if not offerer:
        raise NotFound()

    form = offerer_forms.EditOffererForm()
    if not form.validate():
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
        city=form.city.data,
        postal_code=form.postal_code.data,
        street=form.street.data,
        tags=form.tags.data,
    )

    flash("Les informations ont été mises à jour", "success")
    return _self_redirect(offerer.id)


@offerer_blueprint.route("/history", methods=["GET"])
def get_history(offerer_id: int) -> utils.BackofficeResponse:
    # this should not be necessary but in case there is a huge amount
    # of actions, it is safer to set a limit
    max_actions_count = 50

    actions_history = (
        history_models.ActionHistory.query.filter_by(offererId=offerer_id)
        .order_by(history_models.ActionHistory.actionDate.desc())
        .limit(max_actions_count)
        .options(
            sa.orm.joinedload(history_models.ActionHistory.user).load_only(
                users_models.User.id, users_models.User.firstName, users_models.User.lastName
            ),
            sa.orm.joinedload(history_models.ActionHistory.authorUser).load_only(
                users_models.User.id, users_models.User.firstName, users_models.User.lastName
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

    options = sa.orm.joinedload(offerers_models.OffererInvitation.user).load_only(
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
            users_models.UserProNewNavState.newNavDate.is_not(None).label("hasNewNav"),
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
        .outerjoin(users_models.UserProNewNavState, users_models.UserProNewNavState.userId == users_models.User.id)
        .options(options)
        .filter(users_models.User.id.in_(user_ids_subquery))
        .order_by(offerers_models.UserOfferer.id, users_models.User.full_name)
        .all()
    )

    users_invited = (
        offerers_models.OffererInvitation.query.options(options)
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

    can_add_user = utils.has_current_user_permission(perm_models.Permissions.VALIDATE_OFFERER)
    if can_add_user:
        # Users whose association to the offerer has been removed, for which relationship is only from history
        removed_users = [row for row in rows if row.UserOfferer is None]
        if removed_users:
            add_user_form = offerer_forms.AddProUserForm()
            add_user_form.pro_user_id.choices = [(user.id, f"{user.full_name} ({user.id})") for user in removed_users]
            kwargs.update(
                {
                    "add_user_form": add_user_form,
                    "add_user_dst": url_for(
                        "backoffice_web.offerer.add_user_offerer_and_validate", offerer_id=offerer_id
                    ),
                }
            )

    users_pro = [row for row in rows if row.UserOfferer is not None]

    users_invited_formatted = [
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
        admin_role=users_models.UserRole.ADMIN,
        anonymized_role=users_models.UserRole.ANONYMIZED,
        **kwargs,
    )


@offerer_blueprint.route("/users/<int:user_offerer_id>/delete", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def get_delete_user_offerer_form(offerer_id: int, user_offerer_id: int) -> utils.BackofficeResponse:
    user_offerer = (
        offerers_models.UserOfferer.query.options(
            sa.orm.joinedload(offerers_models.UserOfferer.offerer).load_only(
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
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for(
            "backoffice_web.offerer.delete_user_offerer", offerer_id=offerer_id, user_offerer_id=user_offerer.id
        ),
        div_id=f"delete-modal-{user_offerer.id}",  # must be consistent with parameter passed to build_lazy_modal
        title=f"Supprimer le rattachement à {user_offerer.offerer.name.upper()}",
        button_text="Supprimer le rattachement",
        information="Cette action entraîne la suppression du lien utilisateur/structure et non le rejet. Cette action n’envoie aucun mail à l’acteur culturel.",
    )


@offerer_blueprint.route("/users/<int:user_offerer_id>/delete", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def delete_user_offerer(offerer_id: int, user_offerer_id: int) -> utils.BackofficeResponse:
    user_offerer = (
        offerers_models.UserOfferer.query.join(offerers_models.UserOfferer.offerer)
        .join(offerers_models.UserOfferer.user)
        .options(
            sa.orm.contains_eager(offerers_models.UserOfferer.offerer).load_only(
                offerers_models.Offerer.id,
                offerers_models.Offerer.name,
            ),
            sa.orm.contains_eager(offerers_models.UserOfferer.user).load_only(users_models.User.email),
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
        flash(utils.build_form_error_msg(form), "warning")
        return _self_redirect(offerer_id, active_tab="users", anchor="offerer_details_frame")
    user_email = user_offerer.user.email
    offerer_name = user_offerer.offerer.name

    offerers_api.delete_offerer_attachment(user_offerer, current_user, form.comment.data)

    flash(
        f"Le rattachement de {user_email} à la structure {offerer_name} a été supprimé",
        "success",
    )
    return _self_redirect(offerer_id, active_tab="users", anchor="offerer_details_frame")


@offerer_blueprint.route("/add-user", methods=["POST"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def add_user_offerer_and_validate(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.filter_by(id=offerer_id).one_or_none()
    if not offerer:
        raise NotFound()

    form = offerer_forms.AddProUserForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _self_redirect(offerer.id, active_tab="users", anchor="offerer_details_frame")

    # Single request to get User object and check that the id is within the list of previously attached users, which
    # ensures that:
    # - user exists with given id
    # - user_offerer entry does not exist with same ids
    user = (
        users_models.User.query.join(
            history_models.ActionHistory,
            sa.and_(
                history_models.ActionHistory.userId == users_models.User.id,
                history_models.ActionHistory.offererId == offerer_id,
            ),
        )
        .filter(
            users_models.User.id == form.pro_user_id.data,
            users_models.User.id.not_in(
                db.session.query(offerers_models.UserOfferer.userId)
                .filter(offerers_models.UserOfferer.offererId == offerer_id)
                .subquery()
            ),
        )
        .limit(1)
    ).one_or_none()

    if not user:
        flash("L'ID ne correspond pas à un ancien rattachement à la structure", "warning")
        return _self_redirect(offerer.id, active_tab="users", anchor="offerer_details_frame")

    new_user_offerer = offerers_models.UserOfferer(offerer=offerer, user=user, validationStatus=ValidationStatus.NEW)
    offerers_api.validate_offerer_attachment(new_user_offerer, current_user, form.comment.data)

    flash(
        Markup("Le rattachement de <b>{email}</b> à la structure <b>{offerer_name}</b> a été ajouté").format(
            email=user.email, offerer_name=offerer.name
        ),
        "success",
    )
    return _self_redirect(offerer.id, active_tab="users", anchor="offerer_details_frame")


@offerer_blueprint.route("/venues", methods=["GET"])
def get_managed_venues(offerer_id: int) -> utils.BackofficeResponse:
    venues = (
        offerers_models.Venue.query.filter_by(managingOffererId=offerer_id)
        .outerjoin(
            offerers_models.VenueBankAccountLink,
            sa.and_(
                offerers_models.VenueBankAccountLink.venueId == offerers_models.Venue.id,
                offerers_models.VenueBankAccountLink.timespan.contains(datetime.datetime.utcnow()),
            ),
        )
        .options(
            sa.orm.load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.siret,
                offerers_models.Venue.venueTypeCode,
                offerers_models.Venue.isPermanent,
                offerers_models.Venue.isVirtual,
                offerers_models.Venue.managingOffererId,
            ),
            sa.orm.joinedload(offerers_models.Venue.collectiveDmsApplications).load_only(
                educational_models.CollectiveDmsApplication.state,
                educational_models.CollectiveDmsApplication.lastChangeDate,
                educational_models.CollectiveDmsApplication.application,
                educational_models.CollectiveDmsApplication.procedure,
            ),
            sa.orm.joinedload(offerers_models.Venue.registration).load_only(
                offerers_models.VenueRegistration.target,
                offerers_models.VenueRegistration.webPresence,
            ),
            sa.orm.contains_eager(offerers_models.Venue.bankAccountLinks)
            .joinedload(offerers_models.VenueBankAccountLink.bankAccount)
            .load_only(finance_models.BankAccount.id, finance_models.BankAccount.label),
        )
        .order_by(offerers_models.Venue.common_name)
        .all()
    )

    return render_template(
        "offerer/get/details/managed_venues.html",
        venues=venues,
    )


@offerer_blueprint.route("/addresses", methods=["GET"])
def get_offerer_addresses(offerer_id: int) -> utils.BackofficeResponse:
    offerer_addresses = (
        offerers_models.OffererAddress.query.filter_by(offererId=offerer_id)
        .options(
            sa.orm.load_only(offerers_models.OffererAddress.label),
            sa.orm.joinedload(offerers_models.OffererAddress.address),
        )
        .order_by(offerers_models.OffererAddress.label)
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
        educational_models.CollectiveDmsApplication.query.filter(
            educational_models.CollectiveDmsApplication.siret.startswith(
                sa.select(offerers_models.Offerer.siren)
                .filter(offerers_models.Offerer.id == offerer_id)
                .scalar_subquery()
            )
        )
        .options(
            sa.orm.load_only(
                educational_models.CollectiveDmsApplication.siret,
                educational_models.CollectiveDmsApplication.state,
                educational_models.CollectiveDmsApplication.depositDate,
                educational_models.CollectiveDmsApplication.lastChangeDate,
                educational_models.CollectiveDmsApplication.application,
                educational_models.CollectiveDmsApplication.procedure,
            ),
            sa.orm.joinedload(educational_models.CollectiveDmsApplication.venue).load_only(
                offerers_models.Venue.id,
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
    bank_accounts = (
        finance_models.BankAccount.query.filter_by(offererId=offerer_id)
        .options(
            sa.orm.load_only(
                finance_models.BankAccount.id,
                finance_models.BankAccount.label,
                finance_models.BankAccount.status,
                finance_models.BankAccount.offererId,
            ),
        )
        .order_by(finance_models.BankAccount.label)
        .all()
    )

    return render_template(
        "offerer/get/details/bank_accounts.html",
        bank_accounts=bank_accounts,
    )


@offerer_blueprint.route("/comment", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def comment_offerer(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        offerers_models.Offerer.query.filter_by(id=offerer_id)
        .populate_existing()
        .with_for_update(key_share=True, read=True)
        .one_or_none()
    )
    if not offerer:
        raise NotFound()

    form = offerer_forms.CommentForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
    else:
        offerers_api.add_comment_to_offerer(offerer, current_user, comment=form.comment.data)
        flash("Le commentaire a été enregistré", "success")

    return _self_redirect(offerer.id)


@offerer_blueprint.route("/individual-subscription", methods=["GET"])
@utils.permission_required_in([perm_models.Permissions.VALIDATE_OFFERER, perm_models.Permissions.READ_PRO_AE_INFO])
def get_individual_subscription(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        offerers_models.Offerer.query.filter_by(id=offerer_id)
        .options(
            sa.orm.load_only(offerers_models.Offerer.id),
            sa.orm.joinedload(offerers_models.Offerer.individualSubscription),
            sa.orm.joinedload(offerers_models.Offerer.managedVenues)
            .load_only(offerers_models.Venue.id)
            .joinedload(offerers_models.Venue.collectiveDmsApplications)
            .load_only(
                educational_models.CollectiveDmsApplication.state,
                educational_models.CollectiveDmsApplication.lastChangeDate,
            ),
            sa.orm.joinedload(offerers_models.Offerer.tags),
        )
        .one_or_none()
    )

    if not offerer:
        raise NotFound()

    read_only = not utils.has_current_user_permission(perm_models.Permissions.VALIDATE_OFFERER)

    individual_subscription = offerer.individualSubscription
    if individual_subscription:
        form = offerer_forms.IndividualOffererSubscriptionForm(
            is_email_sent=individual_subscription.isEmailSent,
            date_email_sent=individual_subscription.dateEmailSent,
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
        # Form with default empty values, which will be inserted in database when saved
        form = offerer_forms.IndividualOffererSubscriptionForm(read_only=read_only)

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
        read_only=read_only,
    )


@offerer_blueprint.route("/individual-subscription", methods=["POST"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def update_individual_subscription(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        offerers_models.Offerer.query.filter_by(id=offerer_id)
        .options(
            sa.orm.joinedload(offerers_models.Offerer.individualSubscription).load_only(
                offerers_models.IndividualOffererSubscription.id
            )
        )
        .one_or_none()
    )

    if not offerer:
        raise NotFound()

    form = offerer_forms.IndividualOffererSubscriptionForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _self_redirect(offerer_id, active_tab="subscription")

    data = {
        "isEmailSent": form.is_email_sent.data,
        "dateEmailSent": form.date_email_sent.data,
        "isCriminalRecordReceived": form.is_criminal_record_received.data,
        "dateCriminalRecordReceived": form.date_criminal_record_received.data,
        "isCertificateReceived": form.is_certificate_received.data,
        "certificateDetails": form.certificate_details.data or None,
        "isExperienceReceived": form.is_experience_received.data,
        "experienceDetails": form.experience_details.data or None,
        "has1yrExperience": form.has_1yr_experience.data,
        "has5yrExperience": form.has_4yr_experience.data,
        "isCertificateValid": form.is_certificate_valid.data,
    }

    if offerer.individualSubscription:
        offerers_models.IndividualOffererSubscription.query.filter_by(offererId=offerer_id).update(
            data, synchronize_session=False
        )
    else:
        db.session.add(offerers_models.IndividualOffererSubscription(offererId=offerer_id, **data))
    db.session.commit()

    return _self_redirect(offerer_id, active_tab="subscription")


@offerer_blueprint.route("/api-entreprise", methods=["GET"])
@utils.permission_required(perm_models.Permissions.READ_PRO_ENTREPRISE_INFO)
def get_entreprise_info(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)

    if not offerer.siren:
        raise NotFound()

    if not is_valid_siren(offerer.siren):
        return render_template("offerer/get/details/entreprise_info.html", is_invalid_siren=True, offerer=offerer)

    data: dict[str, typing.Any] = {}
    siren_info = None

    try:
        siren_info = entreprise_api.get_siren(offerer.siren, with_address=True, raise_if_non_public=False)
        data["siren_info"] = siren_info
    except entreprise_exceptions.UnknownEntityException:
        data["siren_error"] = "Ce SIREN est inconnu dans la base de données Sirene, y compris dans les non-diffusibles"
    except entreprise_exceptions.SireneException as error:
        data["siren_error"] = str(error) or "Une erreur s'est produite lors de l'appel à API Entreprise"

    # Only data from INSEE is retrieved in this endpoint.
    # Then other endpoints below will be called in turbo-frames, so that we have one API call per endpoint.
    # This ensures that a long API call does not block other information or makes the current endpoint timeout.

    # I don't have a list but corporate taxes do not apply at least to "Entreprise Individuelle" and public structures
    if siren_info and siren_info.legal_category_code:
        data["show_dgfip_card"] = not (
            entreprise_api.siren_is_individual_or_public(siren_info)
            or siren_info.creation_date.year >= datetime.date.today().year
        )

    return render_template("offerer/get/details/entreprise_info.html", offerer=offerer, **data)


@offerer_blueprint.route("/api-entreprise/rcs", methods=["GET"])
@utils.permission_required(perm_models.Permissions.READ_PRO_ENTREPRISE_INFO)
def get_entreprise_rcs_info(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)

    if not offerer.siren or not is_valid_siren(offerer.siren):
        raise NotFound()

    data: dict[str, typing.Any] = {}

    try:
        data["rcs_info"] = entreprise_api.get_rcs(offerer.siren)
    except entreprise_exceptions.EntrepriseException as error:
        data["rcs_error"] = str(error) or "Une erreur s'est produite lors de l'appel à API Entreprise"

    return render_template("offerer/get/details/entreprise_info_rcs.html", **data)


@offerer_blueprint.route("/api-entreprise/urssaf", methods=["GET"])
@utils.permission_required(perm_models.Permissions.READ_PRO_SENSITIVE_INFO)
def get_entreprise_urssaf_info(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)

    if not offerer.siren or not is_valid_siren(offerer.siren):
        raise NotFound()

    data: dict[str, typing.Any] = {}

    try:
        data["urssaf_info"] = entreprise_api.get_urssaf(offerer.siren)
    except entreprise_exceptions.EntrepriseException as error:
        data["urssaf_error"] = str(error) or "Une erreur s'est produite lors de l'appel à API Entreprise"
    else:
        history_api.add_action(
            history_models.ActionType.OFFERER_ATTESTATION_CHECKED, current_user, offerer=offerer, provider="URSSAF"
        )
        db.session.commit()

    return render_template("offerer/get/details/entreprise_info_urssaf.html", **data)


@offerer_blueprint.route("/api-entreprise/dgfip", methods=["GET"])
@utils.permission_required(perm_models.Permissions.READ_PRO_SENSITIVE_INFO)
def get_entreprise_dgfip_info(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)

    if not offerer.siren or not is_valid_siren(offerer.siren):
        raise NotFound()

    data: dict[str, typing.Any] = {}

    try:
        data["dgfip_info"] = entreprise_api.get_dgfip(offerer.siren)
    except entreprise_exceptions.EntrepriseException as error:
        data["dgfip_error"] = str(error) or "Une erreur s'est produite lors de l'appel à API Entreprise"
    else:
        history_api.add_action(
            history_models.ActionType.OFFERER_ATTESTATION_CHECKED, current_user, offerer=offerer, provider="DGFIP"
        )
        db.session.commit()

    return render_template("offerer/get/details/entreprise_info_dgfip.html", **data)
