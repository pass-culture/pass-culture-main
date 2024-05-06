from functools import partial

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from markupsafe import Markup
import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.core.criteria import models as criteria_models
from pcapi.core.permissions import models as perm_models
from pcapi.models import db
from pcapi.repository import atomic
from pcapi.repository import mark_transaction_as_invalid
from pcapi.routes.backoffice import search_utils
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.utils.clean_accents import clean_accents

from . import forms as criteria_forms


tags_blueprint = utils.child_backoffice_blueprint(
    "tags",
    __name__,
    url_prefix="/tags/",
    permission=perm_models.Permissions.READ_TAGS,
)


def get_tags_categories() -> list[criteria_models.CriterionCategory]:
    return criteria_models.CriterionCategory.query.order_by(criteria_models.CriterionCategory.label).all()


@tags_blueprint.route("", methods=["GET"])
@atomic()
def list_tags() -> utils.BackofficeResponse:
    form = criteria_forms.SearchTagForm(formdata=utils.get_query_params())
    create_category_form = (
        criteria_forms.CreateCriterionCategoryForm()
        if utils.has_current_user_permission(perm_models.Permissions.MANAGE_TAGS_N2)
        else None
    )

    query = criteria_models.Criterion.query.options(sa.orm.joinedload(criteria_models.Criterion.categories))

    if not form.validate():
        code = 400
    else:
        if form.q.data:
            search_query = clean_accents(form.q.data.replace(" ", "%").replace("-", "%"))
            query = query.filter(
                sa.or_(
                    sa.func.unaccent(criteria_models.Criterion.name).ilike(f"%{search_query}%"),
                    sa.func.unaccent(criteria_models.Criterion.description).ilike(f"%{search_query}%"),
                )
            )
        code = 200

    paginated_tags = query.order_by(criteria_models.Criterion.name).paginate(
        page=int(form.page.data),
        per_page=int(form.per_page.data),
    )

    form_url = partial(url_for, ".list_tags", **form.raw_data)
    next_pages_urls = search_utils.pagination_links(form_url, int(form.page.data), paginated_tags.pages)

    form.page.data = 1  # Reset to first page when form is submitted ("Appliquer" clicked)

    return (
        render_template(
            "tags/list_tags.html",
            rows=paginated_tags,
            form=form,
            dst=url_for(".list_tags"),
            next_pages_urls=next_pages_urls,
            category_rows=get_tags_categories(),
            create_category_form=create_category_form,
            active_tab=request.args.get("active_tab", "tags"),
        ),
        code,
    )


@tags_blueprint.route("/create", methods=["POST"])
@atomic()
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS_AND_VENUES_TAGS)
def create_tag() -> utils.BackofficeResponse:
    form = criteria_forms.EditCriterionForm()
    form.categories.choices = [(cat.id, cat.label) for cat in get_tags_categories()]

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for("backoffice_web.tags.list_tags"), code=303)

    try:
        tag = criteria_models.Criterion(
            name=form.name.data,
            description=form.description.data,
            startDateTime=form.start_date.data,
            endDateTime=form.end_date.data,
            categories=[cat for cat in get_tags_categories() if cat.id in form.categories.data],
        )

        db.session.add(tag)
        db.session.flush()
    except sa.exc.IntegrityError:
        mark_transaction_as_invalid()
        flash("Ce tag existe déjà", "warning")
    else:
        flash("Le nouveau tag offres et lieux a été créé", "success")

    return redirect(url_for("backoffice_web.tags.list_tags"), code=303)


@tags_blueprint.route("/tags/new", methods=["GET"])
@atomic()
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS_AND_VENUES_TAGS)
def get_create_tag_form() -> utils.BackofficeResponse:
    form = criteria_forms.EditCriterionForm()
    form.categories.choices = [(cat.id, cat.label) for cat in get_tags_categories()]

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.tags.create_tag"),
        div_id="create-offer-venue-tag",  # must be consistent with parameter passed to build_lazy_modal
        title="Créer un tag offres et lieux",
        button_text="Créer le tag",
    )


