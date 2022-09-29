from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
import pydantic

from pcapi.core.permissions import models as perm_models
from pcapi.core.users import api as users_api
from pcapi.models.feature import FeatureToggle
from pcapi.routes.serialization import BaseModel

from . import blueprint
from . import utils


SearchTerm = pydantic.constr(min_length=1, max_length=128, strip_whitespace=True)
SortByTerm = pydantic.constr(min_length=1, max_length=128, strip_whitespace=True)


class SearchModel(BaseModel):
    terms: pydantic.conlist(item_type=SearchTerm, min_items=1, max_items=16, unique_items=True)  # type: ignore
    order_by: pydantic.conlist(item_type=SortByTerm, min_items=0, max_items=16, unique_items=True)  # type: ignore
    page: pydantic.conint(ge=1, le=10)  # type: ignore
    per_page: pydantic.conint(ge=1, le=100)  # type: ignore

    @pydantic.validator("terms", pre=True)
    def validate_terms(cls, value):  # type: ignore
        return value.split(",")

    @pydantic.validator("order_by", pre=True)
    def validate_order_by(cls, value):  # type: ignore
        if not value:
            return ["id"]
        return value.split(",")


@blueprint.poc_backoffice_web.route("/search", methods=["GET", "POST"])
@utils.custom_login_required(redirect_to=".unauthorized")
@utils.ff_enabled(FeatureToggle.ENABLE_NEW_BACKOFFICE_POC, redirect_to=".unauthorized")
@utils.permission_required(perm_models.Permissions.SEARCH_PUBLIC_ACCOUNT, redirect_to=".unauthorized")
def search():  # type: ignore
    if request.method == "GET" and not request.args:
        order_by = [
            "id",
            "-id",
            "email",
            "-email",
            "firstName",
            "-firstName",
            "lastName",
            "-lastName",
        ]
        return render_template("search.template.html", order_by_options=order_by)

    if request.method == "GET" and request.args:
        return handle_search()

    return redirect(
        url_for(
            ".search",
            query=request.form["query"],
            order_by=request.form["order_by"],
            page=1,
            per_page=20,
        )
    )


def handle_search():  # type: ignore
    try:
        search_model = SearchModel(
            terms=request.args["query"],
            order_by=request.args["order_by"],
            page=request.args["page"],
            per_page=request.args["per_page"],
        )
    except pydantic.ValidationError as err:
        print(err)
        return redirect(url_for(".invalid_search"))

    paginated = users_api.search_public_account(search_model.terms, order_by=search_model.order_by).paginate(
        page=search_model.page, per_page=search_model.per_page, error_out=False
    )

    return render_template(
        "search_result.template.html",
        rows=paginated,
        terms=search_model.terms,
        order_by=search_model.order_by,
        per_page=search_model.per_page,
    )


@blueprint.poc_backoffice_web.route("/invalid-search", methods=["GET"])
@utils.ff_enabled(FeatureToggle.ENABLE_NEW_BACKOFFICE_POC, redirect_to=".unauthorized")
def invalid_search():  # type: ignore
    return render_template("invalid_search.template.html")
