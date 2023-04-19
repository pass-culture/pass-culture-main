from flask import escape
from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
import sqlalchemy as sa

import pcapi.core.criteria.models as criteria_models
import pcapi.core.permissions.models as perm_models
from pcapi.models import db
from pcapi.utils.clean_accents import clean_accents

from . import utils
from .forms import empty as empty_forms
from .forms import tags as tags_forms
from .forms.tags import SearchTagForm


tags_blueprint = utils.child_backoffice_blueprint(
    "tags",
    __name__,
    url_prefix="/tags/",
    permission=perm_models.Permissions.MANAGE_OFFERS_AND_VENUES_TAGS,
)


@tags_blueprint.route("", methods=["GET"])
def list_tags() -> utils.BackofficeResponse:
    form = SearchTagForm(formdata=utils.get_query_params())

    base_query = criteria_models.Criterion.query

    if not form.validate():
        return render_template("tags/list_tags.html", rows=base_query.all(), form=form, dst=url_for(".list_tags")), 400

    if form.is_empty():
        return render_template("tags/list_tags.html", rows=base_query.all(), form=form, dst=url_for(".list_tags"))

    query = clean_accents(form.q.data.replace(" ", "%").replace("-", "%"))
    tags = base_query.filter(
        sa.or_(
            sa.func.unaccent(criteria_models.Criterion.name).ilike(f"%{query}%"),
            sa.func.unaccent(criteria_models.Criterion.description).ilike(f"%{query}%"),
        )
    ).distinct()

    return render_template("tags/list_tags.html", rows=tags, form=form, dst=url_for(".list_tags"))


@tags_blueprint.route("/create", methods=["POST"])
def create_tag() -> utils.BackofficeResponse:
    form = tags_forms.EditTagForm()

    if not form.validate():
        error_msg = utils.build_form_error_msg(form)
        flash(error_msg, "warning")
        return redirect(url_for("backoffice_v3_web.tags.list_tags"), code=303)

    try:
        tag = criteria_models.Criterion(
            name=form.name.data,
            description=form.description.data,
            startDateTime=form.start_date.data,
            endDateTime=form.end_date.data,
        )

        db.session.add(tag)
        db.session.commit()
    except sa.exc.IntegrityError:
        db.session.rollback()
        flash("Ce tag existe déjà", "warning")
    else:
        flash("Tag offres et lieux créé", "success")

    return redirect(url_for("backoffice_v3_web.tags.list_tags"), code=303)


@tags_blueprint.route("/tags/new", methods=["GET"])
def get_create_tag_form() -> utils.BackofficeResponse:
    form = tags_forms.EditTagForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_v3_web.tags.create_tag"),
        div_id="create-offer-venue-tag",  # must be consistent with parameter passed to build_lazy_modal
        title="Créer un tag offres et lieux",
        button_text="Créer le tag",
    )


@tags_blueprint.route("/<int:tag_id>/update", methods=["POST"])
def update_tag(tag_id: int) -> utils.BackofficeResponse:
    tag = criteria_models.Criterion.query.get_or_404(tag_id)
    form = tags_forms.EditTagForm()

    if not form.validate():
        error_msg = utils.build_form_error_msg(form)
        flash(error_msg, "warning")
        return redirect(url_for("backoffice_v3_web.tags.list_tags"), code=303)

    tag.name = form.name.data
    tag.description = form.description.data
    tag.startDateTime = form.start_date.data
    tag.endDateTime = form.end_date.data

    try:
        db.session.add(tag)
        db.session.commit()
    except sa.exc.IntegrityError:
        db.session.rollback()
        flash("Ce nom de tag existe déjà", "warning")
    else:
        flash("Informations mises à jour", "success")

    return redirect(url_for("backoffice_v3_web.tags.list_tags"), code=303)


@tags_blueprint.route("/<int:tag_id>/edit", methods=["GET"])
def get_update_tag_form(tag_id: int) -> utils.BackofficeResponse:
    tag = criteria_models.Criterion.query.get_or_404(tag_id)

    form = tags_forms.EditTagForm(
        name=tag.name,
        description=tag.description,
        start_date=tag.startDateTime.date() if tag.startDateTime else None,
        end_date=tag.endDateTime.date() if tag.endDateTime else None,
    )

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_v3_web.tags.update_tag", tag_id=tag_id),
        div_id=f"update-offer-venue-tag-{tag_id}",  # must be consistent with parameter passed to build_lazy_modal
        title=f"Modifier {tag.name}",
        button_text="Valider",
    )


@tags_blueprint.route("/<int:tag_id>/delete", methods=["POST"])
@utils.permission_required(perm_models.Permissions.DELETE_OFFERER_TAG)
def delete_tag(tag_id: int) -> utils.BackofficeResponse:
    tag = criteria_models.Criterion.query.get_or_404(tag_id)

    try:
        db.session.delete(tag)
        db.session.commit()
    except sa.exc.DBAPIError as exception:
        db.session.rollback()
        flash(f"Une erreur s'est produite : {str(exception)}", "warning")

    flash("Le tag a bien été supprimé", "success")
    return redirect(url_for("backoffice_v3_web.tags.list_tags"), code=303)


@tags_blueprint.route("/<int:tag_id>/delete", methods=["GET"])
@utils.permission_required(perm_models.Permissions.DELETE_OFFERER_TAG)
def get_delete_tag_form(tag_id: int) -> utils.BackofficeResponse:
    tag = criteria_models.Criterion.query.get_or_404(tag_id)

    escaped_name = escape(tag.name)
    information = f"""
Le tag <strong>{ escaped_name }</strong> sera définitivement
supprimé de la base de données et retiré de toutes les offres et lieux 
auxquels il est associé. Veuillez confirmer ce choix.
"""

    return render_template(
        "components/turbo/modal_form.html",
        form=empty_forms.EmptyForm(),
        dst=url_for("backoffice_v3_web.tags.delete_tag", tag_id=tag_id),
        div_id=f"delete-offer-venue-tag-{tag_id}",  # must be consistent with parameter passed to build_lazy_modal
        title=f"Supprimer {tag.name}",
        button_text="Confirmer",
        information=information,
    )