@tags_blueprint.route("/<int:tag_id>/update", methods=["POST"])
@atomic()
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS_AND_VENUES_TAGS)
def update_tag(tag_id: int) -> utils.BackofficeResponse:
    tag = criteria_models.Criterion.query.filter_by(id=tag_id).one_or_none()
    if not tag:
        raise NotFound()

    form = criteria_forms.EditCriterionForm()
    form.categories.choices = [(cat.id, cat.label) for cat in get_tags_categories()]

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for("backoffice_web.tags.list_tags"), code=303)

    tag.name = form.name.data
    tag.description = form.description.data
    tag.startDateTime = form.start_date.data
    tag.endDateTime = form.end_date.data
    tag.categories = [cat for cat in get_tags_categories() if cat.id in form.categories.data]

    try:
        db.session.add(tag)
        db.session.flush()
    except sa.exc.IntegrityError:
        mark_transaction_as_invalid()
        flash("Ce nom de tag existe déjà", "warning")
    else:
        flash("Informations mises à jour", "success")

    return redirect(url_for("backoffice_web.tags.list_tags"), code=303)


@tags_blueprint.route("/<int:tag_id>/edit", methods=["GET"])
@atomic()
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS_AND_VENUES_TAGS)
def get_update_tag_form(tag_id: int) -> utils.BackofficeResponse:
    tag = criteria_models.Criterion.query.filter_by(id=tag_id).one_or_none()
    if not tag:
        raise NotFound()

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
        dst=url_for("backoffice_web.tags.update_tag", tag_id=tag_id),
        div_id=f"update-offer-venue-tag-{tag_id}",  # must be consistent with parameter passed to build_lazy_modal
        title=f"Modifier {tag.name}",
        button_text="Valider",
    )


@tags_blueprint.route("/<int:tag_id>/delete", methods=["POST"])
@atomic()
@utils.permission_required(perm_models.Permissions.MANAGE_TAGS_N2)
def delete_tag(tag_id: int) -> utils.BackofficeResponse:
    tag = criteria_models.Criterion.query.filter_by(id=tag_id).one_or_none()
    if not tag:
        raise NotFound()

    try:
        db.session.delete(tag)
        db.session.flush()
    except sa.exc.DBAPIError as exception:
        mark_transaction_as_invalid()
        flash(Markup("Une erreur s'est produite : {message}").format(message=str(exception)), "warning")

    flash("Le tag a été supprimé", "success")
    return redirect(url_for("backoffice_web.tags.list_tags"), code=303)


@tags_blueprint.route("/<int:tag_id>/delete", methods=["GET"])
@atomic()
@utils.permission_required(perm_models.Permissions.MANAGE_TAGS_N2)
def get_delete_tag_form(tag_id: int) -> utils.BackofficeResponse:
    tag = criteria_models.Criterion.query.filter_by(id=tag_id).one_or_none()
    if not tag:
        raise NotFound()

    information = Markup(
        "Le tag <strong>{name}</strong> sera définitivement supprimé de la base de données et retiré de toutes les "
        "offres et lieux auxquels il est associé. Veuillez confirmer ce choix."
    ).format(name=tag.name)

    return render_template(
        "components/turbo/modal_form.html",
        form=empty_forms.EmptyForm(),
        dst=url_for("backoffice_web.tags.delete_tag", tag_id=tag_id),
        div_id=f"delete-offer-venue-tag-{tag_id}",  # must be consistent with parameter passed to build_lazy_modal
        title=f"Supprimer {tag.name}",
        button_text="Confirmer",
        information=information,
    )


@tags_blueprint.route("/tags/category", methods=["POST"])
@atomic()
@utils.permission_required(perm_models.Permissions.MANAGE_TAGS_N2)
def create_tag_category() -> utils.BackofficeResponse:
    form = criteria_forms.CreateCriterionCategoryForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for("backoffice_web.tags.list_tags", active_tab="categories"), code=303)

    try:
        db.session.add(criteria_models.CriterionCategory(label=form.label.data))
        db.session.flush()
        flash("La nouvelle catégorie a été créée", "success")
    except sa.exc.IntegrityError:
        mark_transaction_as_invalid()
        flash("Cette catégorie existe déjà", "warning")

    return redirect(url_for("backoffice_web.tags.list_tags", active_tab="categories"), code=303)
