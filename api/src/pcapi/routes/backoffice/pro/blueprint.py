from functools import partial
import typing

from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_sqlalchemy import BaseQuery

from pcapi.core.offerers import api as offerers_api
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import api as users_api
from pcapi.routes.backoffice import search_utils
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.pro import forms as pro_forms


pro_blueprint = utils.child_backoffice_blueprint(
    "pro",
    __name__,
    url_prefix="/pro",
    permission=perm_models.Permissions.READ_PRO_ENTITY,
)


class Context:
    """
    Pro section handles different types of entities: pro users, offerers
    and venues. Each one has its own context to handle its specificities
    """

    fetch_rows_func: typing.Callable[[str, list[str]], BaseQuery]
    get_item_base_query: typing.Callable[[int], BaseQuery]
    endpoint: str
    row_id_name: str

    @classmethod
    def get_pro_link(cls, row_id: int, form: pro_forms.ProSearchForm | None, **kwargs: typing.Any) -> str:
        if form:
            kwargs.update({cls.row_id_name: row_id, "q": form.q.data, "departments": form.departments.data})
        return url_for(cls.endpoint, **kwargs)


class UserContext(Context):
    fetch_rows_func = users_api.search_pro_account
    get_item_base_query = users_api.get_pro_account_base_query
    endpoint = "backoffice_web.pro_user.get"
    row_id_name = "user_id"


class OffererContext(Context):
    fetch_rows_func = offerers_api.search_offerer
    get_item_base_query = offerers_api.get_offerer_base_query
    endpoint = "backoffice_web.offerer.get"
    row_id_name = "offerer_id"


class VenueContext(Context):
    fetch_rows_func = offerers_api.search_venue
    get_item_base_query = offerers_api.get_venue_base_query
    endpoint = "backoffice_web.venue.get"
    row_id_name = "venue_id"


class BankAccountContext(Context):
    fetch_rows_func = offerers_api.search_bank_account
    get_item_base_query = offerers_api.get_bank_account_base_query
    endpoint = "backoffice_web.bank_account.get"
    row_id_name = "bank_account_id"

    @classmethod
    def get_pro_link(cls, row_id: int, form: pro_forms.ProSearchForm | None, **kwargs: typing.Any) -> str:
        # No ConsultCard logged for bank account
        filtered_kwargs = {k: v for k, v in kwargs.items() if v and k not in ("search_rank", "total_items")}
        return super().get_pro_link(row_id, form, **filtered_kwargs)


def render_search_template(form: pro_forms.ProSearchForm | None = None) -> str:
    if form is None:
        preferences = current_user.backoffice_profile.preferences
        form = pro_forms.ProSearchForm(departments=preferences.get("departments", []))

    return render_template("pro/search.html", title="Recherche pro", dst=url_for(".search_pro"), form=form)


@pro_blueprint.route("/search", methods=["GET"])
def search_pro() -> utils.BackofficeResponse:
    """
    Renders two search pages: first the one with the search form, then
    the one of the results.
    """
    if not request.args:
        return render_search_template()

    form = pro_forms.ProSearchForm(request.args)
    if not form.validate():
        return render_search_template(form), 400

    result_type = form.pro_type.data
    context = get_context(result_type)
    rows = context.fetch_rows_func(form.q.data, form.departments.data)
    paginated_rows = rows.paginate(
        page=form.page.data,
        per_page=form.per_page.data,
    )

    next_page = partial(url_for, ".search_pro", **form.raw_data)
    next_pages_urls = search_utils.pagination_links(next_page, form.page.data, paginated_rows.pages)

    utils.log_backoffice_tracking_data(
        event_name="PerformSearch",
        extra_data={
            "searchType": "ProSearch",
            "searchQuery": form.q.data,
            "searchDepartments": ",".join(form.departments.data),
            "searchNbResults": paginated_rows.total,
            "searchProType": form.pro_type.data.value,
        },
    )

    if paginated_rows.total == 1:
        return redirect(
            context.get_pro_link(paginated_rows.items[0].id, form=form, search_rank=1, total_items=1), code=303
        )

    search_form = pro_forms.CompactProSearchForm(request.args)
    search_form.page.data = 1  # Reset to first page when form is submitted ("Chercher" clicked)
    search_form.pro_type.data = form.pro_type.data.name  # Don't send an enum to jinja

    return render_template(
        "pro/search_result.html",
        search_form=search_form,
        search_dst=url_for(".search_pro"),
        result_type=result_type.value,
        next_pages_urls=next_pages_urls,
        get_link_to_detail=context.get_pro_link,
        rows=paginated_rows,
    )


def get_context(pro_type: pro_forms.TypeOptions) -> type[Context]:
    return {
        pro_forms.TypeOptions.USER: UserContext,
        pro_forms.TypeOptions.OFFERER: OffererContext,
        pro_forms.TypeOptions.VENUE: VenueContext,
        pro_forms.TypeOptions.BANK_ACCOUNT: BankAccountContext,
    }[pro_type]
