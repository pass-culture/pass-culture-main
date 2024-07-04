import datetime
from functools import partial
import typing

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_sqlalchemy import BaseQuery
import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.core.history import models as history_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import api as users_api
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import models as users_models
from pcapi.core.users.email import update as email_update
from pcapi.repository import atomic
from pcapi.repository import repository
from pcapi.routes.backoffice import search_utils
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.accounts import serialization
from pcapi.routes.backoffice.users import forms as user_forms
from pcapi.utils import email as email_utils

from . import forms


bo_users_blueprint = utils.child_backoffice_blueprint(
    "bo_users",
    __name__,
    url_prefix="/admin/bo-users",
    permission=perm_models.Permissions.READ_ADMIN_ACCOUNTS,
)


def _get_bo_user_query(user_id: int) -> BaseQuery:
    return users_models.User.query.filter_by(id=user_id).join(users_models.User.backoffice_profile)


def get_admin_account_link(user_id: int, form: forms.BOUserSearchForm | None, **kwargs: typing.Any) -> str:
    if form and form.q.data:
        kwargs["q"] = form.q.data
    return url_for("backoffice_web.bo_users.get_bo_user", user_id=user_id, **kwargs)


@bo_users_blueprint.route("/search", methods=["GET"])
@atomic()
def search_bo_users() -> utils.BackofficeResponse:
    request_args = utils.get_query_params()
    form = forms.BOUserSearchForm(formdata=request_args)
    if request_args and not form.validate():
        return render_template("admin/bo_users.html", search_form=form, search_dst=url_for(".search_bo_users")), 400

    users = users_api.search_backoffice_accounts(form.q.data)

    users = users.options(
        # suspension_reason is shown in result card; joinedload to avoid N+1 query
        sa.orm.joinedload(users_models.User.action_history)
    )

    paginated_rows = users.paginate(
        page=form.page.data,
        per_page=form.per_page.data,
    )
    next_page = partial(url_for, ".search_bo_users", **form.raw_data)
    next_pages_urls = search_utils.pagination_links(next_page, form.page.data, paginated_rows.pages)

    form.page.data = 1  # Reset to first page when form is submitted ("Chercher" clicked)

    return render_template(
        "admin/bo_users.html",
        search_form=form,
        search_dst=url_for(".search_bo_users"),
        next_pages_urls=next_pages_urls,
        get_link_to_detail=get_admin_account_link,
        rows=paginated_rows,
    )


def get_bo_user_history(user: users_models.User) -> list[serialization.AccountAction | history_models.ActionHistory]:
    # All data should have been joinloaded with user
    history: list[history_models.ActionHistory | serialization.AccountAction] = list(user.action_history)

    if history_models.ActionType.USER_CREATED not in (action.actionType for action in user.action_history):
        history.append(serialization.AccountCreatedAction(user))

    for change in user.email_history:
        history.append(serialization.EmailChangeAction(change))

    history = sorted(history, key=lambda item: item.actionDate or datetime.datetime.min, reverse=True)

    return history


def render_bo_user_page(user_id: int, edit_form: forms.EditBOUserForm | None = None) -> str:
    user = (
        _get_bo_user_query(user_id)
        .options(
            sa.orm.joinedload(users_models.User.action_history)
            .joinedload(history_models.ActionHistory.authorUser)
            .load_only(users_models.User.firstName, users_models.User.lastName),
            sa.orm.joinedload(users_models.User.email_history),
            sa.orm.joinedload(users_models.User.backoffice_profile).joinedload(perm_models.BackOfficeUserProfile.roles),
        )
        .one_or_none()
    )

    if not user:
        raise NotFound()

    if not edit_form and utils.has_current_user_permission(perm_models.Permissions.MANAGE_ADMIN_ACCOUNTS):
        edit_form = forms.EditBOUserForm(
            last_name=user.lastName,
            first_name=user.firstName,
            email=user.email,
        )

    return render_template(
        "accounts/get.html",
        layout="layouts/admin.html",
        search_form=forms.BOUserSearchForm(q=request.args.get("q")),
        search_dst=url_for(".search_bo_users"),
        user=user,
        edit_account_form=edit_form,
        edit_account_dst=url_for(".update_bo_user", user_id=user.id) if edit_form else None,
        history=get_bo_user_history(user),
        roles=user.backoffice_profile.roles if user.backoffice_profile else [],
        active_tab=request.args.get("active_tab", "history"),
        extract_user_form=None,
        **user_forms.get_toggle_suspension_args(
            user, required_permission=perm_models.Permissions.MANAGE_ADMIN_ACCOUNTS
        ),
    )


@bo_users_blueprint.route("/<int:user_id>", methods=["GET"])
@atomic()
def get_bo_user(user_id: int) -> utils.BackofficeResponse:
    return render_bo_user_page(user_id)


@bo_users_blueprint.route("/<int:user_id>", methods=["POST"])
@atomic()
@utils.permission_required(perm_models.Permissions.MANAGE_ADMIN_ACCOUNTS)
def update_bo_user(user_id: int) -> utils.BackofficeResponse:
    user = _get_bo_user_query(user_id).populate_existing().with_for_update(key_share=True).one_or_none()

    if not user:
        raise NotFound()

    form = forms.EditBOUserForm()
    if not form.validate():
        flash("Le formulaire n'est pas valide", "warning")
        return render_bo_user_page(user_id, form), 400

    snapshot = users_api.update_user_info(
        user, author=current_user, first_name=form.first_name.data, last_name=form.last_name.data, commit=False
    )

    if form.email.data and form.email.data != email_utils.sanitize_email(user.email):
        old_email = user.email
        try:
            email_update.full_email_update_by_admin(user, form.email.data)
        except users_exceptions.EmailExistsError:
            form.email.errors.append("L'email est déjà associé à un autre utilisateur")
            flash("L'email est déjà associé à un autre utilisateur", "warning")
            return render_bo_user_page(user_id, form), 400
        snapshot.set("email", old=old_email, new=form.email.data)

    snapshot.add_action()
    repository.save(user)

    flash("Les informations ont été mises à jour", "success")
    return redirect(url_for(".get_bo_user", user_id=user_id), code=303)
