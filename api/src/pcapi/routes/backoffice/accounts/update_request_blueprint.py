from functools import partial

from flask import render_template
from flask import request
from flask import url_for

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
    # if not request.args:
    #     return ...
    #
    form = account_forms.AccountSearchForm(request.args)  # TODO filters form
    # if not form.validate():
    #     return ..., 400

    query = users_models.UserAccountUpdateRequest.query

    paginated_rows = query.paginate(page=form.page.data, per_page=form.per_page.data)

    next_page = partial(url_for, ".list_account_update_requests", **form.raw_data)
    next_pages_urls = search_utils.pagination_links(next_page, form.page.data, paginated_rows.pages)

    form.page.data = 1  # Reset to first page when form is submitted ("Chercher" clicked)

    return render_template(
        "accounts/update_request_list.html",
        search_form=form,
        search_dst=url_for(".list_account_update_requests"),
        next_pages_urls=next_pages_urls,
        rows=paginated_rows,
    )
