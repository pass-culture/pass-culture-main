import datetime
from functools import partial
from functools import reduce
import typing
from urllib.parse import urlparse

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_sqlalchemy import BaseQuery
from markupsafe import Markup
import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.core.educational import models as educational_models
from pcapi.core.external.attributes import api as external_attributes_api
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
from pcapi.scripts.offerer.delete_cascade_offerer_by_id import delete_cascade_offerer_by_id
from pcapi.utils import date as date_utils
import pcapi.utils.regions as regions_utils

from . import search_utils
from . import utils
from .forms import empty as empty_forms
from .forms import offerer as offerer_forms
from .serialization import offerers as serialization


offerer_blueprint = utils.child_backoffice_blueprint(
    "offerer",
    __name__,
    url_prefix="/pro/offerer/<int:offerer_id>",
    permission=perm_models.Permissions.READ_PRO_ENTITY,
)


def filter_homologation_tags(tags: list[offerers_models.OffererTag]) -> list[offerers_models.OffererTag]:
    return [tag for tag in tags if "homologation" in [cat.name for cat in tag.categories]]


def render_offerer_details(
    offerer: offerers_models.Offerer, edit_offerer_form: offerer_forms.EditOffererForm | None = None
) -> str:
    basic_info = offerers_api.get_offerer_basic_info(offerer.id)

    if not basic_info:
        raise NotFound()

    bank_informations = basic_info.bank_informations or {}
    bank_informations_ok = bank_informations.get("ok", 0)
    bank_informations_ko = bank_informations.get("ko", 0)

    bank_information_status = serialization.OffererBankInformationStatus(
        ok=bank_informations_ok, ko=bank_informations_ko
    )
    if not edit_offerer_form:
        edit_offerer_form = offerer_forms.EditOffererForm(
            name=offerer.name,
            postal_address_autocomplete=f"{offerer.address}, {offerer.postalCode} {offerer.city}"
            if offerer.address is not None and offerer.city is not None and offerer.postalCode is not None
            else None,
            city=offerer.city,
            postal_code=offerer.postalCode,
            address=offerer.address,
            tags=offerer.tags,
        )

    return render_template(
        "offerer/get.html",
        offerer=offerer,
        region=regions_utils.get_region_name_from_postal_code(offerer.postalCode),
        bank_information_status=bank_information_status,
        edit_offerer_form=edit_offerer_form,
        suspension_form=offerer_forms.SuspendOffererForm(),
        delete_offerer_form=empty_forms.EmptyForm(),
        active_tab=request.args.get("active_tab", "history"),
    )


@offerer_blueprint.route("", methods=["GET"])
def get(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)
    return render_offerer_details(offerer)


def get_stats_data(offerer_id: int) -> serialization.OfferersStats:
    offers_stats = offerers_api.get_offerer_offers_stats(offerer_id)
    stats = serialization.OffersStats(
        active=serialization.BaseOffersStats(
            individual=offers_stats.individual_offers.get("active", 0) if offers_stats.individual_offers else 0,
            collective=offers_stats.collective_offers.get("active", 0) if offers_stats.collective_offers else 0,
        ),
        inactive=serialization.BaseOffersStats(
            individual=offers_stats.individual_offers.get("inactive", 0) if offers_stats.individual_offers else 0,
            collective=offers_stats.collective_offers.get("inactive", 0) if offers_stats.collective_offers else 0,
        ),
    )

    total_revenue = offerers_api.get_offerer_total_revenue(offerer_id)

    return serialization.OfferersStats(stats=stats, total_revenue=total_revenue)


@offerer_blueprint.route("/stats", methods=["GET"])
def get_stats(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)
    data = get_stats_data(offerer.id)
    return render_template(
        "offerer/get/stats.html",
        stats=data.stats,
        total_revenue=data.total_revenue,
    )


@offerer_blueprint.route("/suspend", methods=["POST"])
@utils.permission_required(perm_models.Permissions.FRAUD_ACTIONS)
def suspend_offerer(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)
    form = offerer_forms.SuspendOffererForm()

    if not form.validate():
        flash("Les données envoyées comportent des erreurs", "warning")
    else:
        try:
            offerers_api.suspend_offerer(offerer, current_user, form.comment.data)
        except offerers_exceptions.CannotSuspendOffererWithBookingsException:
            flash("Impossible de suspendre une structure juridique pour laquelle il existe des réservations", "warning")
        else:
            flash(f"La structure {offerer.name} ({offerer_id}) a été suspendue", "success")

    return redirect(url_for("backoffice_v3_web.offerer.get", offerer_id=offerer.id), code=303)


