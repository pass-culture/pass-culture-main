from functools import partial
import typing

from flask import render_template
from flask import request
from flask import url_for
from flask_sqlalchemy import BaseQuery
import pydantic

from pcapi.core.offerers import api as offerers_api
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import api as users_api

from . import blueprint
from . import search_utils
from . import utils
from .forms import search as search_forms
from .serialization import search


GetBaseQuery = typing.Callable[[int], BaseQuery]


class Context:
    """
    Pro section handles different types of entities: pro users, offerers
    and venues. Each one has its own context to handle its specificities
    """

    fetch_rows_func: search_utils.SearchFunc
    get_item_base_query: GetBaseQuery

    @classmethod
    def get_pro_link(cls, row_id: int) -> str:
        raise NotImplementedError()


class UserContext(Context):
    fetch_rows_func = users_api.search_pro_account
    get_item_base_query = users_api.get_pro_account_base_query

    @classmethod
    def get_pro_link(cls, row_id: int) -> str:
        return url_for(".pro_user.get", user_id=row_id)


class OffererContext(Context):
    fetch_rows_func = offerers_api.search_offerer
    get_item_base_query = offerers_api.get_offerer_base_query

    @classmethod
    def get_pro_link(cls, row_id: int) -> str:
        return url_for(".offerer.get", offerer_id=row_id)


class VenueContext(Context):
    fetch_rows_func = offerers_api.search_venue
    get_item_base_query = offerers_api.get_venue_base_query

    @classmethod
    def get_pro_link(cls, row_id: int) -> str:
        return url_for(".venue.get", venue_id=row_id)


def render_search_template(form: search_forms.ProSearchForm | None = None) -> str:
    if form is None:
        form = search_forms.ProSearchForm()

    return render_template("pro/search.html", title="Recherche pro", dst=url_for(".search_pro"), form=form)


@blueprint.backoffice_v3_web.route("/pro/search", methods=["GET"])
@utils.permission_required(perm_models.Permissions.READ_PRO_ENTITY)
def search_pro() -> utils.BackofficeResponse:
    """
    Renders two search pages: first the one with the search form, then
    the one of the results.
    """
    if not request.args:
        return render_search_template()

    form = search_forms.ProSearchForm(request.args)
    if not form.validate():
        return render_search_template(form), 400

    try:
        # let pydantic run the more detailed validation and format the
        # form's data in a more user-friendly way
        search_model = search.SearchProModel(**form.data)
    except pydantic.ValidationError as err:
        for error in err.errors():
            form.add_error_to(typing.cast(str, error["loc"][0]))
        return render_search_template(form), 400

    next_page = partial(
        url_for,
        ".search_pro",
        pro_type=search_model.pro_type.value,
        terms=search_model.terms,
        order_by=search_model.order_by,
        per_page=search_model.per_page,
    )

    context = get_context(search_model.pro_type)
    paginated_rows = search_utils.fetch_paginated_rows(context.fetch_rows_func, search_model)
    next_pages_urls = search_utils.pagination_links(next_page, search_model.page, paginated_rows.pages)

    form.page.data = 1  # Reset to first page when form is submitted ("Chercher" clicked)

    return render_template(
        "pro/search_result.html",
        search_form=form,
        search_dst=url_for(".search_pro"),
        result_type=search_model.pro_type.value,
        next_pages_urls=next_pages_urls,
        new_search_url=url_for(".search_pro"),
        get_link_to_detail=context.get_pro_link,
        rows=paginated_rows,
        terms=search_model.terms,
        order_by=search_model.order_by,
        per_page=search_model.per_page,
    )


def get_context(pro_type: search.TypeOptions) -> typing.Type[Context]:
    return {
        search.TypeOptions.USER: UserContext,
        search.TypeOptions.OFFERER: OffererContext,
        search.TypeOptions.VENUE: VenueContext,
    }[pro_type]
