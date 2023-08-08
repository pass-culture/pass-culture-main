import datetime

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
import sqlalchemy as sa
from sqlalchemy import orm

from pcapi.connectors.titelive import GtlIdError
from pcapi.connectors.titelive import get_by_ean13
from pcapi.core import search
from pcapi.core.fraud import models as fraud_models
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers.api import whitelist_product
import pcapi.core.offers.models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.utils import requests

from . import forms
from .. import utils


titelive_blueprint = utils.child_backoffice_blueprint(
    "titelive",
    __name__,
    url_prefix="/pro/titelive",
    permission=perm_models.Permissions.PRO_FRAUD_ACTIONS,
)


@titelive_blueprint.route("/", methods=["GET"])
def search_titelive() -> utils.BackofficeResponse:
    if not request.args:
        return render_template(
            "titelive/search_result.html", form=forms.SearchEanForm(), dst=url_for(".search_titelive")
        )

    form = forms.SearchEanForm(formdata=utils.get_query_params())

    if not form.validate():
        return render_template("titelive/search_result.html", form=form, dst=url_for(".search_titelive")), 400

    ean = form.ean.data

    try:
        json = get_by_ean13(ean)
    except offers_exceptions.TiteLiveAPINotExistingEAN:
        form.ean.errors.append("EAN-13 introuvable")
        return render_template("titelive/search_result.html", form=form, dst=url_for(".search_titelive")), 400
    except requests.exceptions.Timeout:
        form.ean.errors.append("Erreur API Tite Live: timeout")
        return render_template("titelive/search_result.html", form=form, dst=url_for(".search_titelive")), 400
    except requests.ExternalAPIException as e:
        status_code = e.args[0]["status_code"]
        form.ean.errors.append(f"Erreur API Tite Live: {status_code}")
        return render_template("titelive/search_result.html", form=form, dst=url_for(".search_titelive")), 400

    product_whitelist = (
        fraud_models.ProductWhitelist.query.filter(fraud_models.ProductWhitelist.ean == ean)
        .options(
            orm.load_only(
                fraud_models.ProductWhitelist.ean,
                fraud_models.ProductWhitelist.dateCreated,
                fraud_models.ProductWhitelist.comment,
                fraud_models.ProductWhitelist.authorId,
            ),
            orm.joinedload(fraud_models.ProductWhitelist.author).load_only(
                users_models.User.firstName, users_models.User.lastName
            ),
        )
        .one_or_none()
    )
    return render_template(
        "titelive/search_result.html",
        form=form,
        dst=url_for(".search_titelive"),
        json=json,
        product_whitelist=product_whitelist,
    )


@titelive_blueprint.route("/<string:ean>/<string:title>/add-product-whitelist-confirmation-form", methods=["GET"])
def get_add_product_whitelist_confirmation_form(ean: str, title: str) -> utils.BackofficeResponse:
    form = forms.OptionalCommentForm()
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_v3_web.titelive.add_product_whitelist", ean=ean, title=title),
        div_id="add-whitelist-confirmation",
        title="Ajouter à la whitelist",
        button_text="Ajouter",
    )


@titelive_blueprint.route("/<string:ean>/<string:title>/add", methods=["POST"])
def add_product_whitelist(ean: str, title: str) -> utils.BackofficeResponse:
    form = forms.OptionalCommentForm()
    try:
        product = whitelist_product(ean)
    except offers_exceptions.TiteLiveAPINotExistingEAN:
        flash(f"L'EAN \"{ean}\" n'existe pas chez Titelive", "danger")
    else:
        try:
            product_whitelist = fraud_models.ProductWhitelist(
                comment=form.comment.data, ean=ean, title=title, authorId=current_user.id
            )
            db.session.add(product_whitelist)
            db.session.commit()
        except sa.exc.IntegrityError as error:
            db.session.rollback()
            flash(f"L'EAN \"{ean}\" n'a pas été rajouté dans la whitelist : {error}", "danger")
        except GtlIdError as gtl_error:
            db.session.rollback()
            flash(f"L'EAN \"{ean}\" n'a pas été rajouté dans la whitelist : {gtl_error}", "danger")
        else:
            flash(f'L\'EAN "{ean}" a été ajouté dans la whitelist', "success")

            if product:
                offers_query = offers_models.Offer.query.filter(
                    offers_models.Offer.productId == product.id,
                    offers_models.Offer.validation == offers_models.OfferValidationStatus.REJECTED,
                    offers_models.Offer.lastValidationType == OfferValidationType.CGU_INCOMPATIBLE_PRODUCT,
                )
                offer_ids = [o.id for o in offers_query.with_entities(offers_models.Offer.id)]

                if offer_ids:
                    offers_query.update(
                        values={
                            "validation": offers_models.OfferValidationStatus.APPROVED,
                            "lastValidationDate": datetime.datetime.utcnow(),
                            "lastValidationType": OfferValidationType.MANUAL,
                        },
                        synchronize_session=False,
                    )
                    db.session.commit()
                    search.async_index_offer_ids(offer_ids)

    return redirect(url_for(".search_titelive", ean=ean), code=303)


@titelive_blueprint.route("/<string:ean>/delete", methods=["GET"])
def delete_product_whitelist(ean: str) -> utils.BackofficeResponse:
    try:
        product_whitelist = fraud_models.ProductWhitelist.query.filter(
            fraud_models.ProductWhitelist.ean == ean
        ).one_or_none()
        if not product_whitelist:
            flash(f"L'EAN \"{ean}\" n'existe pas dans la whitelist", "warning")
        else:
            db.session.delete(product_whitelist)
            db.session.commit()
    except sa.exc.IntegrityError:
        db.session.rollback()
        flash("Impossible de supprimer l'EAN de la whitelist", "danger")
    else:
        flash(f'L\'EAN "{ean}" a été supprimé de la whitelist', "success")

    return redirect(url_for(".search_titelive", ean=ean), code=303)
