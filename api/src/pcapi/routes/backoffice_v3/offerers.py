from dataclasses import dataclass
import datetime
from functools import partial
import typing
from urllib.parse import urlparse

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
import sqlalchemy as sa
from werkzeug.exceptions import NotFound

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
from .filters import filter_homologation_tags
from .forms import empty as empty_forms
from .forms import offerer as offerer_forms
from .serialization import offerers as serialization


offerer_blueprint = utils.child_backoffice_blueprint(
    "offerer",
    __name__,
    url_prefix="/pro/offerer/<int:offerer_id>",
    permission=perm_models.Permissions.READ_PRO_ENTITY,
)


def render_offerer_details(
    offerer: offerers_models.Offerer, edit_offerer_form: offerer_forms.EditOffererForm | None = None
) -> utils.BackofficeResponse:
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
            postal_address_autocomplete=f"{offerer.address}, {offerer.postalCode} {offerer.city}"
            if offerer.address is not None and offerer.city is not None and offerer.postalCode is not None
            else None,
            city=offerer.city,
            postal_code=offerer.postalCode,
            address=offerer.address,
            tags=offerer.tags,
        )

    delete_offerer_form = empty_forms.EmptyForm()

    return render_template(
        "offerer/get.html",
        offerer=offerer,
        region=regions_utils.get_region_name_from_postal_code(offerer.postalCode),
        bank_information_status=bank_information_status,
        edit_offerer_form=edit_offerer_form,
        delete_offerer_form=delete_offerer_form,
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


def get_offerer_history_data(offerer: offerers_models.Offerer) -> typing.Sequence[history_models.ActionHistory]:
    # this should not be necessary but in case there is a huge amount
    # of actions, it is safer to set a limit
    max_actions_count = 50

    actions = sorted(offerer.action_history, key=lambda action: action.actionDate, reverse=True)
    return actions[:max_actions_count]


def get_offerer(offerer_id: int) -> offerers_models.Offerer:
    offerer = (
        offerers_models.Offerer.query.filter_by(id=offerer_id)
        .options(
            sa.orm.joinedload(offerers_models.Offerer.UserOfferers).joinedload(offerers_models.UserOfferer.user),
        )
        .options(
            sa.orm.joinedload(offerers_models.Offerer.action_history).joinedload(history_models.ActionHistory.user),
            sa.orm.joinedload(offerers_models.Offerer.action_history).joinedload(
                history_models.ActionHistory.authorUser
            ),
        )
        .one_or_none()
    )

    if not offerer:
        raise NotFound()

    return offerer


def _get_add_pro_user_form(offerer: offerers_models.Offerer) -> offerer_forms.AddProUserForm:
    # Users whose association to the offerer has been removed, for which relationship is only from history
    removed_users = sorted(
        {action.user for action in offerer.action_history if action.user} - {uo.user for uo in offerer.UserOfferers},
        key=lambda user: user.full_name,
    )

    form = offerer_forms.AddProUserForm()
    form.pro_user_id.choices = [(user.id, f"{user.full_name} ({user.id})") for user in removed_users]

    return form


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
        return render_offerer_details(offerer=offerer, edit_offerer_form=form)

    modified_info = offerers_api.update_offerer(
        offerer,
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


@offerer_blueprint.route("/details", methods=["GET"])
def get_details(offerer_id: int) -> utils.BackofficeResponse:
    offerer = get_offerer(offerer_id)

    history = get_offerer_history_data(offerer)

    form = offerer_forms.CommentForm()
    dst = url_for("backoffice_v3_web.offerer.comment_offerer", offerer_id=offerer.id)

    can_add_user = utils.has_current_user_permission(perm_models.Permissions.VALIDATE_OFFERER)
    add_user_form = _get_add_pro_user_form(offerer) if can_add_user else None
    add_user_dst = url_for("backoffice_v3_web.offerer.add_user_offerer_and_validate", offerer_id=offerer.id)

    return render_template(
        "offerer/get/details.html",
        offerer=offerer,
        actions=history,
        dst=dst,
        form=form,
        users_offerer=offerer.UserOfferers,
        active_tab=request.args.get("active_tab", "history"),
        add_user_dst=add_user_dst,
        add_user_form=add_user_form,
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


def _get_serialized_last_comment(
    action_types: typing.Collection[history_models.ActionType],
    offerer: offerers_models.Offerer,
    user_id: int | None = None,
) -> str | None:
    last = max(
        (
            action
            for action in offerer.action_history
            if bool(action.comment)
            and (user_id is None or action.userId == user_id)
            and action.actionType in action_types
        ),
        key=lambda action: action.actionDate,
        default=None,
    )
    if last is not None:
        return last.comment

    return None


def _get_serialized_offerer_last_comment(offerer: offerers_models.Offerer, user_id: int | None = None) -> str | None:
    return _get_serialized_last_comment(
        (
            history_models.ActionType.OFFERER_NEW,
            history_models.ActionType.OFFERER_PENDING,
            history_models.ActionType.OFFERER_VALIDATED,
            history_models.ActionType.OFFERER_REJECTED,
            history_models.ActionType.COMMENT,
        ),
        offerer,
        user_id=user_id,
    )


def _redirect_after_offerer_validation_action(code: int = 303) -> utils.BackofficeResponse:
    if request.referrer:
        return redirect(request.referrer, code)

    return redirect(url_for("backoffice_v3_web.validation.list_offerers_to_validate"), code)


@dataclass
class OffererToBeValidatedRow:
    offerer: offerers_models.Offerer
    is_top_actor: bool
    last_comment: str | None
    owner: users_models.User


@validation_blueprint.route("/offerer", methods=["GET"])
def list_offerers_to_validate() -> utils.BackofficeResponse:
    stats = offerers_api.count_offerers_by_validation_status()

    form = offerer_forms.OffererValidationListForm(request.args)
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
        date_utils.date_to_localized_datetime(form.from_date.data, datetime.datetime.min.time()),
        date_utils.date_to_localized_datetime(form.to_date.data, datetime.datetime.max.time()),
    )

    sorted_offerers = offerers.order_by(offerers_models.Offerer.dateCreated.desc())

    paginated_offerers = sorted_offerers.paginate(  # type: ignore [attr-defined]
        page=int(form.data["page"]),
        per_page=int(form.data["per_page"]),
    )

    next_page = partial(url_for, ".list_offerers_to_validate", **form.data)
    next_pages_urls = search_utils.pagination_links(next_page, int(form.data["page"]), paginated_offerers.pages)

    form.page.data = 1  # Reset to first page when form is submitted ("Appliquer" clicked)

    return render_template(
        "offerer/validation.html",
        rows=paginated_offerers,
        form=form,
        next_pages_urls=next_pages_urls,
        is_top_actor_func=offerers_api.is_top_actor,
        get_last_comment_func=_get_serialized_offerer_last_comment,
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


def _get_serialized_user_offerer_last_comment(
    offerer: offerers_models.Offerer, user_id: int | None = None
) -> str | None:
    return _get_serialized_last_comment(
        (
            history_models.ActionType.USER_OFFERER_NEW,
            history_models.ActionType.USER_OFFERER_PENDING,
            history_models.ActionType.USER_OFFERER_VALIDATED,
            history_models.ActionType.USER_OFFERER_REJECTED,
            history_models.ActionType.COMMENT,
        ),
        offerer,
        user_id=user_id,
    )


@validation_blueprint.route("/user-offerer", methods=["GET"])
def list_offerers_attachments_to_validate() -> utils.BackofficeResponse:
    form = offerer_forms.UserOffererValidationListForm(request.args)
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

    sorted_users_offerers = users_offerers.order_by(offerers_models.UserOfferer.id.desc())

    paginated_users_offerers = sorted_users_offerers.paginate(  # type: ignore [attr-defined]
        page=int(form.data["page"]),
        per_page=int(form.data["per_page"]),
    )

    next_page = partial(url_for, ".list_offerers_attachments_to_validate", **form.data)
    next_pages_urls = search_utils.pagination_links(next_page, int(form.data["page"]), paginated_users_offerers.pages)

    form.page.data = 1  # Reset to first page when form is submitted ("Appliquer" clicked)

    return render_template(
        "offerer/user_offerer_validation.html",
        rows=paginated_users_offerers,
        form=form,
        next_pages_urls=next_pages_urls,
        is_top_actor_func=offerers_api.is_top_actor,
        get_last_comment_func=_get_serialized_user_offerer_last_comment,
    )


def _redirect_after_user_offerer_validation_action(offerer_id: int, code: int = 303) -> utils.BackofficeResponse:
    dst_url = url_for("backoffice_v3_web.offerer.get", offerer_id=offerer_id, active_tab="users")

    if request.referrer:
        referrer_path = urlparse(request.referrer).path
        dst_path = urlparse(dst_url).path

        if referrer_path != dst_path:
            return redirect(request.referrer, code)

    return redirect(dst_url + "#offerer_details_frame", code=code)


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

    form = _get_add_pro_user_form(offerer)
    # validate() checks that the id is within the list of previously attached users, so this ensures that:
    # - user exists with given id
    # - user_offerer entry does not exist with same ids
    if not form.validate():
        flash("Les données envoyées comportent des erreurs", "warning")
        return _redirect_after_user_offerer_validation_action(offerer.id)

    user = users_models.User.query.get(form.pro_user_id.data)

    new_user_offerer = offerers_models.UserOfferer(offerer=offerer, user=user, validationStatus=ValidationStatus.NEW)
    offerers_api.validate_offerer_attachment(new_user_offerer, current_user, form.comment.data)

    flash(f"Le rattachement de {user.email} à la structure {offerer.name} a été ajouté", "success")
    return _redirect_after_user_offerer_validation_action(offerer.id)


def _user_offerer_batch_action(
    api_function: typing.Callable[[offerers_models.UserOfferer, users_models.User, str | None], None],
    success_message: str,
) -> utils.BackofficeResponse:
    form = offerer_forms.BatchOptionalCommentForm()
    try:
        user_offerer_ids = [int(id) for id in form.object_ids.data.split(",")]
    except ValueError:
        flash("Identifiant(s) invalide(s)")
        return _redirect_after_offerer_validation_action(400)

    user_offerers = offerers_models.UserOfferer.query.filter(offerers_models.UserOfferer.id.in_(user_offerer_ids)).all()

    for user_offerer in user_offerers:
        api_function(user_offerer, current_user, form.comment.data)
    flash(success_message, "success")

    return _redirect_after_offerer_validation_action()


@validation_blueprint.route("/user-offerer/batch-pending", methods=["POST"])
def batch_set_user_offerer_pending() -> utils.BackofficeResponse:
    return _user_offerer_batch_action(
        offerers_api.set_offerer_attachment_pending, "Les rattachements ont été mis en attente avec succès"
    )


@validation_blueprint.route("/user-offerer/batch-reject", methods=["POST"])
def batch_reject_user_offerer() -> utils.BackofficeResponse:
    return _user_offerer_batch_action(
        offerers_api.reject_offerer_attachment, "Les rattachements sélectionnés ont été rejetés avec succès"
    )


@validation_blueprint.route("/user-offerer/batch-validate", methods=["POST"])
def batch_validate_user_offerer() -> utils.BackofficeResponse:
    return _user_offerer_batch_action(
        offerers_api.validate_offerer_attachment, "Les rattachements sélectionnés ont été validés avec succès"
    )


offerer_tag_blueprint = utils.child_backoffice_blueprint(
    "offerer_tag",
    __name__,
    url_prefix="/pro/offerer-tag",
    permission=perm_models.Permissions.MANAGE_PRO_ENTITY,
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
        error_msg = "Les données envoyées comportent des erreurs."
        for field in form:
            if field.errors:
                error_msg += f" {field.label.text}: {', '.join(error for error in field.errors)};"

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
        error_msg = "Les données envoyées comportent des erreurs."
        for field in form:
            if field.errors:
                error_msg += f" {field.label.text}: {', '.join(error for error in field.errors)};"

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
