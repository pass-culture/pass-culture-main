import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from markupsafe import Markup
from werkzeug.exceptions import NotFound

from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.accounts import forms as accounts_forms
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


account_tag_blueprint = utils.child_backoffice_blueprint(
    "account_tag",
    __name__,
    url_prefix="/public-accounts/tags",
    permission=perm_models.Permissions.READ_TAGS,
)


class Sentinel:
    pass


sentinel = Sentinel()


def get_user_tag_categories() -> list[users_models.UserTagCategory]:
    return db.session.query(users_models.UserTagCategory).order_by(users_models.UserTagCategory.label).all()


@account_tag_blueprint.route("", methods=["GET"])
def list_account_tags() -> utils.BackofficeResponse:
    categories = get_user_tag_categories()
    user_tags = (
        db.session.query(users_models.UserTag)
        .options(sa_orm.joinedload(users_models.UserTag.categories))
        .order_by(users_models.UserTag.name)
        .all()
    )

    forms = {}

    if utils.has_current_user_permission(perm_models.Permissions.MANAGE_ACCOUNT_TAGS):
        update_tag_forms = {}
        categories_choices = [(cat.id, str(cat)) for cat in categories]

        for user_tag in user_tags:
            update_tag_forms[user_tag.id] = accounts_forms.EditUserTagForm(
                name=user_tag.name,
                label=user_tag.label,
                description=user_tag.description,
            )
            update_tag_forms[user_tag.id].categories.choices = categories_choices
            update_tag_forms[user_tag.id].categories.data = [cat.id for cat in user_tag.categories]

        forms["update_tag_forms"] = update_tag_forms

        create_tag_form = accounts_forms.EditUserTagForm()
        create_tag_form.categories.choices = categories_choices
        forms["create_tag_form"] = create_tag_form
        forms["create_category_form"] = accounts_forms.CreateUserTagCategoryForm()

    if utils.has_current_user_permission(perm_models.Permissions.MANAGE_ACCOUNT_TAGS_N2):
        forms["delete_tag_form"] = empty_forms.EmptyForm()

    return render_template(
        "accounts/account_tags.html",
        rows=user_tags,
        category_rows=categories,
        active_tab=request.args.get("active_tab", "tags"),
        **forms,
    )


@account_tag_blueprint.route("/create", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_ACCOUNT_TAGS)
def create_account_tag() -> utils.BackofficeResponse:
    categories = get_user_tag_categories()
    form = accounts_forms.EditUserTagForm()
    form.categories.choices = [(cat.id, cat.label) for cat in categories]

    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for("backoffice_web.account_tag.list_account_tags"), code=303)

    new_categories = [cat for cat in categories if cat.id in form.categories.data]
    try:
        tag = users_models.UserTag(
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

    return redirect(url_for("backoffice_web.account_tag.list_account_tags"), code=303)


def _update_user_tag(
    user_tag: users_models.UserTag,
    name: str | Sentinel = sentinel,
    label: str | None | Sentinel = sentinel,
    description: str | None | Sentinel = sentinel,
    categories: list[users_models.UserTagCategory] | Sentinel = sentinel,
) -> None:
    update = False

    if name is not sentinel:
        assert isinstance(name, str)  # helps mypy
        user_tag.name = name
        update = True
    if label is not sentinel:
        assert isinstance(label, str | None)  # helps mypy
        user_tag.label = label
        update = True
    if description is not sentinel:
        assert isinstance(description, str | None)  # helps mypy
        user_tag.description = description
        update = True
    if categories is not sentinel:
        if isinstance(categories, list) and set(user_tag.categories) != set(categories):
            user_tag.categories = categories
            update = True

    if update:
        db.session.add(user_tag)
        db.session.flush()


@account_tag_blueprint.route("/<int:user_tag_id>/update", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_ACCOUNT_TAGS)
def update_account_tag(user_tag_id: int) -> utils.BackofficeResponse:
    user_tag_to_update = db.session.query(users_models.UserTag).filter_by(id=user_tag_id).one_or_none()
    if not user_tag_to_update:
        raise NotFound()

    categories = get_user_tag_categories()

    form = accounts_forms.EditUserTagForm()
    form.categories.choices = [(cat.id, cat.label or cat.name) for cat in categories]

    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for("backoffice_web.account_tag.list_account_tags"), code=303)

    new_categories = [cat for cat in categories if cat.id in form.categories.data]
    try:
        _update_user_tag(
            user_tag_to_update,
            name=form.name.data,
            label=form.label.data,
            description=form.description.data,
            categories=new_categories,
        )
        flash("Les informations ont été mises à jour", "success")
    except sa.exc.IntegrityError:
        mark_transaction_as_invalid()
        flash("Ce nom de tag existe déjà", "warning")

    return redirect(url_for("backoffice_web.account_tag.list_account_tags"), code=303)


@account_tag_blueprint.route("/<int:user_tag_id>/delete", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_ACCOUNT_TAGS_N2)
def delete_account_tag(user_tag_id: int) -> utils.BackofficeResponse:
    user_tag_to_delete = db.session.query(users_models.UserTag).filter_by(id=user_tag_id).one_or_none()
    if not user_tag_to_delete:
        raise NotFound()

    try:
        db.session.delete(user_tag_to_delete)
        db.session.flush()
        flash("La catégorie a été supprimée", "success")
    except sa.exc.DBAPIError as exception:
        mark_transaction_as_invalid()
        flash(
            Markup("Une erreur s'est produite : {message}").format(message=str(exception)),
            "warning",
        )

    return redirect(url_for("backoffice_web.account_tag.list_account_tags"), code=303)


@account_tag_blueprint.route("/category", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_ACCOUNT_TAGS)
def create_account_tag_category() -> utils.BackofficeResponse:
    form = accounts_forms.CreateUserTagCategoryForm()

    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(
            url_for("backoffice_web.account_tag.list_account_tags", active_tab="categories"),
            code=303,
        )

    try:
        db.session.add(users_models.UserTagCategory(name=form.name.data, label=form.label.data))
        db.session.flush()
        flash("La nouvelle catégorie a été créée", "success")
    except sa.exc.IntegrityError:
        mark_transaction_as_invalid()
        flash("Cette catégorie existe déjà", "warning")

    return redirect(
        url_for("backoffice_web.account_tag.list_account_tags", active_tab="categories"),
        code=303,
    )
