import datetime
from functools import partial

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from werkzeug.exceptions import NotFound

from pcapi.core.chronicles import models as chronicles_models
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.repository import atomic
from pcapi.repository import mark_transaction_as_invalid
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
        mark_transaction_as_invalid()
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
        sa.func.left(chronicles_models.Chronicle.content, 150).label("short_content"),
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


@chronicles_blueprint.route("/<int:chronicle_id>", methods=["GET"])
@atomic()
def details(chronicle_id: int) -> utils.BackofficeResponse:
    if not FeatureToggle.WIP_ENABLE_CHRONICLES_IN_BO.is_active():
        raise NotFound()

    chronicle = (
        chronicles_models.Chronicle.query.filter(
            chronicles_models.Chronicle.id == chronicle_id,
        )
        .options(
            joinedload(chronicles_models.Chronicle.products).load_only(
                offers_models.Product.name,
                offers_models.Product.extraData,
            )
        )
        .one_or_none()
    )

    if not chronicle:
        raise NotFound()

    action_history = (
        history_models.ActionHistory.query.filter(history_models.ActionHistory.chronicleId == chronicle_id)
        .order_by(history_models.ActionHistory.id.desc())
        .all()
    )
    product_name = None
    for product in chronicle.products:
        if product.extraData.get("ean") == chronicle.ean:
            product_name = product.name
            break

    update_content_form = forms.UpdateContentForm(content=chronicle.content)
    attach_product_form = forms.AttachProductForm()

    return render_template(
        "chronicles/details.html",
        chronicle=chronicle,
        product_name=product_name,
        active_tab=request.args.get("active_tab", "content"),
        chronicle_publication_form=EmptyForm(),
        update_content_form=update_content_form,
        empty_form=EmptyForm(),
        attach_product_form=attach_product_form,
        action_history=action_history,
        comment_form=forms.CommentForm(),
    )


@chronicles_blueprint.route("/<int:chronicle_id>/update-content", methods=["POST"])
@atomic()
@permission_required(perm_models.Permissions.MANAGE_CHRONICLE)
def update_chronicle_content(chronicle_id: int) -> utils.BackofficeResponse:
    if not FeatureToggle.WIP_ENABLE_CHRONICLES_IN_BO.is_active():
        raise NotFound()

    form = forms.UpdateContentForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(
            url_for("backoffice_web.chronicles.details", chronicle_id=chronicle_id, active_tab="content"), code=303
        )

    chronicle = chronicles_models.Chronicle.query.get_or_404(chronicle_id)
    chronicle.content = form.content.data
    db.session.add(chronicle)
    db.session.flush()

    flash("Le texte de la chronique a été mis à jour", "success")
    return redirect(
        url_for("backoffice_web.chronicles.details", chronicle_id=chronicle_id, active_tab="content"), code=303
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
    flash(f"La chronique {chronicle_id} a été publiée", "success")
    return redirect(request.referrer or url_for("backoffice_web.chronicles.list_chronicles"), code=303)


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
    flash(f"La chronique {chronicle_id} a été dépubliée", "success")
    return redirect(request.referrer or url_for("backoffice_web.chronicles.list_chronicles"), code=303)


@chronicles_blueprint.route("/<int:chronicle_id>/attach-product", methods=["POST"])
@atomic()
@permission_required(perm_models.Permissions.MANAGE_CHRONICLE)
def attach_product(chronicle_id: int) -> utils.BackofficeResponse:
    if not FeatureToggle.WIP_ENABLE_CHRONICLES_IN_BO.is_active():
        raise NotFound()

    form = forms.AttachProductForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        redirect(url_for("backoffice_web.chronicles.details", chronicle_id=chronicle_id), code=303)

    chronicle = chronicles_models.Chronicle.query.get_or_404(chronicle_id)
    products = offers_models.Product.query.filter(offers_models.Product.extraData["ean"].astext == form.ean.data).all()

    if not products:
        mark_transaction_as_invalid()
        flash("Aucune œuvre n'a été trouvée pour cet EAN", "warning")
        return redirect(
            url_for("backoffice_web.chronicles.details", chronicle_id=chronicle_id, active_tab="book"), code=303
        )

    for product in products:
        chronicle.products.append(product)
        db.session.add(product)

    if len(products) > 1:
        product_names = ", ".join(product.name for product in products)
        flash(
            Markup("Les produits <b>{product_names}</b> ont été rattachés à la chronique").format(
                product_names=product_names
            ),
            "success",
        )
    else:
        flash(
            Markup("Le produit <b>{product_name}</b> a été rattaché à la chronique").format(
                product_name=products[0].name
            ),
            "success",
        )
    db.session.flush()

    return redirect(
        url_for("backoffice_web.chronicles.details", chronicle_id=chronicle_id, active_tab="book"), code=303
    )


@chronicles_blueprint.route("/<int:chronicle_id>/detach-product/<int:product_id>", methods=["POST"])
@atomic()
@permission_required(perm_models.Permissions.MANAGE_CHRONICLE)
def detach_product(chronicle_id: int, product_id: int) -> utils.BackofficeResponse:
    if not FeatureToggle.WIP_ENABLE_CHRONICLES_IN_BO.is_active():
        raise NotFound()

    deleted = chronicles_models.ProductChronicle.query.filter(
        chronicles_models.ProductChronicle.productId == product_id,
        chronicles_models.ProductChronicle.chronicleId == chronicle_id,
    ).delete(synchronize_session=False)
    db.session.flush()

    if deleted:
        flash("Le produit à bien été détaché de la chronique", "success")
    else:
        mark_transaction_as_invalid()
        flash("Le produit n'existe pas ou n'était pas attaché à la chronique", "warning")

    return redirect(
        url_for("backoffice_web.chronicles.details", chronicle_id=chronicle_id, active_tab="book"), code=303
    )


@chronicles_blueprint.route("/<int:chronicle_id>/comment", methods=["POST"])
@atomic()
def comment_chronicle(chronicle_id: int) -> utils.BackofficeResponse:
    if not FeatureToggle.WIP_ENABLE_CHRONICLES_IN_BO.is_active():
        raise NotFound()

    form = forms.CommentForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        redirect(
            url_for("backoffice_web.chronicles.details", chronicle_id=chronicle_id, active_tab="history"), code=303
        )

    chronicle = chronicles_models.Chronicle.query.get_or_404(chronicle_id)

    history_api.add_action(
        history_models.ActionType.COMMENT, author=current_user, chronicle=chronicle, comment=form.comment.data
    )
    flash("Le commentaire a été enregistré", "success")
    return redirect(
        url_for("backoffice_web.chronicles.details", chronicle_id=chronicle_id, active_tab="history"), code=303
    )