@offerer_blueprint.route("/unsuspend", methods=["POST"])
@utils.permission_required(perm_models.Permissions.FRAUD_ACTIONS)
def unsuspend_offerer(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)
    form = offerer_forms.SuspendOffererForm()

    if not form.validate():
        flash("Les données envoyées comportent des erreurs", "warning")
    else:
        offerers_api.unsuspend_offerer(offerer, current_user, form.comment.data)
        flash(f"La structure {offerer.name} ({offerer_id}) a été réactivée", "success")

    return redirect(url_for("backoffice_v3_web.offerer.get", offerer_id=offerer.id), code=303)


@offerer_blueprint.route("/delete", methods=["POST"])
@utils.permission_required(perm_models.Permissions.DELETE_PRO_ENTITY)
def delete_offerer(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)
    offerer_name = offerer.name

    # Get users to update before association info is deleted
    # joined user is no longer available after delete_model()
    emails = offerers_repository.get_emails_by_offerer(offerer)

    try:
        delete_cascade_offerer_by_id(offerer.id)
    except offerers_exceptions.CannotDeleteOffererWithBookingsException:
        flash("Impossible d'effacer une structure juridique pour laquelle il existe des réservations", "warning")
        return redirect(url_for("backoffice_v3_web.offerer.get", offerer_id=offerer.id), code=303)

    for email in emails:
        external_attributes_api.update_external_pro(email)

    flash(f"La structure {offerer_name} ({offerer_id}) a été supprimée", "success")
    return redirect(url_for("backoffice_v3_web.search_pro"), code=303)


@offerer_blueprint.route("/update", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def update_offerer(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)
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
        return render_offerer_details(offerer=offerer, edit_offerer_form=form), 400

    modified_info = offerers_api.update_offerer(
        offerer,
        name=form.name.data,
        city=form.city.data,
        postal_code=form.postal_code.data,
        address=form.address.data,
        tags=form.tags.data,
    )

    if modified_info:
        history_api.log_action(
            history_models.ActionType.INFO_MODIFIED,
            current_user,
            offerer=offerer,
            modified_info=modified_info,
        )

    flash("Informations mises à jour", "success")
    return redirect(url_for("backoffice_v3_web.offerer.get", offerer_id=offerer.id), code=303)


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
        dst=url_for("backoffice_v3_web.offerer.comment_offerer", offerer_id=offerer_id),
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
                history_models.ActionHistory.offererId == offerer_id, history_models.ActionHistory.userId.isnot(None)
            )
        )
        .distinct()
        .subquery()
    )

    rows = (
        db.session.query(
            users_models.User.id,
            users_models.User.firstName,
            users_models.User.lastName,
            users_models.User.full_name,
            users_models.User.email,
            offerers_models.UserOfferer,
        )
        .select_from(users_models.User)
        .outerjoin(
            offerers_models.UserOfferer,
            sa.and_(
                offerers_models.UserOfferer.userId == users_models.User.id,
                offerers_models.UserOfferer.offererId == offerer_id,
            ),
        )
        .filter(users_models.User.id.in_(user_ids_subquery))
        .order_by(offerers_models.UserOfferer.id, users_models.User.full_name)
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
                        "backoffice_v3_web.offerer.add_user_offerer_and_validate", offerer_id=offerer_id
                    ),
                }
            )

    return render_template(
        "offerer/get/details/users.html",
        rows=[row for row in rows if row.UserOfferer is not None],
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
            "backoffice_v3_web.offerer.delete_user_offerer", offerer_id=offerer_id, user_offerer_id=user_offerer.id
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
        offerers_models.UserOfferer.query.options(
            sa.orm.joinedload(offerers_models.UserOfferer.offerer).load_only(
                offerers_models.Offerer.id,
                offerers_models.Offerer.name,
            ),
            sa.orm.joinedload(offerers_models.UserOfferer.user).load_only(users_models.User.email),
        )
        .filter_by(id=user_offerer_id)
        .one_or_none()
    )
    if not user_offerer:
        raise NotFound()

    form = offerer_forms.OptionalCommentForm()
    if not form.validate():
        flash("Les données envoyées comportent des erreurs", "warning")
        return _redirect_after_user_offerer_validation_action(offerer_id)
    user_email = user_offerer.user.email
    offerer_name = user_offerer.offerer.name

    offerers_api.delete_offerer_attachment(user_offerer, current_user, form.comment.data)

    flash(
        f"Le rattachement de {user_email} à la structure {offerer_name} a été supprimé",
        "success",
    )
    return _redirect_after_user_offerer_validation_action(offerer_id)


