from functools import partial

from flask import render_template
from flask import url_for
import sqlalchemy as sa

from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.repository import atomic
from pcapi.routes.backoffice import search_utils
from pcapi.routes.backoffice import utils

from . import forms as account_forms


account_update_blueprint = utils.child_backoffice_blueprint(
    "account_update",
    __name__,
    url_prefix="/account-update-requests",
    permission=perm_models.Permissions.MANAGE_ACCOUNT_UPDATE_REQUEST,
)


@account_update_blueprint.route("", methods=["GET"])
@atomic()
def list_account_update_requests() -> utils.BackofficeResponse:
    form = account_forms.AccountUpdateRequestSearchForm(formdata=utils.get_query_params())
    if not form.validate():
        return render_template("accounts/update_requests_list.html", rows=[], form=form), 400

    query = users_models.UserAccountUpdateRequest.query.options(
        sa.orm.joinedload(users_models.UserAccountUpdateRequest.user).load_only(
            users_models.User.id,
            users_models.User.email,
            users_models.User.firstName,
            users_models.User.lastName,
            users_models.User.civility,
            users_models.User.phoneNumber,
            users_models.User.dateOfBirth,
            users_models.User.validatedBirthDate,
        ),
        sa.orm.joinedload(users_models.UserAccountUpdateRequest.lastInstructor).load_only(
            users_models.User.id,
            users_models.User.email,
            users_models.User.firstName,
            users_models.User.lastName,
        ),
    ).order_by(users_models.UserAccountUpdateRequest.id.desc())

    paginated_rows = query.paginate(page=int(form.page.data), per_page=int(form.per_page.data))
    next_page = partial(url_for, ".list_account_update_requests", **form.raw_data)
    next_pages_urls = search_utils.pagination_links(next_page, int(form.page.data), paginated_rows.pages)
    form.page.data = 1  # Reset to first page when form is submitted ("Chercher" clicked)

    return render_template(
        "accounts/update_requests_list.html",
        rows=paginated_rows,
        form=form,
        next_pages_urls=next_pages_urls,
    )
