import itertools

from flask import redirect
from flask import request
from flask.helpers import flash
from flask.helpers import url_for
from flask_admin import expose
from flask_admin.contrib.sqla.fields import QuerySelectMultipleField
from flask_admin.form import SecureForm
from sqlalchemy.orm import joinedload
from werkzeug.wrappers import Response
from wtforms import StringField
from wtforms import validators

from pcapi.admin.base_configuration import BaseCustomAdminView
from pcapi.core.categories import categories
from pcapi.core.offers.api import add_criteria_to_offers
from pcapi.core.offers.api import deactivate_inappropriate_products
from pcapi.core.offers.models import Offer
from pcapi.models.criterion import Criterion
from pcapi.models.product import Product


class SearchForm(SecureForm):
    isbn = StringField(
        "ISBN",
    )
    visa = StringField(
        "Visa d'exploitation",
    )


def _select_criteria() -> list[Criterion]:
    return Criterion.query.all()


def _format_isbn(isbn: str) -> str:
    return isbn.replace("-", "").replace(" ", "")


def _is_isbn_valid(isbn: str) -> bool:
    return len(_format_isbn(isbn)) == 13


class OfferCriteriaForm(SecureForm):
    criteria = QuerySelectMultipleField(
        query_factory=_select_criteria,
        allow_blank=True,
        validators=[
            validators.DataRequired(),
        ],
    )


def _get_current_criteria_on_active_offers(offers: list[Offer]) -> dict[str, dict]:
    current_criteria_on_offers: dict[str, dict] = {}
    for offer in offers:
        if not offer.isActive:
            continue
        for criterion in offer.criteria:
            if criterion.name in current_criteria_on_offers:
                current_criteria_on_offers[criterion.name]["count"] += 1
            else:
                current_criteria_on_offers[criterion.name] = {"count": 1, "criterion": criterion}

    return current_criteria_on_offers


def _get_products_compatible_status(products: list[Product]) -> dict[str, str]:
    if all(product.isGcuCompatible for product in products):
        return {
            "status": "compatible_products",
            "text": "Oui",
        }

    if all(not product.isGcuCompatible for product in products):
        return {
            "status": "incompatible_products",
            "text": "Non",
        }

    return {
        "status": "partially_incompatible_products",
        "text": "Partiellement",
    }


def _get_product_type(product: Product) -> str:
    if product.subcategory.category_id == categories.FILM.id:
        return "cinema"
    if product.subcategory.category_id == categories.LIVRE.id:
        return "book"

    return "unknown"


class ManyOffersOperationsView(BaseCustomAdminView):
    @expose("/", methods=["GET", "POST"])
    def search(self) -> Response:
        form = SearchForm()
        if request.method == "POST":
            form = SearchForm(request.form)
            isbn = form.isbn.data if form.isbn else None
            visa = form.visa.data if form.visa else None
            if isbn:
                if not _is_isbn_valid(isbn):
                    flash("L'ISBN doit être composé de 13 caractères", "error")
                    return self.render("admin/search_many_offers.html", form=form)

                return redirect(url_for(".edit", isbn=_format_isbn(isbn)))

            if visa:
                return redirect(url_for(".edit", visa=visa))

            flash("Veuillez renseigner un ISBN ou un visa d'exploitation", "error")

        return self.render("admin/search_many_offers.html", form=form)

    @expose("/edit", methods=["GET"])
    def edit(self) -> Response:
        isbn = request.args.get("isbn")
        visa = request.args.get("visa")
        if not isbn and not visa:
            flash("Veuillez renseigner un ISBN ou un visa d'exploitation", "error")
            return redirect(url_for(".search"))

        if isbn:
            products = (
                Product.query.filter(Product.extraData["isbn"].astext == isbn)
                .options(joinedload(Product.offers).joinedload(Offer.criteria))
                .all()
            )

        if visa:
            products = (
                Product.query.filter(Product.extraData["visa"].astext == visa)
                .options(joinedload(Product.offers).joinedload(Offer.criteria))
                .all()
            )

        if not products:
            flash("Aucun livre n'a été trouvé avec cet ISBN ou ce visa d'exploitation", "error")
            return redirect(url_for(".search"))

        offer_criteria_form = OfferCriteriaForm()

        offers = list(itertools.chain.from_iterable(p.offers for p in products))
        active_offers_number = len([offer for offer in offers if offer.isActive])
        inactive_offers_number = len(offers) - active_offers_number
        current_criteria_on_offers = _get_current_criteria_on_active_offers(offers)
        current_criteria_on_all_offers = []

        for _, value in current_criteria_on_offers.items():
            if value["count"] == active_offers_number:
                current_criteria_on_all_offers.append(value["criterion"])

        if len(current_criteria_on_all_offers) > 0:
            offer_criteria_form.criteria.data = current_criteria_on_all_offers

        context = {
            "name": products[0].name,
            "type": _get_product_type(products[0]),
            "active_offers_number": active_offers_number,
            "inactive_offers_number": inactive_offers_number,
            "isbn": isbn,
            "offer_criteria_form": offer_criteria_form,
            "current_criteria_on_offers": current_criteria_on_offers,
            "product_compatibility": _get_products_compatible_status(products),
            "visa": visa,
        }

        return self.render("admin/edit_many_offers.html", **context)

    @expose("/add_criteria_to_offers", methods=["POST"])
    def add_criteria_to_offers(self) -> Response:
        isbn = request.args.get("isbn")
        visa = request.args.get("visa")
        if not isbn and not visa:
            flash("Veuillez renseigner un ISBN ou un visa d'exploitation", "error")
            return redirect(url_for(".search"))

        form = OfferCriteriaForm(request.form)
        if form.validate():
            is_operation_successful = add_criteria_to_offers(form.data["criteria"], isbn=isbn, visa=visa)
            if is_operation_successful:
                flash("Les offres du produit ont bien été tagguées", "success")
                return redirect(url_for(".search"))

            flash("Une erreur s'est produite lors de l'opération", "error")
            return redirect(url_for(".search"))

        flash("Le formulaire est invalide")
        return redirect(url_for(".edit"))

    @expose("/product_gcu_compatibility", methods=["POST"])
    def product_gcu_compatibility(self) -> Response:
        isbn = request.args.get("isbn")
        if not isbn:
            flash("Veuillez renseigner un ISBN", "error")
            return redirect(url_for(".search"))

        is_operation_successful = deactivate_inappropriate_products(isbn)
        if is_operation_successful:
            flash("Le produit a été rendu incompatible aux CGU et les offres ont été désactivées", "success")
        else:
            flash("Une erreur s'est produite lors de l'opération", "error")
        return redirect(url_for(".search"))