@offerer_blueprint.route("/venues", methods=["GET"])
def get_managed_venues(offerer_id: int) -> utils.BackofficeResponse:
    venues = (
        offerers_models.Venue.query.filter_by(managingOffererId=offerer_id)
        .options(
            sa.orm.load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.siret,
                offerers_models.Venue.venueTypeCode,
                offerers_models.Venue.isVirtual,
                offerers_models.Venue.managingOffererId,
            ),
            sa.orm.joinedload(offerers_models.Venue.collectiveDmsApplications).load_only(
                educational_models.CollectiveDmsApplication.state,
                educational_models.CollectiveDmsApplication.lastChangeDate,
            ),
            sa.orm.joinedload(offerers_models.Venue.registration).load_only(
                offerers_models.VenueRegistration.target,
                offerers_models.VenueRegistration.webPresence,
            ),
        )
        .all()
    )

    return render_template(
        "offerer/get/details/managed_venues.html",
        venues=venues,
    )


@offerer_blueprint.route("/comment", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def comment_offerer(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)

    form = offerer_forms.CommentForm()
    if not form.validate():
        flash("Les données envoyées comportent des erreurs", "warning")
    else:
        offerers_api.add_comment_to_offerer(offerer, current_user, comment=form.comment.data)
        flash("Commentaire enregistré", "success")

    return redirect(url_for("backoffice_v3_web.offerer.get", offerer_id=offerer_id), code=303)


validation_blueprint = utils.child_backoffice_blueprint(
    "validation",
    __name__,
    url_prefix="/pro/validation",
    permission=perm_models.Permissions.VALIDATE_OFFERER,
)


def _redirect_after_offerer_validation_action(code: int = 303) -> utils.BackofficeResponse:
    if request.referrer:
        return redirect(request.referrer, code)

    return redirect(url_for("backoffice_v3_web.validation.list_offerers_to_validate"), code)


@validation_blueprint.route("/offerer", methods=["GET"])
def list_offerers_to_validate() -> utils.BackofficeResponse:
    stats = offerers_api.count_offerers_by_validation_status()

    form = offerer_forms.OffererValidationListForm(formdata=utils.get_query_params())
    if not form.validate():
        return render_template("offerer/validation.html", rows=[], form=form, stats=stats), 400

    # new and pending attachements by default
    if not form.status.data:
        form.status.data = [ValidationStatus.NEW.value, ValidationStatus.PENDING.value]

    offerers = offerers_api.list_offerers_to_be_validated(
        form.q.data,
        form.regions.data,
        form.tags.data,
        form.status.data,
        form.dms_adage_status.data,
        date_utils.date_to_localized_datetime(form.from_date.data, datetime.datetime.min.time()),
        date_utils.date_to_localized_datetime(form.to_date.data, datetime.datetime.max.time()),
    )

    sorted_offerers: BaseQuery = offerers.order_by(
        getattr(getattr(offerers_models.Offerer, form.sort.data), form.order.data)()
    )

    paginated_offerers = sorted_offerers.paginate(
        page=int(form.data["page"]),
        per_page=int(form.data["per_page"]),
    )

    form_url = partial(url_for, ".list_offerers_to_validate", **form.raw_data)
    next_pages_urls = search_utils.pagination_links(form_url, int(form.data["page"]), paginated_offerers.pages)

    date_created_sort_url = form_url(
        sort="dateCreated", order="desc" if form.sort.data == "dateCreated" and form.order.data == "asc" else "asc"
    )

    form.page.data = 1  # Reset to first page when form is submitted ("Appliquer" clicked)

    return render_template(
        "offerer/validation.html",
        rows=paginated_offerers,
        form=form,
        next_pages_urls=next_pages_urls,
        date_created_sort_url=date_created_sort_url,
        stats=stats,
    )


@validation_blueprint.route("/offerer/<int:offerer_id>/validate", methods=["POST"])
def validate_offerer(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)

    try:
        offerers_api.validate_offerer(offerer, current_user)
    except offerers_exceptions.OffererAlreadyValidatedException:
        flash(f"La structure {offerer.name} est déjà validée", "warning")
        return _redirect_after_offerer_validation_action()

    flash(f"La structure {offerer.name} a été validée", "success")
    return _redirect_after_offerer_validation_action()


@validation_blueprint.route("/offerer/<int:offerer_id>/reject", methods=["GET"])
def get_reject_offerer_form(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)

    form = offerer_forms.OptionalCommentForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_v3_web.validation.reject_offerer", offerer_id=offerer.id),
        div_id=f"reject-modal-{offerer.id}",  # must be consistent with parameter passed to build_lazy_modal
        title=f"Rejeter la structure la structure {offerer.name.upper()}",
        button_text="Rejeter la structure",
    )


