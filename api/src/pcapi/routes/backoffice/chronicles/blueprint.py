import datetime
from functools import partial

import sqlalchemy as sa
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
from sqlalchemy import orm as sa_orm
from werkzeug.exceptions import NotFound

from pcapi.core.chronicles import api as chronicles_api
from pcapi.core.chronicles import models as chronicles_models
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.models import db
from pcapi.models.utils import get_or_404
from pcapi.routes.backoffice import search_utils
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.forms.empty import EmptyForm
from pcapi.routes.backoffice.search_utils import paginate
from pcapi.routes.backoffice.utils import permission_required
from pcapi.utils import string as string_utils
from pcapi.utils.transaction_manager import mark_transaction_as_invalid

from . import forms


chronicles_blueprint = utils.child_backoffice_blueprint(
    "chronicles",
    __name__,
    url_prefix="/chronicles/",
    permission=perm_models.Permissions.READ_CHRONICLE,
)


def _get_chronicle_query() -> sa_orm.Query:
    product_subquery = (
        sa.select(sa.func.array_agg(offers_models.Product.name))
        .select_from(chronicles_models.ProductChronicle)
        .join(offers_models.Product, offers_models.Product.id == chronicles_models.ProductChronicle.productId)
        .filter(chronicles_models.ProductChronicle.chronicleId == chronicles_models.Chronicle.id)
        .scalar_subquery()
    )

    offer_subquery = (
        sa.select(sa.func.array_agg(offers_models.Offer.name))
        .select_from(chronicles_models.OfferChronicle)
        .join(offers_models.Offer, offers_models.Offer.id == chronicles_models.OfferChronicle.offerId)
        .filter(chronicles_models.OfferChronicle.chronicleId == chronicles_models.Chronicle.id)
        .scalar_subquery()
    )

    query = db.session.query(
        chronicles_models.Chronicle.id,
        chronicles_models.Chronicle.content,
        sa.func.left(chronicles_models.Chronicle.content, 150).label("short_content"),
        chronicles_models.Chronicle.dateCreated,
        chronicles_models.Chronicle.isActive,
        chronicles_models.Chronicle.isSocialMediaDiffusible,
        product_subquery.label("products"),
        offer_subquery.label("offers"),
    )
    return query


