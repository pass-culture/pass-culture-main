from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
import sqlalchemy as sa

from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.models import db

from . import forms as offerer_forms
from .. import utils
from ..forms import empty as empty_forms


offerer_tag_blueprint = utils.child_backoffice_blueprint(
    "offerer_tag",
    __name__,
    url_prefix="/pro/offerer-tag",
    permission=perm_models.Permissions.MANAGE_OFFERER_TAG,
)


def get_offerer_tag_categories() -> list[offerers_models.OffererTagCategory]:
    return offerers_models.OffererTagCategory.query.order_by(offerers_models.OffererTagCategory.label).all()


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