@validation_blueprint.route("/offerer/<int:offerer_id>/reject", methods=["POST"])
def reject_offerer(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)

    form = offerer_forms.OptionalCommentForm()
    if not form.validate():
        flash("Les données envoyées comportent des erreurs", "warning")
        return _redirect_after_offerer_validation_action()

    try:
        offerers_api.reject_offerer(offerer, current_user, comment=form.comment.data)
    except offerers_exceptions.OffererAlreadyRejectedException:
        flash(f"La structure {offerer.name} est déjà rejetée", "warning")
        return _redirect_after_offerer_validation_action()

    flash(f"La structure {offerer.name} a été rejetée", "success")
    return _redirect_after_offerer_validation_action()


@validation_blueprint.route("/offerer/<int:offerer_id>/pending", methods=["GET"])
def get_offerer_pending_form(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)

    form = offerer_forms.CommentAndTagOffererForm(tags=filter_homologation_tags(offerer.tags))

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_v3_web.validation.set_offerer_pending", offerer_id=offerer.id),
        div_id=f"pending-modal-{offerer.id}",  # must be consistent with parameter passed to build_lazy_modal
        title=f"Mettre en attente la structure {offerer.name.upper()}",
        button_text="Mettre en attente",
    )


@validation_blueprint.route("/offerer/<int:offerer_id>/pending", methods=["POST"])
def set_offerer_pending(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)

    form = offerer_forms.CommentAndTagOffererForm()
    if not form.validate():
        flash("Les données envoyées comportent des erreurs", "warning")
        return _redirect_after_offerer_validation_action()

    # Don't pass directly form.tags.data to set_offerer_pending() because this would remove non-homologation tags
    saved_homologation_tags = set(filter_homologation_tags(offerer.tags))
    tags_to_add = set(form.tags.data) - saved_homologation_tags
    tags_to_remove = saved_homologation_tags - set(form.tags.data)

    offerers_api.set_offerer_pending(
        offerer, current_user, comment=form.comment.data, tags_to_add=tags_to_add, tags_to_remove=tags_to_remove
    )

    flash(f"La structure {offerer.name} a été mise en attente", "success")
    return _redirect_after_offerer_validation_action()


@validation_blueprint.route("/offerer/<int:offerer_id>/top-actor", methods=["POST"])
def toggle_top_actor(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)

    try:
        tag = offerers_models.OffererTag.query.filter(offerers_models.OffererTag.name == "top-acteur").one()
    except sa.exc.NoResultFound:
        flash("Le tag top-acteur n'existe pas", "warning")
        return _redirect_after_offerer_validation_action()

    form = offerer_forms.TopActorForm()
    if not form.validate():
        flash("Les données envoyées comportent des erreurs", "warning")
        return _redirect_after_offerer_validation_action()

    if form.is_top_actor.data and form.is_top_actor.data == "on":
        # Associate the tag with offerer
        try:
            db.session.add(offerers_models.OffererTagMapping(offererId=offerer.id, tagId=tag.id))
            db.session.commit()
        except sa.exc.IntegrityError:
            # Already in database
            db.session.rollback()
    else:
        # Remove the tag from offerer
        offerers_models.OffererTagMapping.query.filter(
            offerers_models.OffererTagMapping.offererId == offerer.id,
            offerers_models.OffererTagMapping.tagId == tag.id,
        ).delete()
        db.session.commit()

    return _redirect_after_offerer_validation_action()


def _offerer_batch_action(
    api_function: typing.Callable,
    success_message: str,
    form_class: typing.Callable,
) -> utils.BackofficeResponse:
    form = form_class()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _redirect_after_offerer_validation_action()

    offerers = offerers_models.Offerer.query.filter(offerers_models.Offerer.id.in_(form.object_ids_list)).all()

    if hasattr(form, "tags"):
        tags = form.tags.data
        previous_tags = list(reduce(set.intersection, [set(offerer.tags) for offerer in offerers]))  # type: ignore
        deleted_tags = list(set(previous_tags).difference(list(set(tags))))

    for offerer in offerers:
        kwargs = {}
        if hasattr(form, "tags"):
            kwargs["tags_to_add"] = form.tags.data
            kwargs["tags_to_remove"] = deleted_tags
        if hasattr(form, "comment"):
            kwargs["comment"] = form.comment.data

        api_function(offerer, current_user, **kwargs)

    flash(success_message, "success")

    return _redirect_after_offerer_validation_action()


@validation_blueprint.route("/offerer/batch-validate", methods=["POST"])
def batch_validate_offerer() -> utils.BackofficeResponse:
    try:
        return _offerer_batch_action(
            offerers_api.validate_offerer,
            "Les structures sélectionnées ont été validées avec succès",
            offerer_forms.BatchForm,
        )
    except offerers_exceptions.OffererAlreadyValidatedException:
        flash("Au moins une des structures a déjà été validée", "error")
        return _redirect_after_offerer_validation_action()


