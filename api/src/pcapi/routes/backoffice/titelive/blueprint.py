import pydantic.v1 as pydantic_v1
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup

from pcapi.connectors.serialization import titelive_serializers
from pcapi.connectors.titelive import GtlIdError
from pcapi.connectors.titelive import get_by_ean13
from pcapi.core.fraud import models as fraud_models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers.titelive_book_search import get_ineligibility_reasons
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.repository.session_management import mark_transaction_as_invalid
from pcapi.utils import requests

from .. import utils
from . import forms


titelive_blueprint = utils.child_backoffice_blueprint(
    "titelive",
    __name__,
    url_prefix="/pro/titelive",
    permission=perm_models.Permissions.READ_OFFERS,
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

    try:
        data = pydantic_v1.parse_obj_as(titelive_serializers.TiteLiveBookWork, json["oeuvre"])
    except Exception:
        ineligibility_reasons = None
    else:
        ineligibility_reasons = get_ineligibility_reasons(data.article[0], data.titre)

    product_whitelist = (
        db.session.query(fraud_models.ProductWhitelist)
        .filter(fraud_models.ProductWhitelist.ean == ean)
        .options(
            sa_orm.load_only(
                fraud_models.ProductWhitelist.ean,
                fraud_models.ProductWhitelist.dateCreated,
                fraud_models.ProductWhitelist.comment,
                fraud_models.ProductWhitelist.authorId,
            ),
            sa_orm.joinedload(fraud_models.ProductWhitelist.author).load_only(
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
        ineligibility_reasons=ineligibility_reasons,
        product_whitelist=product_whitelist,
    )


@titelive_blueprint.route("/<string:ean>/<string:title>/add-product-whitelist-confirmation-form", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_add_product_whitelist_confirmation_form(ean: str, title: str) -> utils.BackofficeResponse:
    form = forms.OptionalCommentForm()
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.titelive.add_product_whitelist", ean=ean, title=title),
        div_id="add-whitelist-confirmation",
        title="Ajouter à la whitelist",
        button_text="Ajouter",
    )


@titelive_blueprint.route("/<string:ean>/<string:title>/add", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def add_product_whitelist(ean: str, title: str) -> utils.BackofficeResponse:
    form = forms.OptionalCommentForm()
    try:
        product = offers_api.whitelist_product(ean)
    except offers_exceptions.TiteLiveAPINotExistingEAN:
        flash(Markup("L'EAN <b>{ean}</b> n'existe pas chez Titelive").format(ean=ean), "warning")
    except GtlIdError:
        flash(
            Markup("L'EAN <b>{ean}</b> n'a pas de GTL ID chez Titelive").format(ean=ean),
            "warning",
        )
    else:
        try:
            product_whitelist = fraud_models.ProductWhitelist(
                comment=form.comment.data, ean=ean, title=title, authorId=current_user.id
            )
            db.session.add(product_whitelist)
            db.session.flush()
        except sa.exc.IntegrityError as error:
            mark_transaction_as_invalid()
            flash(
                Markup("L'EAN <b>{ean}</b> n'a pas été ajouté dans la whitelist :<br/>{error}").format(
                    ean=ean, error=error
                ),
                "warning",
            )
        except GtlIdError:
            mark_transaction_as_invalid()
            flash(
                Markup("L'EAN <b>{ean}</b> n'a pas de GTL ID côté Titelive").format(ean=ean),
                "warning",
            )
        else:
            flash(Markup("L'EAN <b>{ean}</b> a été ajouté dans la whitelist").format(ean=ean), "success")

            if product:
                offers_api.revalidate_offers_after_product_whitelist(product, current_user)

    return redirect(url_for(".search_titelive", ean=ean), code=303)


@titelive_blueprint.route("/<string:ean>/delete", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def delete_product_whitelist(ean: str) -> utils.BackofficeResponse:
    try:
        product_whitelist = (
            db.session.query(fraud_models.ProductWhitelist)
            .filter(fraud_models.ProductWhitelist.ean == ean)
            .one_or_none()
        )
        if not product_whitelist:
            flash(Markup("L'EAN <b>{ean}</b> n'existe pas dans la whitelist").format(ean=ean), "warning")
        else:
            db.session.delete(product_whitelist)
            db.session.flush()
    except sa.exc.IntegrityError as error:
        mark_transaction_as_invalid()
        flash(
            Markup("Impossible de supprimer l'EAN <b>{ean}</b> de la whitelist :<br/>{error}").format(
                ean=ean, error=error
            ),
            "warning",
        )
    else:
        flash(Markup("L'EAN <b>{ean}</b> a été supprimé de la whitelist").format(ean=ean), "success")

    return redirect(url_for(".search_titelive", ean=ean), code=303)
