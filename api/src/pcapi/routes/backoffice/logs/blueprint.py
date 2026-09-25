import datetime
import typing

from flask import Response
from flask import flash
from flask import render_template
from flask import url_for
from sqlalchemy import orm as sa_orm

from pcapi.connectors.google_logs import get_backend
from pcapi.core import token
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.routes.backoffice import blueprint as backoffice_blueprint
from pcapi.routes.backoffice.utils import advanced_search as advanced_search_utils
from pcapi.routes.backoffice.utils import request as request_utils
from pcapi.routes.backoffice.utils import response as response_utils

from . import forms as logs_forms


logs_blueprint = backoffice_blueprint.child_backoffice_blueprint(
    "logs",
    __name__,
    url_prefix="/logs/",
    permission=perm_models.Permissions.READ_TECH_LOGS,
)

LOG_PAGE_SIZE = 20
MAXIMUM_LOG_TIME = 12 * 60 * 60  # 12h
LOG_SEARCH_EXPIRATION = datetime.timedelta(hours=2)
SEARCH_FIELD_TO_PYTHON: dict[str, dict[str, typing.Any]] = {
    "LOG_DATE": {
        "field": "date",
        "log_field_name": "timestamp",
        "special": lambda d: datetime.datetime.combine(d, datetime.time.min).timestamp(),
    },
    "OFFER": {
        "field": "integer",
        "log_field_name": "jsonPayload.extra.offer_id",
    },
    "PRODUCT": {
        "field": "integer",
        "log_field_name": "jsonPayload.extra.product_id",
    },
}


@logs_blueprint.route("", methods=["GET"])
def list_logs() -> response_utils.BackofficeResponse:
    form = logs_forms.SearchForm(formdata=request_utils.get_query_params())
    if not form.validate():
        return (
            render_template(
                "logs/list.html",
                dst=url_for("backoffice.logs.list_logs"),
                form=form,
                force_display_table=False,
            ),
            400,
        )

    search_log, warnings = advanced_search_utils.generate_gcp_search_dict(
        search_type=form.search_type.data,
        search_parameters=form.search.data,
        fields_definition=SEARCH_FIELD_TO_PYTHON,
    )
    for warning in warnings:
        flash(warning, "warning")

    search_token = token.create_token(
        token_type=token.TokenType.LOG_SEARCH, data=search_log.dict(), ttl=LOG_SEARCH_EXPIRATION
    )

    return render_template(
        "logs/list.html",
        dst=url_for("backoffice.logs.list_logs"),
        form=form,
        token=search_token,
        force_display_table=True,
    )


@logs_blueprint.route("rows/<search_token>", methods=["GET"])
def list_logs_rows(search_token: str) -> response_utils.BackofficeResponse:
    try:
        search = advanced_search_utils.FilterLogContainer.from_dict(
            token.load_token(
                token_type=token.TokenType.LOG_SEARCH,
                token=search_token,
            ),
        )
    except users_exceptions.InvalidToken:
        # token expired or already consumed
        return Response(
            response="redirecting",
            status=303,
            headers={
                "HX-Redirect": url_for("backoffice.logs.list_logs"),
            },
        )

    # pagination
    if search.end_date <= search.original_start_date:
        # extended search we search past original_start_date
        search.start_date = search.end_date - MAXIMUM_LOG_TIME
    else:
        search.start_date = max(search.end_date - MAXIMUM_LOG_TIME, search.original_start_date)

    filters = advanced_search_utils.generate_gcp_search_string_from_list(search)

    logs = []
    users_id = set()

    for log in get_backend().get_logs(filters=filters, limit=LOG_PAGE_SIZE):
        logs.append(log)
        if log.user_id:
            users_id.add(log.user_id)
        if log.impersonator_id:
            users_id.add(log.impersonator_id)

    # pagination
    if (not logs) or (logs[-1].insert_id == search.last_insert_id) or len(logs) < LOG_PAGE_SIZE:
        search.end_date = search.start_date
    else:
        search.end_date = logs[-1].timestamp

    # infinite loop detection
    if logs:
        search.last_insert_id = logs[-1].insert_id

    # get users for links and display names
    users_query = (
        db.session.query(
            users_models.User,
        )
        .filter(
            users_models.User.id.in_(users_id),
        )
        .options(
            sa_orm.load_only(
                users_models.User.id,
                users_models.User.firstName,
                users_models.User.lastName,
            ),
        )
    )

    users_dict = {user.id: user for user in users_query}

    next_page_token = token.create_token(
        token_type=token.TokenType.LOG_SEARCH, data=search.dict(), ttl=LOG_SEARCH_EXPIRATION
    )
    return render_template(
        "logs/list_rows.html",
        logs=logs,
        token=search_token,
        users=users_dict,
        next_page_token=next_page_token,
        auto_next=search.start_date > search.original_start_date,
    )