@validation_blueprint.route("/offerer/batch-pending-form", methods=["GET", "POST"])
def get_batch_offerer_pending_form() -> utils.BackofficeResponse:
    form = offerer_forms.BatchCommentAndTagOffererForm()
    if form.object_ids.data:
        if not form.validate():
            flash(utils.build_form_error_msg(form), "warning")
            return _redirect_after_offerer_validation_action()

        offerers = (
            offerers_models.Offerer.query.filter(offerers_models.Offerer.id.in_(form.object_ids_list))
            .options(
                sa.orm.load_only(offerers_models.Offerer.id),
                sa.orm.joinedload(offerers_models.Offerer.tags).load_only(
                    offerers_models.OffererTag.id, offerers_models.OffererTag.label
                ),
            )
            .all()
        )
        tags = list(reduce(set.intersection, [set(offerer.tags) for offerer in offerers]))  # type: ignore

        if len(tags) > 0:
            form.tags.data = tags

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_v3_web.validation.batch_set_offerer_pending"),
        div_id="batch-pending-modal",
        title="Mettre en attente les structures",
        button_text="Mettre en attente les structures",
    )


@validation_blueprint.route("/offerer/batch-pending", methods=["POST"])
def batch_set_offerer_pending() -> utils.BackofficeResponse:
    return _offerer_batch_action(
        offerers_api.set_offerer_pending,
        "Les structures ont été mises en attente avec succès",
        offerer_forms.BatchCommentAndTagOffererForm,
    )


@validation_blueprint.route("/offerer/batch-reject-form", methods=["GET"])
def get_batch_reject_offerer_form() -> utils.BackofficeResponse:
    form = offerer_forms.BatchOptionalCommentForm()
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_v3_web.validation.batch_reject_offerer"),
        div_id="batch-reject-modal",
        title="Rejeter les structures",
        button_text="Rejeter les structures",
    )


@validation_blueprint.route("/offerer/batch-reject", methods=["POST"])
def batch_reject_offerer() -> utils.BackofficeResponse:
    try:
        return _offerer_batch_action(
            offerers_api.reject_offerer,
            "Les structures sélectionnées ont été rejetées avec succès",
            offerer_forms.BatchOptionalCommentForm,
        )
    except offerers_exceptions.OffererAlreadyRejectedException:
        flash("Une des structures a déjà été rejetée", "error")
        return _redirect_after_offerer_validation_action()


# #
# USER OFFERER
# #


def _get_serialized_user_offerer_last_comment(
    offerer: offerers_models.Offerer, user_id: int | None = None
) -> str | None:
    last = max(
        (
            action
            for action in offerer.action_history
            if bool(action.comment)
            and action.userId == user_id
            and action.actionType
            in (
                history_models.ActionType.USER_OFFERER_NEW,
                history_models.ActionType.USER_OFFERER_PENDING,
                history_models.ActionType.USER_OFFERER_VALIDATED,
                history_models.ActionType.USER_OFFERER_REJECTED,
                history_models.ActionType.COMMENT,
            )
        ),
        key=lambda action: action.actionDate,
        default=None,
    )
    if last is not None:
        return last.comment

    return None


@validation_blueprint.route("/user-offerer", methods=["GET"])
def list_offerers_attachments_to_validate() -> utils.BackofficeResponse:
    form = offerer_forms.UserOffererValidationListForm(formdata=utils.get_query_params())
    if not form.validate():
        return render_template("offerer/user_offerer_validation.html", rows=[], form=form), 400

    # new and pending attachements by default
    if not form.status.data:
        form.status.data = [ValidationStatus.NEW.value, ValidationStatus.PENDING.value]

    users_offerers = offerers_api.list_users_offerers_to_be_validated(
        form.q.data,
        form.regions.data,
        form.tags.data,
        form.status.data,
        form.offerer_status.data,
        date_utils.date_to_localized_datetime(form.from_date.data, datetime.datetime.min.time()),
        date_utils.date_to_localized_datetime(form.to_date.data, datetime.datetime.max.time()),
    )

    sorted_users_offerers: BaseQuery = users_offerers.order_by(
        getattr(getattr(offerers_models.UserOfferer, form.sort.data), form.order.data)()
    )

    paginated_users_offerers = sorted_users_offerers.paginate(
        page=int(form.data["page"]),
        per_page=int(form.data["per_page"]),
    )

    form_url = partial(url_for, ".list_offerers_attachments_to_validate", **form.raw_data)
    next_pages_urls = search_utils.pagination_links(form_url, int(form.data["page"]), paginated_users_offerers.pages)

    date_created_sort_url = form_url(
        sort="dateCreated", order="desc" if form.sort.data == "dateCreated" and form.order.data == "asc" else "asc"
    )

    form.page.data = 1  # Reset to first page when form is submitted ("Appliquer" clicked)

    return render_template(
        "offerer/user_offerer_validation.html",
        rows=paginated_users_offerers,
        form=form,
        next_pages_urls=next_pages_urls,
        get_last_comment_func=_get_serialized_user_offerer_last_comment,
        date_created_sort_url=date_created_sort_url,
    )