@chronicles_blueprint.route("", methods=["GET"])
def list_chronicles() -> utils.BackofficeResponse:
    form = forms.GetChronicleSearchForm(formdata=utils.get_query_params())
    if not form.validate():
        mark_transaction_as_invalid()
        return render_template("chronicles/list.html", rows=[], form=form), 400

    query = _get_chronicle_query()

    q_filters = []
    product_identifier = string_utils.format_ean_or_visa(form.q.data) if form.q.data else None
    if product_identifier and string_utils.is_numeric(product_identifier):
        query = query.join(chronicles_models.Chronicle.products)
        product_identifier = form.q.data
        q_filters.append(
            sa.or_(
                offers_models.Product.ean == product_identifier,
                offers_models.Product.extraData.op("->")("allocineId") == product_identifier,
                offers_models.Product.extraData["visa"].astext == product_identifier,
            )
        )
    elif form.q.data:
        if form.search_type.data in (forms.SearchType.ALL.name, forms.SearchType.CHRONICLE_CONTENT.name):
            q_filters.append(
                sa.and_(
                    *[
                        chronicles_models.Chronicle._content_ts_vector.op("@@")(sa.func.plainto_tsquery("french", w))
                        for w in form.q.data.split(" ")
                        if len(w) > 1
                    ]
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

    if form.is_active.data and len(form.is_active.data) == 1:
        query = query.filter(chronicles_models.Chronicle.isActive.is_(form.is_active.data[0] == "true"))

    if form.social_media_diffusible.data and len(form.social_media_diffusible.data) == 1:
        query = query.filter(
            chronicles_models.Chronicle.isSocialMediaDiffusible.is_(form.social_media_diffusible.data[0] == "true"),
        )

    if form.category.data and len(form.category.data) != len(chronicles_models.ChronicleClubType):
        query = query.filter(
            chronicles_models.Chronicle.clubType.in_(
                [chronicles_models.ChronicleClubType[club_type] for club_type in form.category.data]
            )
        )

    query = query.order_by(chronicles_models.Chronicle.id.desc())

    paginated_chronicles = paginate(
        query=query,
        page=int(form.page.data),
        per_page=int(form.limit.data),
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


def _render_chronicle_row(chronicle_id: int) -> utils.BackofficeResponse:
    row = _get_chronicle_query().filter(chronicles_models.Chronicle.id == chronicle_id).first()
    return render_template("chronicles/list_rows.html", chronicles=[row])


@chronicles_blueprint.route("/<int:chronicle_id>", methods=["GET"])
def details(chronicle_id: int) -> utils.BackofficeResponse:
    chronicle = (
        db.session.query(chronicles_models.Chronicle)
        .filter(
            chronicles_models.Chronicle.id == chronicle_id,
        )
        .options(
            sa_orm.joinedload(chronicles_models.Chronicle.products).load_only(
                offers_models.Product.name,
                offers_models.Product.ean,
                offers_models.Product.extraData,
            ),
            sa_orm.joinedload(chronicles_models.Chronicle.offers).load_only(
                offers_models.Offer.id,
                offers_models.Offer.name,
            ),
        )
        .one_or_none()
    )

    if not chronicle:
        raise NotFound()

    action_history = (
        db.session.query(history_models.ActionHistory)
        .filter(history_models.ActionHistory.chronicleId == chronicle_id)
        .order_by(history_models.ActionHistory.id.desc())
        .all()
    )
    product_name = None
    if chronicle.productIdentifierType == chronicles_models.ChronicleProductIdentifierType.OFFER_ID:
        for offer in chronicle.offers:
            if chronicle.productIdentifier == offer.id:
                product_name = offer.name
                break
    else:
        for product in chronicle.products:
            product_identifier = chronicles_api.get_product_identifier(chronicle, product)
            if product_identifier == chronicle.productIdentifier:
                product_name = product.name
                break

    return render_template(
        "chronicles/details.html",
        chronicle=chronicle,
        product_name=product_name,
        active_tab=request.args.get("active_tab", "content"),
        chronicle_publication_form=EmptyForm(),
        empty_form=EmptyForm(),
        attach_product_form=forms.AttachProductForm(),
        action_history=action_history,
        comment_form=forms.CommentForm(),
        attach_offer_form=forms.AttachOfferForm(),
    )


@chronicles_blueprint.route("/<int:chronicle_id>/update-content", methods=["GET"])
@permission_required(perm_models.Permissions.MANAGE_CHRONICLE)
def get_update_chronicle_content_form(chronicle_id: int) -> utils.BackofficeResponse:
    chronicle = get_or_404(chronicles_models.Chronicle, chronicle_id)
    form = forms.UpdateContentForm(content=chronicle.content)

    kwargs = {
        "form": form,
        "dst": url_for(".update_chronicle_content", chronicle_id=chronicle_id),
        "div_id": f"update-chronicle-content-{chronicle_id}",  # must be consistent with parameter passed to build_lazy_modal
        "title": "Modifier le contenu de la chronique",
        "button_text": "Enregistrer",
        "ajax_submit": utils.is_request_from_htmx(),
    }

    if kwargs["ajax_submit"]:
        kwargs["target_id"] = f"#chronicle-row-{chronicle_id}"

    return render_template("components/dynamic/modal_form.html", **kwargs)


@chronicles_blueprint.route("/<int:chronicle_id>/update-content", methods=["POST"])
@permission_required(perm_models.Permissions.MANAGE_CHRONICLE)
def update_chronicle_content(chronicle_id: int) -> utils.BackofficeResponse:
    form = forms.UpdateContentForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(
            url_for("backoffice_web.chronicles.details", chronicle_id=chronicle_id, active_tab="content"), code=303
        )

    chronicle = get_or_404(chronicles_models.Chronicle, chronicle_id)
    chronicle.content = form.content.data
    db.session.add(chronicle)
    db.session.flush()

    flash(
        Markup("Le texte de la chronique <b>{chronicle_id}</b> a été mis à jour").format(chronicle_id=chronicle_id),
        "success",
    )

    if utils.is_request_from_htmx():
        return _render_chronicle_row(chronicle_id)
    return redirect(
        request.referrer
        or url_for("backoffice_web.chronicles.details", chronicle_id=chronicle_id, active_tab="content"),
        code=303,
    )


@chronicles_blueprint.route("/<int:chronicle_id>/publish", methods=["POST"])
@permission_required(perm_models.Permissions.MANAGE_CHRONICLE)
def publish_chronicle(chronicle_id: int) -> utils.BackofficeResponse:
    chronicle = get_or_404(chronicles_models.Chronicle, chronicle_id)
    chronicle.isActive = True
    db.session.add(chronicle)
    db.session.flush()
    history_api.add_action(
        history_models.ActionType.CHRONICLE_PUBLISHED,
        author=current_user,
        chronicle=chronicle,
    )
    flash(f"La chronique {chronicle_id} a été publiée", "success")
    if utils.is_request_from_htmx():
        return _render_chronicle_row(chronicle_id)
    return redirect(request.referrer or url_for("backoffice_web.chronicles.list_chronicles"), code=303)


@chronicles_blueprint.route("/<int:chronicle_id>/unpublish", methods=["POST"])
@permission_required(perm_models.Permissions.MANAGE_CHRONICLE)
def unpublish_chronicle(chronicle_id: int) -> utils.BackofficeResponse:
    chronicle = get_or_404(chronicles_models.Chronicle, chronicle_id)
    chronicle.isActive = False
    db.session.add(chronicle)
    db.session.flush()
    history_api.add_action(
        history_models.ActionType.CHRONICLE_UNPUBLISHED,
        author=current_user,
        chronicle=chronicle,
    )
    flash(f"La chronique {chronicle_id} a été dépubliée", "success")

    if utils.is_request_from_htmx():
        return _render_chronicle_row(chronicle_id)
    return redirect(request.referrer or url_for("backoffice_web.chronicles.list_chronicles"), code=303)


@chronicles_blueprint.route("/<int:chronicle_id>/attach-product", methods=["POST"])
@permission_required(perm_models.Permissions.MANAGE_CHRONICLE)
def attach_product(chronicle_id: int) -> utils.BackofficeResponse:
    selected_chronicle = get_or_404(chronicles_models.Chronicle, chronicle_id)

    form = forms.AttachProductForm()

    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        redirect(
            url_for("backoffice_web.chronicles.details", chronicle_id=chronicle_id, active_tab="product"), code=303
        )

    product_identifier = str(form.product_identifier.data)

    products_subquery = (
        sa.select(sa.func.array_agg(chronicles_models.ProductChronicle.productId))
        .filter(
            chronicles_models.ProductChronicle.chronicleId == chronicles_models.Chronicle.id,
        )
        .correlate(
            chronicles_models.Chronicle,
        )
        .scalar_subquery()
    )

    chronicle_query = db.session.query(chronicles_models.Chronicle, products_subquery.label("products")).filter(
        chronicles_models.Chronicle.productIdentifier == selected_chronicle.productIdentifier,
        chronicles_models.Chronicle.productIdentifierType == selected_chronicle.productIdentifierType,
    )

    match form.product_identifier_type.data:
        case chronicles_models.ChronicleProductIdentifierType.ALLOCINE_ID.name:
            products = (
                db.session.query(offers_models.Product)
                .filter(offers_models.Product.extraData.op("->")("allocineId") == product_identifier)
                .all()
            )
        case chronicles_models.ChronicleProductIdentifierType.EAN.name:
            products = (
                db.session.query(offers_models.Product).filter(offers_models.Product.ean == product_identifier).all()
            )
        case chronicles_models.ChronicleProductIdentifierType.VISA.name:
            products = (
                db.session.query(offers_models.Product)
                .filter(offers_models.Product.extraData["visa"].astext == product_identifier)
                .all()
            )
        case _:
            products = []

    if not products:
        mark_transaction_as_invalid()
        flash("Aucune œuvre n'a été trouvée pour cet identifiant", "warning")
        return redirect(
            url_for("backoffice_web.chronicles.details", chronicle_id=chronicle_id, active_tab="product"), code=303
        )

    for product in products:
        for chronicle, products_id in chronicle_query:
            if not (products_id and product.id in products_id):
                chronicle.products.append(product)

    db.session.flush()

    if len(products) > 1:
        product_names = ", ".join(product.name for product in products)
        flash(
            Markup(
                "Les produits <b>{product_names}</b> ont été rattachés à toutes les chroniques sur la même œuvre que celle-ci"
            ).format(product_names=product_names),
            "success",
        )
    else:
        flash(
            Markup(
                "Le produit <b>{product_name}</b> a été rattaché à toutes les chroniques sur la même œuvre que celle-ci"
            ).format(product_name=products[0].name),
            "success",
        )

    return redirect(
        url_for("backoffice_web.chronicles.details", chronicle_id=chronicle_id, active_tab="product"), code=303
    )


@chronicles_blueprint.route("/<int:chronicle_id>/detach-product/<int:product_id>", methods=["POST"])
@permission_required(perm_models.Permissions.MANAGE_CHRONICLE)
def detach_product(chronicle_id: int, product_id: int) -> utils.BackofficeResponse:
    selected_chronicle = get_or_404(chronicles_models.Chronicle, chronicle_id)
    chronicles_subquery = (
        db.session.query(chronicles_models.Chronicle)
        .filter(
            sa.or_(
                sa.and_(
                    chronicles_models.Chronicle.productIdentifier == selected_chronicle.productIdentifier,
                    ~chronicles_models.Chronicle.productIdentifier.is_(None),
                ),
                chronicles_models.Chronicle.id == chronicle_id,
            )
        )
        .with_entities(chronicles_models.Chronicle.id)
    )
    deleted = (
        db.session.query(chronicles_models.ProductChronicle)
        .filter(
            chronicles_models.ProductChronicle.productId == product_id,
            chronicles_models.ProductChronicle.chronicleId.in_(chronicles_subquery),
        )
        .delete(synchronize_session=False)
    )
    db.session.flush()

    if deleted:
        flash("Le produit a bien été détaché de toutes les chroniques sur la même œuvre que celle-ci", "success")
    else:
        mark_transaction_as_invalid()
        flash("Le produit n'existe pas ou n'était pas attaché à la chronique", "warning")

    return redirect(
        url_for("backoffice_web.chronicles.details", chronicle_id=chronicle_id, active_tab="product"), code=303
    )


@chronicles_blueprint.route("/<int:chronicle_id>/attach-offer", methods=["POST"])
@permission_required(perm_models.Permissions.MANAGE_CHRONICLE)
def attach_offer(chronicle_id: int) -> utils.BackofficeResponse:
    selected_chronicle = get_or_404(chronicles_models.Chronicle, chronicle_id)

    form = forms.AttachOfferForm()

    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        redirect(url_for("backoffice_web.chronicles.details", chronicle_id=chronicle_id, active_tab="offer"), code=303)

    offers_subquery = (
        sa.select(sa.func.array_agg(chronicles_models.OfferChronicle.offerId))
        .filter(
            chronicles_models.OfferChronicle.chronicleId == chronicles_models.Chronicle.id,
        )
        .correlate(
            chronicles_models.Chronicle,
        )
        .scalar_subquery()
    )

    chronicle_query = db.session.query(chronicles_models.Chronicle, offers_subquery.label("offers")).filter(
        chronicles_models.Chronicle.productIdentifier == selected_chronicle.productIdentifier,
        chronicles_models.Chronicle.productIdentifierType == selected_chronicle.productIdentifierType,
    )

    offer = db.session.query(offers_models.Offer).filter(offers_models.Offer.id == form.offer_id.data).one_or_none()

    if not offer:
        mark_transaction_as_invalid()
        flash("Aucune offre n'a été trouvée pour cet ID", "warning")
        return redirect(
            url_for("backoffice_web.chronicles.details", chronicle_id=chronicle_id, active_tab="offer"), code=303
        )

    for chronicle, offers_id in chronicle_query:
        if not (offers_id and int(form.offer_id.data) in offers_id):
            db.session.add(chronicles_models.OfferChronicle(offerId=int(form.offer_id.data), chronicleId=chronicle.id))

    db.session.flush()

    flash(
        Markup(
            "L'offre <b>{offer_name}</b> a été rattachée à toutes les chroniques sur la même œuvre que celle-ci"
        ).format(offer_name=offer.name),
        "success",
    )

    return redirect(
        url_for("backoffice_web.chronicles.details", chronicle_id=chronicle_id, active_tab="offer"), code=303
    )


@chronicles_blueprint.route("/<int:chronicle_id>/detach-offer/<int:offer_id>", methods=["POST"])
@permission_required(perm_models.Permissions.MANAGE_CHRONICLE)
def detach_offer(chronicle_id: int, offer_id: int) -> utils.BackofficeResponse:
    selected_chronicle = get_or_404(chronicles_models.Chronicle, chronicle_id)
    chronicles_subquery = (
        db.session.query(chronicles_models.Chronicle)
        .filter(
            sa.or_(
                sa.and_(
                    chronicles_models.Chronicle.productIdentifier == selected_chronicle.productIdentifier,
                    chronicles_models.Chronicle.productIdentifierType == selected_chronicle.productIdentifierType,
                ),
                chronicles_models.Chronicle.id == chronicle_id,
            )
        )
        .with_entities(chronicles_models.Chronicle.id)
    )
    deleted = (
        db.session.query(chronicles_models.OfferChronicle)
        .filter(
            chronicles_models.OfferChronicle.offerId == offer_id,
            chronicles_models.OfferChronicle.chronicleId.in_(chronicles_subquery),
        )
        .delete(synchronize_session=False)
    )
    db.session.flush()

    if deleted:
        flash("L'offre a bien été détachée de toutes les chroniques sur la même œuvre que celle-ci", "success")
    else:
        mark_transaction_as_invalid()
        flash("L'offre n'existe pas ou n'était pas attachée à la chronique", "warning")

    return redirect(
        url_for("backoffice_web.chronicles.details", chronicle_id=chronicle_id, active_tab="offer"), code=303
    )


@chronicles_blueprint.route("/<int:chronicle_id>/comment", methods=["POST"])
def comment_chronicle(chronicle_id: int) -> utils.BackofficeResponse:
    form = forms.CommentForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        redirect(
            url_for("backoffice_web.chronicles.details", chronicle_id=chronicle_id, active_tab="history"), code=303
        )

    chronicle = get_or_404(chronicles_models.Chronicle, chronicle_id)

    history_api.add_action(
        history_models.ActionType.COMMENT, author=current_user, chronicle=chronicle, comment=form.comment.data
    )
    flash("Le commentaire a été enregistré", "success")
    return redirect(
        url_for("backoffice_web.chronicles.details", chronicle_id=chronicle_id, active_tab="history"), code=303
    )
