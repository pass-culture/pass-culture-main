import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from markupsafe import Markup
from werkzeug.exceptions import NotFound

from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.models import db
from pcapi.utils.transaction_manager import mark_transaction_as_invalid

from .. import utils
from ..forms import empty as empty_forms
from . import forms as offerer_forms


offerer_tag_blueprint = utils.child_backoffice_blueprint(
    "offerer_tag",
    __name__,
    url_prefix="/pro/offerer-tag",
    permission=perm_models.Permissions.READ_TAGS,
)


def get_offerer_tag_categories() -> list[offerers_models.OffererTagCategory]:
    return db.session.query(offerers_models.OffererTagCategory).order_by(offerers_models.OffererTagCategory.label).all()


@offerer_tag_blueprint.route("", methods=["GET"])
def list_offerer_tags() -> utils.BackofficeResponse:
    categories = get_offerer_tag_categories()
    offerer_tags = (
        db.session.query(offerers_models.OffererTag)
        .options(sa_orm.joinedload(offerers_models.OffererTag.categories))
        .order_by(offerers_models.OffererTag.name)
        .all()
    )

    forms = {}

    if utils.has_current_user_permission(perm_models.Permissions.MANAGE_OFFERER_TAG):
        update_tag_forms = {}
        categories_choices = [(cat.id, cat.label or cat.name) for cat in categories]

        for offerer_tag in offerer_tags:
            update_tag_forms[offerer_tag.id] = offerer_forms.EditOffererTagForm(
                name=offerer_tag.name,
                label=offerer_tag.label,
                description=offerer_tag.description,
            )
            update_tag_forms[offerer_tag.id].categories.choices = categories_choices
            update_tag_forms[offerer_tag.id].categories.data = [cat.id for cat in offerer_tag.categories]

        forms["update_tag_forms"] = update_tag_forms

        create_tag_form = offerer_forms.EditOffererTagForm()
        create_tag_form.categories.choices = categories_choices
        forms["create_tag_form"] = create_tag_form
        forms["create_category_form"] = offerer_forms.CreateOffererTagCategoryForm()

    if utils.has_current_user_permission(perm_models.Permissions.MANAGE_TAGS_N2):
        forms["delete_tag_form"] = empty_forms.EmptyForm()

    return render_template(
        "offerer/offerer_tag.html",
        rows=offerer_tags,
        category_rows=categories,
        active_tab=request.args.get("active_tab", "tags"),
        **forms,
    )


@offerer_tag_blueprint.route("/create", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERER_TAG)
def create_offerer_tag() -> utils.BackofficeResponse:
    categories = get_offerer_tag_categories()
    form = offerer_forms.EditOffererTagForm()
    form.categories.choices = [(cat.id, cat.label) for cat in categories]

    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for("backoffice_web.offerer_tag.list_offerer_tags"), code=303)

    new_categories = [cat for cat in categories if cat.id in form.categories.data]
    try:
        tag = offerers_models.OffererTag(
            name=form.name.data,
            label=form.label.data,
            description=form.description.data,
            categories=new_categories,
        )
        db.session.add(tag)
        db.session.flush()
        flash("Le nouveau tag a été créé", "success")

    except sa.exc.IntegrityError:
        mark_transaction_as_invalid()
        flash("Ce tag existe déjà", "warning")

    return redirect(url_for("backoffice_web.offerer_tag.list_offerer_tags"), code=303)


@offerer_tag_blueprint.route("/<int:offerer_tag_id>/update", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERER_TAG)
def update_offerer_tag(offerer_tag_id: int) -> utils.BackofficeResponse:
    offerer_tag_to_update = db.session.query(offerers_models.OffererTag).filter_by(id=offerer_tag_id).one_or_none()
    if not offerer_tag_to_update:
        raise NotFound()

    categories = get_offerer_tag_categories()

    form = offerer_forms.EditOffererTagForm()
    form.categories.choices = [(cat.id, cat.label or cat.name) for cat in categories]

    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for("backoffice_web.offerer_tag.list_offerer_tags"), code=303)

    new_categories = [cat for cat in categories if cat.id in form.categories.data]
    try:
        offerers_api.update_offerer_tag(
            offerer_tag_to_update,
            name=form.name.data,
            label=form.label.data,
            description=form.description.data,
            categories=new_categories,
        )
        flash("Les informations ont été mises à jour", "success")
    except sa.exc.IntegrityError:
        mark_transaction_as_invalid()
        flash("Ce nom de tag existe déjà", "warning")

    return redirect(url_for("backoffice_web.offerer_tag.list_offerer_tags"), code=303)


@offerer_tag_blueprint.route("/<int:offerer_tag_id>/delete", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_TAGS_N2)
def delete_offerer_tag(offerer_tag_id: int) -> utils.BackofficeResponse:
    offerer_tag_to_delete = db.session.query(offerers_models.OffererTag).filter_by(id=offerer_tag_id).one_or_none()
    if not offerer_tag_to_delete:
        raise NotFound()

    try:
        db.session.delete(offerer_tag_to_delete)
        db.session.flush()
    except sa.exc.DBAPIError as exception:
        mark_transaction_as_invalid()
        flash(Markup("Une erreur s'est produite : {message}").format(message=str(exception)), "warning")

    return redirect(url_for("backoffice_web.offerer_tag.list_offerer_tags"), code=303)


@offerer_tag_blueprint.route("/category", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERER_TAG)
def create_offerer_tag_category() -> utils.BackofficeResponse:
    form = offerer_forms.CreateOffererTagCategoryForm()

    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for("backoffice_web.offerer_tag.list_offerer_tags", active_tab="categories"), code=303)

    try:
        db.session.add(offerers_models.OffererTagCategory(name=form.name.data, label=form.label.data))
        db.session.flush()
        flash("La nouvelle catégorie a été créée", "success")
    except sa.exc.IntegrityError:
        mark_transaction_as_invalid()
        flash("Cette catégorie existe déjà", "warning")

    return redirect(url_for("backoffice_web.offerer_tag.list_offerer_tags", active_tab="categories"), code=303)