def _redirect_after_user_offerer_validation_action(offerer_id: int, code: int = 303) -> utils.BackofficeResponse:
    dst_url = url_for("backoffice_v3_web.offerer.get", offerer_id=offerer_id, active_tab="users")

    if request.referrer:
        referrer_path = urlparse(request.referrer).path
        dst_path = urlparse(dst_url).path

        if referrer_path != dst_path:
            return redirect(request.referrer, code)

    return redirect(dst_url + "#offerer_details_frame", code=code)


def _redirect_after_user_offerer_validation_action_list(code: int = 303) -> utils.BackofficeResponse:
    if request.referrer:
        return redirect(request.referrer, code)

    return redirect(url_for("backoffice_v3_web.validation.list_offerers_attachments_to_validate"), code)


user_offerer_blueprint = utils.child_backoffice_blueprint(
    "user_offerer",
    __name__,
    url_prefix="/pro/user_offerer/<int:user_offerer_id>",
    permission=perm_models.Permissions.VALIDATE_OFFERER,
)


@validation_blueprint.route("/user-offerer/<int:user_offerer_id>/validate", methods=["POST"])
def validate_user_offerer(user_offerer_id: int) -> utils.BackofficeResponse:
    user_offerer = offerers_models.UserOfferer.query.filter_by(id=user_offerer_id).one_or_none()
    if not user_offerer:
        raise NotFound()

    try:
        offerers_api.validate_offerer_attachment(user_offerer, current_user)
    except offerers_exceptions.UserOffererAlreadyValidatedException:
        flash(
            f"Le rattachement de {user_offerer.user.email} à la structure {user_offerer.offerer.name} est déjà validé",
            "warning",
        )
        return _redirect_after_user_offerer_validation_action(user_offerer.offerer.id)

    flash(
        f"Le rattachement de {user_offerer.user.email} à la structure {user_offerer.offerer.name} a été validé",
        "success",
    )
    return _redirect_after_user_offerer_validation_action(user_offerer.offerer.id)


@validation_blueprint.route("/user-offerer/batch-reject", methods=["GET"])
def get_batch_reject_user_offerer_form() -> utils.BackofficeResponse:
    form = offerer_forms.BatchOptionalCommentForm()
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_v3_web.validation.batch_reject_user_offerer"),
        div_id="batch-reject-modal",
        title="Rejeter le rattachement",
        button_text="Rejeter le rattachement",
    )


@validation_blueprint.route("/user-offerer/batch-pending", methods=["GET"])
def get_batch_user_offerer_pending_form() -> utils.BackofficeResponse:
    form = offerer_forms.BatchOptionalCommentForm()
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_v3_web.validation.batch_set_user_offerer_pending"),
        div_id="batch-pending-modal",
        title="Mettre en attente le rattachement",
        button_text="Mettre en attente le rattachement",
    )


@validation_blueprint.route("/user-offerer/<int:user_offerer_id>/reject", methods=["GET"])
def get_reject_user_offerer_form(user_offerer_id: int) -> utils.BackofficeResponse:
    user_offerer = offerers_models.UserOfferer.query.filter_by(id=user_offerer_id).one_or_none()
    if not user_offerer:
        raise NotFound()

    form = offerer_forms.OptionalCommentForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_v3_web.validation.reject_user_offerer", user_offerer_id=user_offerer.id),
        div_id=f"reject-modal-{user_offerer.id}",  # must be consistent with parameter passed to build_lazy_modal
        title=f"Rejeter le rattachement à {user_offerer.offerer.name.upper()}",
        button_text="Rejeter le rattachement",
    )


@validation_blueprint.route("/user-offerer/<int:user_offerer_id>/reject", methods=["POST"])
def reject_user_offerer(user_offerer_id: int) -> utils.BackofficeResponse:
    user_offerer = offerers_models.UserOfferer.query.filter_by(id=user_offerer_id).one_or_none()
    if not user_offerer:
        raise NotFound()

    form = offerer_forms.OptionalCommentForm()
    if not form.validate():
        flash("Les données envoyées comportent des erreurs", "warning")
        return _redirect_after_user_offerer_validation_action(user_offerer.offerer.id)

    offerers_api.reject_offerer_attachment(user_offerer, current_user, form.comment.data)

    flash(
        f"Le rattachement de {user_offerer.user.email} à la structure {user_offerer.offerer.name} a été rejeté",
        "success",
    )
    return _redirect_after_user_offerer_validation_action(user_offerer.offerer.id)


