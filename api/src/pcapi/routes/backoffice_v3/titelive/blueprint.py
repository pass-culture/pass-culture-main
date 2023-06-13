from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
import sqlalchemy as sa
from sqlalchemy import orm

from pcapi.connectors.titelive import get_by_ean13
from pcapi.core.fraud import models as fraud_models
from pcapi.core.offers.api import delete_unwanted_existing_product
from pcapi.core.offers.api import whitelist_existing_product
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.utils import requests

from . import forms
from .. import utils


titelive_blueprint = utils.child_backoffice_blueprint(
    "titelive",
    __name__,
    url_prefix="/pro/titelive",
    permission=perm_models.Permissions.FRAUD_ACTIONS,
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
    except requests.ExternalAPIException as e:
        status_code = e.args[0]["status_code"]
        if status_code == 404:
            form.ean.errors.append("EAN-13 introuvable")
        else:
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
        product_whitelist = fraud_models.ProductWhitelist(
            comment=form.comment.data, ean=ean, title=title, authorId=current_user.id
        )

        db.session.add(product_whitelist)
        db.session.commit()
        whitelist_existing_product(ean)
    except sa.exc.IntegrityError:
        db.session.rollback()
        flash(f'L\'EAN "{ean}" est déjà dans la whitelist', "warning")
    else:
        flash(f'L\'EAN "{ean}" a été ajouté dans la whitelist', "success")

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
            delete_unwanted_existing_product(ean)
    except sa.exc.IntegrityError:
        db.session.rollback()
        flash("Impossible de supprimer l'EAN de la whitelist", "danger")
    else:
        flash(f'L\'EAN "{ean}" a été supprimé de la whitelist', "success")

    return redirect(url_for(".search_titelive", ean=ean), code=303)
