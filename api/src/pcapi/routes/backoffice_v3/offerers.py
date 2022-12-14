from dataclasses import dataclass
import datetime
from functools import partial
import typing

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
import pytz
import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.core.history import models as history_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.models import db
import pcapi.utils.regions as regions_utils

from . import search_utils
from . import utils
from .forms import offerer as offerer_forms
from .serialization import offerers as serialization


PARIS_TZ = pytz.timezone("Europe/Paris")


def _date_to_localized_datetime(date_: datetime.date | None, time_: datetime.time) -> datetime.datetime | None:
    # When min/max date filters are used in requests, backoffice user expect Metroplitan French time (CET),
    # since date and time in the backoffice are formatted to show CET times.
    if not date_:
        return None
    naive_utc_datetime = datetime.datetime.combine(date_, time_)
    return PARIS_TZ.localize(naive_utc_datetime).astimezone(pytz.utc)


offerer_blueprint = utils.child_backoffice_blueprint(
    "offerer",
    __name__,
    url_prefix="/pro/offerer/<int:offerer_id>",
    permission=perm_models.Permissions.READ_PRO_ENTITY,
)


@offerer_blueprint.route("", methods=["GET"])
def get(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)
    basic_info = offerers_api.get_offerer_basic_info(offerer_id)

    if not basic_info:
        raise NotFound()

    bank_informations = basic_info.bank_informations or {}
    bank_informations_ok = bank_informations.get("ok", 0)
    bank_informations_ko = bank_informations.get("ko", 0)

    bank_information_status = serialization.OffererBankInformationStatus(
        ok=bank_informations_ok, ko=bank_informations_ko
    )

    return render_template(
        "offerer/get.html",
        offerer=offerer,
        region=regions_utils.get_region_name_from_postal_code(offerer.postalCode),
        bank_information_status=bank_information_status,
        is_collective_eligible=basic_info.is_collective_eligible,
    )


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


def _is_user_offerer_action_type(historyItem: serialization.HistoryItem) -> bool:
    user_offerer_action_types = [
        history_models.ActionType.USER_OFFERER_NEW,
        history_models.ActionType.USER_OFFERER_PENDING,
        history_models.ActionType.USER_OFFERER_VALIDATED,
        history_models.ActionType.USER_OFFERER_REJECTED,
    ]
    return history_models.ActionType(historyItem.type) in user_offerer_action_types


def _is_offerer_new_action_type(historyItem: serialization.HistoryItem) -> bool:
    return history_models.ActionType(historyItem.type) == history_models.ActionType.OFFERER_NEW


def get_offerer_history_data(offerer: offerers_models.Offerer) -> typing.Sequence[serialization.HistoryItem]:
    # this should not be necessary but in case there is a huge amount
    # of actions, it is safer to set a limit
    max_actions_count = 50

    actions = sorted(offerer.action_history, key=lambda action: action.actionDate, reverse=True)
    return [
        serialization.HistoryItem(
            type=action.actionType.value,
            date=action.actionDate,
            authorId=action.authorUserId,
            authorName=action.authorUser.full_name if action.authorUser else None,
            comment=action.comment,
            accountId=action.userId,
            accountName=action.user.full_name if action.user else None,
        )
        for action in actions[:max_actions_count]
    ]


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


@offerer_blueprint.route("/details", methods=["GET"])
def get_details(offerer_id: int) -> utils.BackofficeResponse:
    offerer = get_offerer(offerer_id)

    history = get_offerer_history_data(offerer)

    return render_template(
        "offerer/get/details.html",
        offerer=offerer,
        history=history,
        users_offerer=offerer.UserOfferers,
        active_tab=request.args.get("active_tab", "history"),
        is_user_offerer_action_type=_is_user_offerer_action_type,
        is_offerer_new_action_type=_is_offerer_new_action_type,
    )


offerer_comment_blueprint = utils.child_backoffice_blueprint(
    "offerer_comment",
    __name__,
    url_prefix="/pro/offerer/<int:offerer_id>/comment",
    permission=perm_models.Permissions.MANAGE_PRO_ENTITY,
)


@offerer_comment_blueprint.route("", methods=["GET"])
def new_comment(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)
    form = offerer_forms.CommentForm()
    return render_template("offerer/comment.html", form=form, offerer=offerer)


@offerer_comment_blueprint.route("", methods=["POST"])
def comment_offerer(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)

    form = offerer_forms.CommentForm()
    if not form.validate():
        flash("Les données envoyées comportent des erreurs", "warning")
        return render_template("offerer/comment.html", form=form, offerer=offerer), 400

    offerers_api.add_comment_to_offerer(offerer, current_user, comment=form.comment.data)
    flash("Commentaire enregistré", "success")

    return redirect(url_for("backoffice_v3_web.offerer.get", offerer_id=offerer_id), code=303)