@validation_blueprint.route("/user-offerer/<int:user_offerer_id>/pending", methods=["GET"])
def get_user_offerer_pending_form(user_offerer_id: int) -> utils.BackofficeResponse:
    user_offerer = offerers_models.UserOfferer.query.filter_by(id=user_offerer_id).one_or_none()
    if not user_offerer:
        raise NotFound()

    form = offerer_forms.OptionalCommentForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_v3_web.validation.set_user_offerer_pending", user_offerer_id=user_offerer.id),
        div_id=f"pending-modal-{user_offerer.id}",  # must be consistent with parameter passed to build_lazy_modal
        title=f"Mettre en attente le rattachement à {user_offerer.offerer.name.upper()}",
        button_text="Mettre en attente le rattachement",
    )


@validation_blueprint.route("/user-offerer/<int:user_offerer_id>/pending", methods=["POST"])
def set_user_offerer_pending(user_offerer_id: int) -> utils.BackofficeResponse:
    user_offerer = offerers_models.UserOfferer.query.filter_by(id=user_offerer_id).one_or_none()
    if not user_offerer:
        raise NotFound()

    form = offerer_forms.OptionalCommentForm()
    if not form.validate():
        flash("Les données envoyées comportent des erreurs", "warning")
        return _redirect_after_user_offerer_validation_action(user_offerer.offerer.id)

    offerers_api.set_offerer_attachment_pending(user_offerer, current_user, form.comment.data)
    flash(
        f"Le rattachement de {user_offerer.user.email} à la structure {user_offerer.offerer.name} a été mis en attente",
        "success",
    )

    return _redirect_after_user_offerer_validation_action(user_offerer.offerer.id)


