from flask import escape
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
import sqlalchemy as sa

import pcapi.core.criteria.models as criteria_models
import pcapi.core.permissions.models as perm_models
from pcapi.models import db
from pcapi.routes.backoffice_v3 import utils
from pcapi.routes.backoffice_v3.forms import empty as empty_forms
from pcapi.utils.clean_accents import clean_accents

from . import form as criteria_forms


tags_blueprint = utils.child_backoffice_blueprint(
    "tags",
    __name__,
    url_prefix="/tags/",
    permission=perm_models.Permissions.MANAGE_OFFERS_AND_VENUES_TAGS,
)


def get_tags_categories() -> list[criteria_models.CriterionCategory]:
    return criteria_models.CriterionCategory.query.order_by(criteria_models.CriterionCategory.label).all()


@tags_blueprint.route("", methods=["GET"])
def list_tags() -> utils.BackofficeResponse:
    form = criteria_forms.SearchTagForm(formdata=utils.get_query_params())
    create_category_form = (
        criteria_forms.CreateCriterionCategoryForm()
        if utils.has_current_user_permission(perm_models.Permissions.MANAGE_TAGS_N2)
        else None
    )

    base_query = criteria_models.Criterion.query

    if not form.validate():
        tags = base_query.all()
        code = 400
    else:
        if form.is_empty():
            tags = base_query.all()
        else:
            query = clean_accents(form.q.data.replace(" ", "%").replace("-", "%"))
            tags = base_query.filter(
                sa.or_(
                    sa.func.unaccent(criteria_models.Criterion.name).ilike(f"%{query}%"),
                    sa.func.unaccent(criteria_models.Criterion.description).ilike(f"%{query}%"),
                )
            ).distinct()
        code = 200

    return (
        render_template(
            "tags/list_tags.html",
            rows=tags,
            form=form,
            dst=url_for(".list_tags"),
            category_rows=get_tags_categories(),
            create_category_form=create_category_form,
            active_tab=request.args.get("active_tab", "tags"),
        ),
        code,
    )


@tags_blueprint.route("/create", methods=["POST"])
def create_tag() -> utils.BackofficeResponse:
    form = criteria_forms.EditCriterionForm()
    form.categories.choices = [(cat.id, cat.label) for cat in get_tags_categories()]

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
            categories=[cat for cat in get_tags_categories() if cat.id in form.categories.data],
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
    form = criteria_forms.EditCriterionForm()
    form.categories.choices = [(cat.id, cat.label) for cat in get_tags_categories()]

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
    form = criteria_forms.EditCriterionForm()
    form.categories.choices = [(cat.id, cat.label) for cat in get_tags_categories()]

    if not form.validate():
        error_msg = utils.build_form_error_msg(form)
        flash(error_msg, "warning")
        return redirect(url_for("backoffice_v3_web.tags.list_tags"), code=303)

    tag.name = form.name.data
    tag.description = form.description.data
    tag.startDateTime = form.start_date.data
    tag.endDateTime = form.end_date.data
    tag.categories = [cat for cat in get_tags_categories() if cat.id in form.categories.data]

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

    form = criteria_forms.EditCriterionForm(
        name=tag.name,
        description=tag.description,
        start_date=tag.startDateTime.date() if tag.startDateTime else None,
        end_date=tag.endDateTime.date() if tag.endDateTime else None,
    )
    form.categories.choices = [(cat.id, cat.label or cat.name) for cat in get_tags_categories()]
    form.categories.data = [cat.id for cat in tag.categories]

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_v3_web.tags.update_tag", tag_id=tag_id),
        div_id=f"update-offer-venue-tag-{tag_id}",  # must be consistent with parameter passed to build_lazy_modal
        title=f"Modifier {tag.name}",
        button_text="Valider",
    )


@tags_blueprint.route("/<int:tag_id>/delete", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_TAGS_N2)
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
@utils.permission_required(perm_models.Permissions.MANAGE_TAGS_N2)
def get_delete_tag_form(tag_id: int) -> utils.BackofficeResponse:
    tag = criteria_models.Criterion.query.get_or_404(tag_id)

    escaped_name = escape(tag.name)
    information = f"""
Le tag <strong>{escaped_name}</strong> sera définitivement
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


@tags_blueprint.route("/tags/category", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_TAGS_N2)
def create_tag_category() -> utils.BackofficeResponse:
    form = criteria_forms.CreateCriterionCategoryForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for("backoffice_v3_web.tags.list_tags", active_tab="categories"), code=303)

    try:
        db.session.add(criteria_models.CriterionCategory(label=form.label.data))
        db.session.commit()
        flash("La catégorie a été créée", "success")
    except sa.exc.IntegrityError:
        db.session.rollback()
        flash("Cette catégorie existe déjà", "warning")

    return redirect(url_for("backoffice_v3_web.tags.list_tags", active_tab="categories"), code=303)
