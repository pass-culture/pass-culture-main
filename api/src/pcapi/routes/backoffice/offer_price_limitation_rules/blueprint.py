from decimal import Decimal

from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from markupsafe import Markup
import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.core.categories import subcategories_v2
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.models import db
from pcapi.repository import atomic
from pcapi.repository import mark_transaction_as_invalid
from pcapi.routes.backoffice.filters import format_offer_subcategory
from pcapi.routes.backoffice.forms import empty as empty_forms

from . import forms
from .. import utils


offer_price_limitation_rules_blueprint = utils.child_backoffice_blueprint(
    "offer_price_limitation_rules",
    __name__,
    url_prefix="/offer-price-limitation-rules",
    permission=perm_models.Permissions.PRO_FRAUD_ACTIONS,
)


@offer_price_limitation_rules_blueprint.route("", methods=["GET"])
@atomic()
def list_rules() -> utils.BackofficeResponse:
    form = forms.SearchRuleForm(formdata=utils.get_query_params())

    if not form.validate():
        return (
            render_template(
                "offer_price_limitation_rules/list_rules.html", rows=[], form=form, dst=url_for(".list_rules")
            ),
            400,
        )

    query = offers_models.OfferPriceLimitationRule.query
    if form.subcategory.data:
        query = query.filter(offers_models.OfferPriceLimitationRule.subcategoryId.in_(form.subcategory.data))
    if form.category.data:
        query = query.filter(
            offers_models.OfferPriceLimitationRule.subcategoryId.in_(
                subcategory.id
                for subcategory in subcategories_v2.ALL_SUBCATEGORIES
                if subcategory.category.id in form.category.data
            )
        )

    rules = query.all()
    rules = sorted(
        rules,
        key=(
            lambda rule: (
                subcategories_v2.ALL_SUBCATEGORIES_DICT[rule.subcategoryId].category.pro_label,
                subcategories_v2.ALL_SUBCATEGORIES_DICT[rule.subcategoryId].pro_label,
            )
        ),
    )

    return render_template(
        "offer_price_limitation_rules/list_rules.html",
        rows=rules,
        form=form,
        dst=url_for(".list_rules"),
    )


@offer_price_limitation_rules_blueprint.route("/create", methods=["GET"])
@atomic()
def get_create_offer_price_limitation_rule_form() -> utils.BackofficeResponse:
    form = forms.CreateOfferPriceLimitationRuleForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.offer_price_limitation_rules.create_rule"),
        div_id="create-offer-price-limitation-rule",  # must be consistent with parameter passed to build_lazy_modal
        title="Créer une règle de modification de prix d'offre",
        button_text="Créer la règle",
    )


@offer_price_limitation_rules_blueprint.route("/create", methods=["POST"])
@atomic()
def create_rule() -> utils.BackofficeResponse:
    form = forms.CreateOfferPriceLimitationRuleForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for("backoffice_web.offer_price_limitation_rules.list_rules"), code=303)

    rate = Decimal(form.rate.data / 100).quantize(Decimal("0.0001"))
    try:
        new_rule = offers_models.OfferPriceLimitationRule(subcategoryId=form.subcategory.data, rate=rate)
        db.session.add(new_rule)
        db.session.flush()
        flash("La nouvelle règle a été créée", "success")

    except sa.exc.IntegrityError as err:
        mark_transaction_as_invalid()
        flash(Markup("Erreur dans la création de la règle : {message}").format(message=str(err)), "warning")

    return redirect(url_for("backoffice_web.offer_price_limitation_rules.list_rules"), code=303)


@offer_price_limitation_rules_blueprint.route("/<int:rule_id>/delete", methods=["GET"])
@atomic()
def get_delete_offer_price_limitation_rule_form(rule_id: int) -> utils.BackofficeResponse:
    rule_to_delete = offers_models.OfferPriceLimitationRule.query.filter_by(id=rule_id).one_or_none()
    if not rule_to_delete:
        raise NotFound()

    return render_template(
        "components/turbo/modal_form.html",
        form=empty_forms.EmptyForm(),
        dst=url_for("backoffice_web.offer_price_limitation_rules.delete_rule", rule_id=rule_id),
        div_id=f"delete-offer-price-limitation-rule-{rule_id}",  # must be consistent with parameter passed to build_lazy_modal
        title="Supprimer une règle de modification de prix d'offre",
        button_text="Supprimer la règle",
        information=Markup(
            "La règle sur la sous-catégorie <b>{subcategory}</b> sera définitivement supprimée de la base de données. Veuillez confirmer ce choix."
        ).format(subcategory=format_offer_subcategory(rule_to_delete.subcategoryId)),
    )


@offer_price_limitation_rules_blueprint.route("/<int:rule_id>/delete", methods=["POST"])
@atomic()
def delete_rule(rule_id: int) -> utils.BackofficeResponse:
    rule_to_delete = offers_models.OfferPriceLimitationRule.query.filter_by(id=rule_id).one_or_none()
    if not rule_to_delete:
        raise NotFound()

    db.session.delete(rule_to_delete)
    db.session.flush()

    flash(
        Markup("La règle sur la sous-catégorie <b>{subcategory}</b> a été supprimée").format(
            subcategory=format_offer_subcategory(rule_to_delete.subcategoryId)
        ),
        "success",
    )

    return redirect(url_for("backoffice_web.offer_price_limitation_rules.list_rules"), code=303)


@offer_price_limitation_rules_blueprint.route("/<int:rule_id>/edit", methods=["GET"])
@atomic()
def get_edit_offer_price_limitation_rule_form(rule_id: int) -> utils.BackofficeResponse:
    rule_to_update = offers_models.OfferPriceLimitationRule.query.filter_by(id=rule_id).one_or_none()
    if not rule_to_update:
        raise NotFound()

    rate = Decimal(rule_to_update.rate * 100).quantize(Decimal("0.01"))
    form = forms.EditOfferPriceLimitationRuleForm(rate=rate)

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.offer_price_limitation_rules.edit_rule", rule_id=rule_id),
        div_id=f"edit-offer-price-limitation-rule-{rule_id}",  # must be consistent with parameter passed to build_lazy_modal
        title="Modifier une règle de modification de prix d'offre",
        button_text="Modifier la règle",
    )


@offer_price_limitation_rules_blueprint.route("/<int:rule_id>/edit", methods=["POST"])
@atomic()
def edit_rule(rule_id: int) -> utils.BackofficeResponse:
    rule_to_update = offers_models.OfferPriceLimitationRule.query.filter_by(id=rule_id).one_or_none()
    if not rule_to_update:
        raise NotFound()

    form = forms.EditOfferPriceLimitationRuleForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for("backoffice_web.offer_price_limitation_rules.list_rules"), code=303)

    rate = Decimal(form.rate.data / 100).quantize(Decimal("0.0001"))
    try:
        rule_to_update.rate = rate
        db.session.flush()

    except sa.exc.IntegrityError as exc:
        mark_transaction_as_invalid()
        flash(Markup("Une erreur s'est produite : {message}").format(message=str(exc)), "warning")
    else:
        flash(
            Markup("La règle sur la sous-catégorie <b>{subcategory}</b> a été modifiée").format(
                subcategory=format_offer_subcategory(rule_to_update.subcategoryId)
            ),
            "success",
        )

    return redirect(url_for("backoffice_web.offer_price_limitation_rules.list_rules"), code=303)