validate_offerer_blueprint = utils.child_backoffice_blueprint(
    "validate_offerer",
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

    return redirect(url_for("backoffice_v3_web.validate_offerer.list_offerers_to_validate"), code)


@dataclass
class OffererToBeValidatedRow:
    offerer: offerers_models.Offerer
    is_top_actor: bool
    last_comment: str | None
    owner: users_models.User


@validate_offerer_blueprint.route("/offerer", methods=["GET"])
def list_offerers_to_validate() -> utils.BackofficeResponse:
    stats = offerers_api.count_offerers_by_validation_status()

    form = offerer_forms.OffererValidationListForm(request.args)
    if not form.validate():
        return render_template("offerer/validation.html", rows=[], form=form, stats=stats), 400

    offerers = offerers_api.list_offerers_to_be_validated(
        form.q.data,
        form.tags.data,
        form.status.data,
        _date_to_localized_datetime(form.from_date.data, datetime.datetime.min.time()),
        _date_to_localized_datetime(form.to_date.data, datetime.datetime.max.time()),
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


@offerer_blueprint.route("/validate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def validate(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)

    try:
        offerers_api.validate_offerer(offerer, current_user)
    except offerers_exceptions.OffererAlreadyValidatedException:
        flash(f"La structure {offerer.name} est déjà validée", "warning")
        return _redirect_after_offerer_validation_action(code=400)

    flash(f"La structure {offerer.name} a été validée", "success")
    return _redirect_after_offerer_validation_action()


@offerer_blueprint.route("/reject", methods=["POST"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def reject(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)

    form = offerer_forms.OptionalCommentForm()
    if not form.validate():
        flash("Les données envoyées comportent des erreurs", "warning")
        return _redirect_after_offerer_validation_action(code=400)

    try:
        offerers_api.reject_offerer(offerer, current_user, comment=form.comment.data)
    except offerers_exceptions.OffererAlreadyRejectedException:
        flash(f"La structure {offerer.name} est déjà rejetée", "warning")
        return _redirect_after_offerer_validation_action(code=400)

    flash(f"La structure {offerer.name} a été rejetée", "success")
    return _redirect_after_offerer_validation_action()


@offerer_blueprint.route("/pending", methods=["POST"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def set_pending(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)

    form = offerer_forms.OptionalCommentForm()
    if not form.validate():
        flash("Les données envoyées comportent des erreurs", "warning")
        return _redirect_after_offerer_validation_action(code=400)

    offerers_api.set_offerer_pending(offerer, current_user, comment=form.comment.data)

    flash(f"La structure {offerer.name} a été mise en attente", "success")
    return _redirect_after_offerer_validation_action()


@offerer_blueprint.route("/top-actor", methods=["POST"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def toggle_top_actor(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)

    try:
        tag = offerers_models.OffererTag.query.filter(offerers_models.OffererTag.name == "top-acteur").one()
    except sa.exc.NoResultFound:
        flash("Le tag top-acteur n'existe pas", "warning")
        return _redirect_after_offerer_validation_action(code=400)

    form = offerer_forms.TopActorForm()
    if not form.validate():
        flash("Les données envoyées comportent des erreurs", "warning")
        return _redirect_after_offerer_validation_action(code=400)

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


@validate_offerer_blueprint.route("/user_offerer", methods=["GET"])
def list_offerers_attachments_to_validate() -> utils.BackofficeResponse:
    form = offerer_forms.UserOffererValidationListForm(request.args)
    if not form.validate():
        return render_template("offerer/user_offerer_validation.html", rows=[], form=form), 400

    users_offerers = offerers_api.list_users_offerers_to_be_validated(
        form.tags.data,
        form.status.data,
        _date_to_localized_datetime(form.from_date.data, datetime.datetime.min.time()),
        _date_to_localized_datetime(form.to_date.data, datetime.datetime.max.time()),
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
    if request.referrer:
        return redirect(request.referrer, code)

    return redirect(url_for("backoffice_v3_web.offerer.get", offerer_id=offerer_id), code=code)


user_offerer_blueprint = utils.child_backoffice_blueprint(
    "user_offerer",
    __name__,
    url_prefix="/pro/user_offerer/<int:user_offerer_id>",
    permission=perm_models.Permissions.VALIDATE_OFFERER,
)


@user_offerer_blueprint.route("/validate", methods=["POST"])
def user_offerer_validate(user_offerer_id: int) -> utils.BackofficeResponse:
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


@user_offerer_blueprint.route("/reject", methods=["POST"])
def user_offerer_reject(user_offerer_id: int) -> utils.BackofficeResponse:
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


@user_offerer_blueprint.route("/pending", methods=["POST"])
def user_offerer_set_pending(user_offerer_id: int) -> utils.BackofficeResponse:
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
