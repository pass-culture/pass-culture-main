import datetime
from functools import partial

from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from flask_login import current_user
import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.core.chronicles import models as chronicles_models
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.repository import atomic
from pcapi.routes.backoffice import search_utils
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.forms.empty import EmptyForm
from pcapi.routes.backoffice.utils import permission_required
from pcapi.utils import string as string_utils

from . import forms


chronicles_blueprint = utils.child_backoffice_blueprint(
    "chronicles",
    __name__,
    url_prefix="/chronicles/",
    permission=perm_models.Permissions.READ_CHRONICLE,
)


@chronicles_blueprint.route("", methods=["GET"])
@atomic()
def list_chronicles() -> utils.BackofficeResponse:

    if not FeatureToggle.WIP_ENABLE_CHRONICLES_IN_BO.is_active():
        raise NotFound()

    form = forms.GetChronicleSearchForm(formdata=utils.get_query_params())
    if not form.validate():
        return render_template("chronicles/list.html", rows=[], form=form), 400

    product_subquery = (
        sa.select(sa.func.array_agg(offers_models.Product.name))
        .select_from(chronicles_models.ProductChronicle)
        .join(offers_models.Product, offers_models.Product.id == chronicles_models.ProductChronicle.productId)
        .filter(chronicles_models.ProductChronicle.chronicleId == chronicles_models.Chronicle.id)
        .scalar_subquery()
    )

    query = db.session.query(
        chronicles_models.Chronicle.id,
        chronicles_models.Chronicle.content,
        sa.func.left(chronicles_models.Chronicle.content, 350).label("short_content"),
        chronicles_models.Chronicle.dateCreated,
        chronicles_models.Chronicle.isActive,
        product_subquery.label("products"),
    )
    q_filters = []
    if form.q.data and string_utils.is_ean_valid(form.q.data):
        query = query.join(chronicles_models.Chronicle.products)
        q_filters.append(offers_models.Product.extraData["ean"].astext == string_utils.format_ean_or_visa(form.q.data))
    elif form.q.data:
        if form.search_type.data in (forms.SearchType.ALL.name, forms.SearchType.CHRONICLE_CONTENT.name):
            q_filters.append(
                sa.and_(
                    chronicles_models.Chronicle.__content_ts_vector__.match(w, postgresql_regconfig="french")
                    for w in form.q.data.split(" ")
                )
            )
        if form.search_type.data in (forms.SearchType.ALL.name, forms.SearchType.PRODUCT_NAME.name):
            if form.search_type.data == forms.SearchType.ALL.name:
                query = query.outerjoin(chronicles_models.Chronicle.products)
            else:
                query = query.join(chronicles_models.Chronicle.products)
            split_product_name = "%".join(form.q.data.split(" "))
            q_filters.append(offers_models.Product.name.ilike(f"%{split_product_name}%"))
    if q_filters:
        query = query.filter(sa.or_(*q_filters))

    if form.date_range.data:
        if form.date_range.from_date is not None:
            from_date = datetime.datetime.combine(form.date_range.from_date, datetime.time.min)
            query = query.filter(chronicles_models.Chronicle.dateCreated >= from_date)
        if form.date_range.to_date is not None:
            to_date = datetime.datetime.combine(form.date_range.to_date, datetime.time.max)
            query = query.filter(chronicles_models.Chronicle.dateCreated < to_date)

    query = query.order_by(chronicles_models.Chronicle.id.desc())

    paginated_chronicles = query.paginate(
        page=int(form.page.data),
        per_page=int(form.per_page.data),
    )

    form_url = partial(url_for, "backoffice_web.chronicles.list_chronicles", **form.raw_data)
    next_pages_urls = search_utils.pagination_links(form_url, int(form.page.data), paginated_chronicles.pages)

    form.page.data = 1  # Reset to first page when form is submitted ("Appliquer" clicked)
    return render_template(
        "chronicles/list.html",
        rows=paginated_chronicles,
        form=form,
        next_pages_urls=next_pages_urls,
        chronicle_publication_form=EmptyForm(),
    )


@chronicles_blueprint.route("/<int:chronicle_id>/pubish", methods=["POST"])
@atomic()
@permission_required(perm_models.Permissions.MANAGE_CHRONICLE)
def publish_chronicle(chronicle_id: int) -> utils.BackofficeResponse:
    if not FeatureToggle.WIP_ENABLE_CHRONICLES_IN_BO.is_active():
        raise NotFound()

    chronicle = chronicles_models.Chronicle.query.get_or_404(chronicle_id)
    chronicle.isActive = True
    db.session.add(chronicle)
    db.session.flush()
    history_api.add_action(
        history_models.ActionType.CHRONICLE_PUBLISHED,
        author=current_user,
        chronicle=chronicle,
    )
    flash(f"La chronique {chronicle_id} à été publiée", "success")
    return redirect(url_for("backoffice_web.chronicles.list_chronicles"), code=303)


@chronicles_blueprint.route("/<int:chronicle_id>/unpublish", methods=["POST"])
@atomic()
@permission_required(perm_models.Permissions.MANAGE_CHRONICLE)
def unpublish_chronicle(chronicle_id: int) -> utils.BackofficeResponse:
    if not FeatureToggle.WIP_ENABLE_CHRONICLES_IN_BO.is_active():
        raise NotFound()

    chronicle = chronicles_models.Chronicle.query.get_or_404(chronicle_id)
    chronicle.isActive = False
    db.session.add(chronicle)
    db.session.flush()
    history_api.add_action(
        history_models.ActionType.CHRONICLE_UNPUBLISHED,
        author=current_user,
        chronicle=chronicle,
    )
    flash(f"La chronique {chronicle_id} à été dépubliée", "success")
    return redirect(url_for("backoffice_web.chronicles.list_chronicles"), code=303)
