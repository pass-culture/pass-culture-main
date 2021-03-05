from typing import Dict
from typing import List

from flask import redirect
from flask import request
from flask.helpers import flash
from flask.helpers import url_for
from flask_admin import BaseView
from flask_admin import expose
from flask_admin.contrib.sqla.fields import QuerySelectMultipleField
from flask_admin.form import SecureForm
from sqlalchemy.orm import joinedload
from wtforms import StringField
from wtforms import validators

from pcapi.core.offers.api import add_criteria_to_offers
from pcapi.core.offers.models import Offer
from pcapi.models.criterion import Criterion
from pcapi.models.product import Product


class SearchForm(SecureForm):
    isbn = StringField(
        "ISBN",
        [
            validators.DataRequired(),
        ],
    )


def _select_criteria() -> List[Criterion]:
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


def _get_current_criteria_on_offers(offers: List[Offer]) -> Dict[str, Dict]:
    current_criteria_on_offers: Dict[str, Dict] = {}
    for offer in offers:
        for criterion in offer.criteria:
            if criterion.name in current_criteria_on_offers:
                current_criteria_on_offers[criterion.name]["count"] += 1
            else:
                current_criteria_on_offers[criterion.name] = {"count": 1, "criterion": criterion}

    return current_criteria_on_offers


class ManyOffersOperationsView(BaseView):
    @expose("/", methods=["GET", "POST"])
    def search(self):
        form = SearchForm()
        if request.method == "POST":
            form = SearchForm(request.form)
            if form.validate():
                isbn = form.isbn.data
                if _is_isbn_valid(isbn):
                    return redirect(url_for(".edit", isbn=_format_isbn(isbn)))
                flash("L'ISBN doit être composé de 13 caractères", "error")
            else:
                flash("Veuillez renseigner un ISBN", "error")

        return self.render("admin/search_many_offers.html", form=form)

    @expose("/edit", methods=["GET", "POST"])
    def edit(self):
        isbn = request.args.get("isbn")
        if not isbn:
            flash("Veuillez renseigner un ISBN valide", "error")
            return redirect(url_for(".search"))

        if request.method == "POST":
            form = OfferCriteriaForm(request.form)
            if form.validate():
                is_operation_successful = add_criteria_to_offers(form.data["criteria"], isbn)
                if is_operation_successful:
                    flash("Les offres du produit ont bien été tagguées", "success")
                    return redirect(url_for(".search"))

                flash("Une erreur s'est produite lors de l'opération", "error")
                return redirect(url_for(".search"))

        product = (
            Product.query.filter(Product.extraData["isbn"].astext == isbn)
            .options(joinedload(Product.offers).joinedload(Offer.criteria))
            .first()
        )
        if not product or len(product.offers) == 0:
            flash("Aucune offre n'a été trouvée avec cet ISBN", "error")
            return redirect(url_for(".search"))

        offer_criteria_form = OfferCriteriaForm()

        offers = product.offers
        current_criteria_on_offers = _get_current_criteria_on_offers(offers)
        current_criteria_on_all_offers = []

        for _, value in current_criteria_on_offers.items():
            if value["count"] == len(offers):
                current_criteria_on_all_offers.append(value["criterion"])

        if len(current_criteria_on_all_offers) > 0:
            offer_criteria_form.criteria.data = current_criteria_on_all_offers

        context = {
            "name": product.name,
            "offers_number": len(offers),
            "isbn": isbn,
            "offer_criteria_form": offer_criteria_form,
            "current_criteria_on_offers": current_criteria_on_offers,
        }

        return self.render("admin/edit_many_offers.html", **context)
