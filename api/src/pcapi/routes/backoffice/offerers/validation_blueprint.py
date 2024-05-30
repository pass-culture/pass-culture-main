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
from flask_sqlalchemy import BaseQuery
from markupsafe import Markup
import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.core.history import models as history_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.routes.backoffice import autocomplete
from pcapi.routes.backoffice import search_utils
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.forms.empty import BatchForm
from pcapi.utils import date as date_utils

from . import forms as offerer_forms
from . import validation_repository


validation_blueprint = utils.child_backoffice_blueprint(
    "validation",
    __name__,
    url_prefix="/pro/validation",
    permission=perm_models.Permissions.READ_PRO_ENTITY,
)


def _filter_homologation_tags(tags: list[offerers_models.OffererTag]) -> list[offerers_models.OffererTag]:
    return [tag for tag in tags if "homologation" in [cat.name for cat in tag.categories]]


def _redirect_after_offerer_validation_action(code: int = 303) -> utils.BackofficeResponse:
    if request.referrer:
        return redirect(request.referrer, code)

    return redirect(url_for("backoffice_web.validation.list_offerers_to_validate"), code)


@validation_blueprint.route("/offerer", methods=["GET"])
def list_offerers_to_validate() -> utils.BackofficeResponse:
    stats = offerers_api.count_offerers_by_validation_status()

    form = offerer_forms.OffererValidationListForm(formdata=utils.get_query_params())
    if not form.validate():
        return render_template("offerer/validation.html", rows=[], form=form, stats=stats), 400

    # new and pending attachments by default
    if not form.status.data:
        form.status.data = [ValidationStatus.NEW.value]

    offerers = validation_repository.list_offerers_to_be_validated(
        form.q.data,
        form.regions.data,
        form.tags.data,
        form.status.data,
        form.ae_documents_received.data,
        form.instructors.data,
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

    autocomplete.prefill_bo_users_choices(form.instructors)

    return render_template(
        "offerer/validation.html",
        rows=paginated_offerers,
        form=form,
        next_pages_urls=next_pages_urls,
        date_created_sort_url=date_created_sort_url,
        stats=stats,
    )


@validation_blueprint.route("/offerer/<int:offerer_id>/validate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def validate_offerer(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        offerers_models.Offerer.query.filter_by(id=offerer_id)
        .populate_existing()
        .with_for_update(key_share=True)
        .one_or_none()
    )
    if not offerer:
        raise NotFound()

    try:
        offerers_api.validate_offerer(offerer, current_user)
    except offerers_exceptions.OffererAlreadyValidatedException:
        flash(Markup("La structure <b>{name}</b> est déjà validée").format(name=offerer.name), "warning")
        return _redirect_after_offerer_validation_action()

    flash(Markup("La structure <b>{name}</b> a été validée").format(name=offerer.name), "success")
    return _redirect_after_offerer_validation_action()


@validation_blueprint.route("/offerer/<int:offerer_id>/reject", methods=["GET"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def get_reject_offerer_form(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        offerers_models.Offerer.query.filter_by(id=offerer_id)
        .populate_existing()
        .with_for_update(key_share=True)
        .one_or_none()
    )
    if not offerer:
        raise NotFound()

    form = offerer_forms.OptionalCommentForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.validation.reject_offerer", offerer_id=offerer.id),
        div_id=f"reject-modal-{offerer.id}",  # must be consistent with parameter passed to build_lazy_modal
        title=f"Rejeter la structure la structure {offerer.name.upper()}",
        button_text="Rejeter la structure",
    )


@validation_blueprint.route("/offerer/<int:offerer_id>/reject", methods=["POST"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def reject_offerer(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        offerers_models.Offerer.query.filter_by(id=offerer_id)
        .populate_existing()
        .with_for_update(key_share=True)
        .one_or_none()
    )
    if not offerer:
        raise NotFound()

    form = offerer_forms.OptionalCommentForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _redirect_after_offerer_validation_action()

    try:
        offerers_api.reject_offerer(offerer, current_user, comment=form.comment.data)
    except offerers_exceptions.OffererAlreadyRejectedException:
        flash(Markup("La structure <b>{name}</b> est déjà rejetée").format(name=offerer.name), "warning")
        return _redirect_after_offerer_validation_action()

    flash(Markup("La structure <b>{name}</b> a été rejetée").format(name=offerer.name), "success")
    return _redirect_after_offerer_validation_action()


@validation_blueprint.route("/offerer/<int:offerer_id>/pending", methods=["GET"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def get_offerer_pending_form(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        offerers_models.Offerer.query.filter_by(id=offerer_id)
        .options(
            sa.orm.joinedload(offerers_models.Offerer.tags)
            .joinedload(offerers_models.OffererTag.categories)
            .load_only(offerers_models.OffererTagCategory.name)
        )
        .one_or_none()
    )
    if not offerer:
        raise NotFound()

    form = offerer_forms.CommentAndTagOffererForm(tags=_filter_homologation_tags(offerer.tags))

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.validation.set_offerer_pending", offerer_id=offerer.id),
        div_id=f"pending-modal-{offerer.id}",  # must be consistent with parameter passed to build_lazy_modal
        title=f"Mettre en attente la structure {offerer.name.upper()}",
        button_text="Mettre en attente",
    )


@validation_blueprint.route("/offerer/<int:offerer_id>/pending", methods=["POST"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def set_offerer_pending(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        offerers_models.Offerer.query.filter_by(id=offerer_id)
        .populate_existing()
        .with_for_update(key_share=True)
        .one_or_none()
    )
    if not offerer:
        raise NotFound()

    form = offerer_forms.CommentAndTagOffererForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _redirect_after_offerer_validation_action()

    # Don't pass directly form.tags.data to set_offerer_pending() because this would remove non-homologation tags
    saved_homologation_tags = set(_filter_homologation_tags(offerer.tags))
    tags_to_add = set(form.tags.data) - saved_homologation_tags
    tags_to_remove = saved_homologation_tags - set(form.tags.data)

    offerers_api.set_offerer_pending(
        offerer, current_user, comment=form.comment.data, tags_to_add=tags_to_add, tags_to_remove=tags_to_remove
    )

    flash(Markup("La structure <b>{name}</b> a été mise en attente").format(name=offerer.name), "success")
    return _redirect_after_offerer_validation_action()


@validation_blueprint.route("/offerer/<int:offerer_id>/top-actor", methods=["POST"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def toggle_top_actor(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        offerers_models.Offerer.query.filter_by(id=offerer_id)
        .populate_existing()
        .with_for_update(key_share=True, read=True)
        .one_or_none()
    )
    if not offerer:
        raise NotFound()

    try:
        tag = offerers_models.OffererTag.query.filter(offerers_models.OffererTag.name == "top-acteur").one()
    except sa.exc.NoResultFound:
        flash("Le tag top-acteur n'existe pas", "warning")
        return _redirect_after_offerer_validation_action()

    form = offerer_forms.TopActorForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
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

    offerers = (
        offerers_models.Offerer.query.filter(offerers_models.Offerer.id.in_(form.object_ids_list))
        .populate_existing()
        .with_for_update(key_share=True)
        .all()
    )

    if hasattr(form, "tags"):
        tags = form.tags.data
        previous_tags = set.intersection(*[set(offerer.tags) for offerer in offerers])
        deleted_tags = list(previous_tags.difference(set(tags)))
    else:
        deleted_tags = []

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
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def batch_validate_offerer() -> utils.BackofficeResponse:
    try:
        return _offerer_batch_action(
            offerers_api.validate_offerer,
            "Les structures sélectionnées ont été validées",
            BatchForm,
        )
    except offerers_exceptions.OffererAlreadyValidatedException:
        flash("Au moins une des structures a déjà été validée", "warning")
        return _redirect_after_offerer_validation_action()


@validation_blueprint.route("/offerer/batch-pending-form", methods=["GET", "POST"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
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
        tags = list(set.intersection(*[set(offerer.tags) for offerer in offerers]))

        if len(tags) > 0:
            form.tags.data = tags

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.validation.batch_set_offerer_pending"),
        div_id="batch-pending-modal",
        title="Mettre en attente les structures",
        button_text="Mettre en attente les structures",
    )


@validation_blueprint.route("/offerer/batch-pending", methods=["POST"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def batch_set_offerer_pending() -> utils.BackofficeResponse:
    return _offerer_batch_action(
        offerers_api.set_offerer_pending,
        "Les structures sélectionnées ont été mises en attente",
        offerer_forms.BatchCommentAndTagOffererForm,
    )


@validation_blueprint.route("/offerer/batch-reject-form", methods=["GET"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def get_batch_reject_offerer_form() -> utils.BackofficeResponse:
    form = offerer_forms.BatchOptionalCommentForm()
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.validation.batch_reject_offerer"),
        div_id="batch-reject-modal",
        title="Rejeter les structures",
        button_text="Rejeter les structures",
    )


@validation_blueprint.route("/offerer/batch-reject", methods=["POST"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def batch_reject_offerer() -> utils.BackofficeResponse:
    try:
        return _offerer_batch_action(
            offerers_api.reject_offerer,
            "Les structures sélectionnées ont été rejetées",
            offerer_forms.BatchOptionalCommentForm,
        )
    except offerers_exceptions.OffererAlreadyRejectedException:
        flash("Une des structures a déjà été rejetée", "warning")
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
                history_models.ActionType.USER_OFFERER_DELETED,
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

    # new and pending attachments by default
    if not form.status.data:
        form.status.data = [ValidationStatus.NEW.value]

    users_offerers = validation_repository.list_users_offerers_to_be_validated(
        form.q.data,
        form.regions.data,
        form.tags.data,
        form.status.data,
        form.instructors.data,
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

    autocomplete.prefill_bo_users_choices(form.instructors)

    return render_template(
        "offerer/user_offerer_validation.html",
        rows=paginated_users_offerers,
        form=form,
        next_pages_urls=next_pages_urls,
        get_last_comment_func=_get_serialized_user_offerer_last_comment,
        date_created_sort_url=date_created_sort_url,
    )


def _redirect_after_user_offerer_validation_action(offerer_id: int, code: int = 303) -> utils.BackofficeResponse:
    dst_url = url_for("backoffice_web.offerer.get", offerer_id=offerer_id, active_tab="users")

    if request.referrer:
        referrer_path = urlparse(request.referrer).path
        dst_path = urlparse(dst_url).path

        if referrer_path != dst_path:
            return redirect(request.referrer, code)

    return redirect(dst_url + "#offerer_details_frame", code=code)


def _redirect_after_user_offerer_validation_action_list(code: int = 303) -> utils.BackofficeResponse:
    if request.referrer:
        return redirect(request.referrer, code)

    return redirect(url_for("backoffice_web.validation.list_offerers_attachments_to_validate"), code)


user_offerer_blueprint = utils.child_backoffice_blueprint(
    "user_offerer",
    __name__,
    url_prefix="/pro/user_offerer/<int:user_offerer_id>",
    permission=perm_models.Permissions.VALIDATE_OFFERER,
)


def _load_user_offerer(user_offerer_id: int) -> offerers_models.UserOfferer:
    user_offerer = (
        offerers_models.UserOfferer.query.filter_by(id=user_offerer_id)
        .options(
            sa.orm.joinedload(offerers_models.UserOfferer.user).load_only(users_models.User.email),
            sa.orm.joinedload(offerers_models.UserOfferer.offerer).load_only(
                offerers_models.Offerer.id, offerers_models.Offerer.name
            ),
        )
        .one_or_none()
    )

    if not user_offerer:
        raise NotFound()

    return user_offerer


@validation_blueprint.route("/user-offerer/<int:user_offerer_id>/validate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def validate_user_offerer(user_offerer_id: int) -> utils.BackofficeResponse:
    user_offerer = _load_user_offerer(user_offerer_id)

    try:
        offerers_api.validate_offerer_attachment(user_offerer, current_user)
    except offerers_exceptions.UserOffererAlreadyValidatedException:
        flash(
            Markup("Le rattachement de <b>{email}</b> à la structure <b>{offerer_name}</b> est déjà validé").format(
                email=user_offerer.user.email, offerer_name=user_offerer.offerer.name
            ),
            "warning",
        )
        return _redirect_after_user_offerer_validation_action(user_offerer.offerer.id)

    flash(
        Markup("Le rattachement de <b>{email}</b> à la structure <b>{offerer_name}</b> a été validé").format(
            email=user_offerer.user.email, offerer_name=user_offerer.offerer.name
        ),
        "success",
    )
    return _redirect_after_user_offerer_validation_action(user_offerer.offerer.id)


@validation_blueprint.route("/user-offerer/batch-reject", methods=["GET"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def get_batch_reject_user_offerer_form() -> utils.BackofficeResponse:
    form = offerer_forms.BatchOptionalCommentForm()
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.validation.batch_reject_user_offerer"),
        div_id="batch-reject-modal",
        title="Rejeter le rattachement",
        button_text="Rejeter le rattachement",
    )


@validation_blueprint.route("/user-offerer/batch-pending", methods=["GET"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def get_batch_user_offerer_pending_form() -> utils.BackofficeResponse:
    form = offerer_forms.BatchOptionalCommentForm()
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.validation.batch_set_user_offerer_pending"),
        div_id="batch-pending-modal",
        title="Mettre en attente le rattachement",
        button_text="Mettre en attente le rattachement",
    )


@validation_blueprint.route("/user-offerer/<int:user_offerer_id>/reject", methods=["GET"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def get_reject_user_offerer_form(user_offerer_id: int) -> utils.BackofficeResponse:
    user_offerer = _load_user_offerer(user_offerer_id)

    form = offerer_forms.OptionalCommentForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.validation.reject_user_offerer", user_offerer_id=user_offerer.id),
        div_id=f"reject-modal-{user_offerer.id}",  # must be consistent with parameter passed to build_lazy_modal
        title=f"Rejeter le rattachement à {user_offerer.offerer.name.upper()}",
        button_text="Rejeter le rattachement",
    )


@validation_blueprint.route("/user-offerer/<int:user_offerer_id>/reject", methods=["POST"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def reject_user_offerer(user_offerer_id: int) -> utils.BackofficeResponse:
    user_offerer = _load_user_offerer(user_offerer_id)

    form = offerer_forms.OptionalCommentForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _redirect_after_user_offerer_validation_action(user_offerer.offerer.id)

    offerers_api.reject_offerer_attachment(user_offerer, current_user, form.comment.data)

    flash(
        Markup("Le rattachement de <b>{email}</b> à la structure <b>{offerer_name}</b> a été rejeté").format(
            email=user_offerer.user.email, offerer_name=user_offerer.offerer.name
        ),
        "success",
    )
    return _redirect_after_user_offerer_validation_action(user_offerer.offerer.id)


@validation_blueprint.route("/user-offerer/<int:user_offerer_id>/pending", methods=["GET"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def get_user_offerer_pending_form(user_offerer_id: int) -> utils.BackofficeResponse:
    user_offerer = _load_user_offerer(user_offerer_id)

    form = offerer_forms.OptionalCommentForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.validation.set_user_offerer_pending", user_offerer_id=user_offerer.id),
        div_id=f"pending-modal-{user_offerer.id}",  # must be consistent with parameter passed to build_lazy_modal
        title=f"Mettre en attente le rattachement à {user_offerer.offerer.name.upper()}",
        button_text="Mettre en attente le rattachement",
    )


@validation_blueprint.route("/user-offerer/<int:user_offerer_id>/pending", methods=["POST"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def set_user_offerer_pending(user_offerer_id: int) -> utils.BackofficeResponse:
    user_offerer = _load_user_offerer(user_offerer_id)

    form = offerer_forms.OptionalCommentForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _redirect_after_user_offerer_validation_action(user_offerer.offerer.id)

    offerers_api.set_offerer_attachment_pending(user_offerer, current_user, form.comment.data)
    flash(
        Markup("Le rattachement de <b>{email}</b> à la structure <b>{offerer_name}</b> a été mis en attente").format(
            email=user_offerer.user.email, offerer_name=user_offerer.offerer.name
        ),
        "success",
    )

    return _redirect_after_user_offerer_validation_action(user_offerer.offerer.id)


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
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def batch_set_user_offerer_pending() -> utils.BackofficeResponse:
    return _user_offerer_batch_action(
        offerers_api.set_offerer_attachment_pending, "Les rattachements ont été mis en attente"
    )


@validation_blueprint.route("/user-offerer/batch-reject", methods=["POST"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def batch_reject_user_offerer() -> utils.BackofficeResponse:
    try:
        return _user_offerer_batch_action(
            offerers_api.reject_offerer_attachment, "Les rattachements sélectionnés ont été rejetés"
        )
    except offerers_exceptions.UserOffererAlreadyValidatedException:
        flash("Au moins un des rattachements est déjà rejeté", "warning")
        return _redirect_after_user_offerer_validation_action_list()


@validation_blueprint.route("/user-offerer/batch-validate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def batch_validate_user_offerer() -> utils.BackofficeResponse:
    try:
        return _user_offerer_batch_action(
            offerers_api.validate_offerer_attachment, "Les rattachements sélectionnés ont été validés"
        )
    except offerers_exceptions.UserOffererAlreadyValidatedException:
        flash("Au moins un des rattachements est déjà validé", "warning")
        return _redirect_after_user_offerer_validation_action_list()
