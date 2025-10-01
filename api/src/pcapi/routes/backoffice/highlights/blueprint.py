from functools import partial

import sqlalchemy as sa
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from markupsafe import Markup

from pcapi.core.highlights import api as highlights_api
from pcapi.core.highlights import models as highlights_models
from pcapi.core.permissions import models as perm_models
from pcapi.models import db
from pcapi.routes.backoffice import search_utils
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.search_utils import paginate
from pcapi.utils import db as db_utils
from pcapi.utils.clean_accents import clean_accents

from . import forms as highlights_forms


highlights_blueprint = utils.child_backoffice_blueprint(
    "highlights",
    __name__,
    url_prefix="/highlights/",
    permission=perm_models.Permissions.READ_HIGHLIGHT,
)


@highlights_blueprint.route("", methods=["GET"])
def list_highlights() -> utils.BackofficeResponse:
    form = highlights_forms.SearchHighlightForm(formdata=utils.get_query_params())
    if not form.validate():
        return (
            render_template(
                "highlights/list_highlights.html",
                rows=[],
                form=form,
                create_form=highlights_forms.CreateHighlightForm(),
            ),
            400,
        )

    query = db.session.query(highlights_models.Highlight)
    if form.q.data:
        search_query = f"%{clean_accents(form.q.data.replace(' ', '%').replace('-', '%'))}%"
        query_filter: sa.sql.elements.ColumnElement[bool] = sa.func.immutable_unaccent(
            highlights_models.Highlight.name
        ).ilike(search_query)

        query = query.filter(query_filter)

    paginated_rows = paginate(
        query=query.order_by(highlights_models.Highlight.highlight_timespan.desc()),
        page=int(form.page.data),
        per_page=int(form.limit.data),
    )

    form_url = partial(url_for, "backoffice_web.highlights.list_highlights", **form.raw_data)
    next_pages_urls = search_utils.pagination_links(form_url, int(form.page.data), paginated_rows.pages)

    form.page.data = 1  # Reset to first page when form is submitted ("Appliquer" clicked)

    return render_template(
        "highlights/list_highlights.html",
        rows=paginated_rows,
        form=form,
        next_pages_urls=next_pages_urls,
        create_form=highlights_forms.CreateHighlightForm(),
    )


@highlights_blueprint.route("/new", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_HIGHLIGHT)
def get_create_highlight_form() -> utils.BackofficeResponse:
    form = highlights_forms.CreateHighlightForm()

    return render_template(
        "components/dynamic/modal_form.html",
        ajax_submit=False,
        form=form,
        dst=url_for("backoffice_web.highlights.create_highlight"),
        div_id="create-highlight",  # must be consistent with parameter passed to build_lazy_modal
        title="Créer un temps fort",
        button_text="Créer le temps fort",
    )


@highlights_blueprint.route("/create", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_HIGHLIGHT)
def create_highlight() -> utils.BackofficeResponse:
    form = highlights_forms.CreateHighlightForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for(".list_highlights"), code=303)
    availability_timespan = db_utils.make_timerange(
        start=form.availability_timespan.data[0], end=form.availability_timespan.data[1]
    )
    highlight_timespan = db_utils.make_timerange(
        start=form.highlight_timespan.data[0], end=form.highlight_timespan.data[1]
    )
    highlight = highlights_api.create_highlight(
        name=form.name.data,
        description=form.description.data,
        availability_timespan=availability_timespan,
        highlight_timespan=highlight_timespan,
        image_as_bytes=form.get_image_as_bytes(request),
        image_mimetype=form.get_image_mimetype(request),
    )
    db.session.add(highlight)
    db.session.flush()

    flash(Markup("Le temps fort <b>{name}</b> a été créé.").format(name=highlight.name), "success")

    return redirect(url_for(".list_highlights"), code=303)