@offerer_blueprint.route("/add-user", methods=["POST"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def add_user_offerer_and_validate(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)

    form = offerer_forms.AddProUserForm()
    if not form.validate():
        flash("Les données envoyées comportent des erreurs", "warning")
        return _redirect_after_user_offerer_validation_action(offerer.id)

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
        return _redirect_after_user_offerer_validation_action(offerer.id)

    new_user_offerer = offerers_models.UserOfferer(offerer=offerer, user=user, validationStatus=ValidationStatus.NEW)
    offerers_api.validate_offerer_attachment(new_user_offerer, current_user, form.comment.data)

    flash(f"Le rattachement de {user.email} à la structure {offerer.name} a été ajouté", "success")
    return _redirect_after_user_offerer_validation_action(offerer.id)


def _user_offerer_batch_action(
    api_function: typing.Callable[[offerers_models.UserOfferer, users_models.User, str | None], None],
    success_message: str,
) -> utils.BackofficeResponse:
    form = offerer_forms.BatchOptionalCommentForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _redirect_after_user_offerer_validation_action_list()

    user_offerers = offerers_models.UserOfferer.query.filter(
        offerers_models.UserOfferer.id.in_(form.object_ids_list)
    ).all()

    for user_offerer in user_offerers:
        api_function(user_offerer, current_user, form.comment.data)
    flash(success_message, "success")

    return _redirect_after_user_offerer_validation_action_list()


@validation_blueprint.route("/user-offerer/batch-pending", methods=["POST"])
def batch_set_user_offerer_pending() -> utils.BackofficeResponse:
    return _user_offerer_batch_action(
        offerers_api.set_offerer_attachment_pending, "Les rattachements ont été mis en attente avec succès"
    )


@validation_blueprint.route("/user-offerer/batch-reject", methods=["POST"])
def batch_reject_user_offerer() -> utils.BackofficeResponse:
    try:
        return _user_offerer_batch_action(
            offerers_api.reject_offerer_attachment, "Les rattachements sélectionnés ont été rejetés avec succès"
        )
    except offerers_exceptions.UserOffererAlreadyValidatedException:
        flash("Au moins un des rattachements est déjà rejeté", "error")
        return _redirect_after_user_offerer_validation_action_list()


@validation_blueprint.route("/user-offerer/batch-validate", methods=["POST"])
def batch_validate_user_offerer() -> utils.BackofficeResponse:
    try:
        return _user_offerer_batch_action(
            offerers_api.validate_offerer_attachment, "Les rattachements sélectionnés ont été validés avec succès"
        )
    except offerers_exceptions.UserOffererAlreadyValidatedException:
        flash("Au moins un des rattachements est déjà validé", "warning")
        return _redirect_after_user_offerer_validation_action_list()


# #
# OFFERER TAG
# #

offerer_tag_blueprint = utils.child_backoffice_blueprint(
    "offerer_tag",
    __name__,
    url_prefix="/pro/offerer-tag",
    permission=perm_models.Permissions.MANAGE_OFFERER_TAG,
)


@offerer_tag_blueprint.route("", methods=["GET"])
def list_offerer_tags() -> utils.BackofficeResponse:
    categories = get_offerer_tag_categories()
    offerer_tags = offerers_models.OffererTag.query.order_by(offerers_models.OffererTag.name).all()
    forms = {}
    for offerer_tag in offerer_tags:
        forms[offerer_tag.id] = offerer_forms.EditOffererTagForm(
            name=offerer_tag.name,
            label=offerer_tag.label,
            description=offerer_tag.description,
        )
        forms[offerer_tag.id].categories.choices = [(cat.id, cat.label or cat.name) for cat in categories]
        forms[offerer_tag.id].categories.data = [cat.id for cat in offerer_tag.categories]

    create_tag_form = offerer_forms.EditOffererTagForm()
    create_tag_form.categories.choices = [(cat.id, cat.label or cat.name) for cat in categories]

    return render_template(
        "offerer/offerer_tag.html",
        rows=offerer_tags,
        forms=forms,
        create_tag_form=create_tag_form,
        delete_tag_form=empty_forms.EmptyForm(),
    )


@offerer_tag_blueprint.route("/<int:offerer_tag_id>/update", methods=["POST"])
def update_offerer_tag(offerer_tag_id: int) -> utils.BackofficeResponse:
    categories = get_offerer_tag_categories()
    offerer_tag_to_update = offerers_models.OffererTag.query.get_or_404(offerer_tag_id)
    form = offerer_forms.EditOffererTagForm()
    form.categories.choices = [(cat.id, cat.label or cat.name) for cat in categories]

    if not form.validate():
        error_msg = utils.build_form_error_msg(form)
        flash(error_msg, "warning")
        return redirect(url_for("backoffice_v3_web.offerer_tag.list_offerer_tags"), code=303)

    new_categories = [cat for cat in categories if cat.id in form.categories.data]
    try:
        offerers_api.update_offerer_tag(
            offerer_tag_to_update,
            name=form.name.data,
            label=form.label.data,
            description=form.description.data,
            categories=new_categories,
        )
        flash("Informations mises à jour", "success")
    except sa.exc.IntegrityError:
        db.session.rollback()
        flash("Ce nom de tag existe déjà", "warning")

    return redirect(url_for("backoffice_v3_web.offerer_tag.list_offerer_tags"), code=303)


@offerer_tag_blueprint.route("/create", methods=["POST"])
def create_offerer_tag() -> utils.BackofficeResponse:
    categories = get_offerer_tag_categories()
    form = offerer_forms.EditOffererTagForm()
    form.categories.choices = [(cat.id, cat.label) for cat in categories]

    if not form.validate():
        error_msg = utils.build_form_error_msg(form)
        flash(error_msg, "warning")
        return redirect(url_for("backoffice_v3_web.offerer_tag.list_offerer_tags"), code=303)

    new_categories = [cat for cat in categories if cat.id in form.categories.data]
    try:
        tag = offerers_models.OffererTag(
            name=form.name.data,
            label=form.label.data,
            description=form.description.data,
            categories=new_categories,
        )
        db.session.add(tag)
        db.session.commit()
        flash("Tag structure créé", "success")

    except sa.exc.IntegrityError:
        db.session.rollback()
        flash("Ce tag existe déjà", "warning")

    return redirect(url_for("backoffice_v3_web.offerer_tag.list_offerer_tags"), code=303)


def get_offerer_tag_categories() -> list[offerers_models.OffererTagCategory]:
    return offerers_models.OffererTagCategory.query.order_by(offerers_models.OffererTagCategory.label).all()


@offerer_tag_blueprint.route("/<int:offerer_tag_id>/delete", methods=["POST"])
@utils.permission_required(perm_models.Permissions.DELETE_OFFERER_TAG)
def delete_offerer_tag(offerer_tag_id: int) -> utils.BackofficeResponse:
    offerer_tag_to_delete = offerers_models.OffererTag.query.get_or_404(offerer_tag_id)

    try:
        db.session.delete(offerer_tag_to_delete)
        db.session.commit()
    except sa.exc.DBAPIError as exception:
        db.session.rollback()
        flash(f"Une erreur s'est produite : {str(exception)}", "warning")

    return redirect(url_for("backoffice_v3_web.offerer_tag.list_offerer_tags"), code=303)
