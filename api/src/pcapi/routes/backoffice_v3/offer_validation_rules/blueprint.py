import datetime

from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from flask_login import current_user
import sqlalchemy as sa

import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
import pcapi.core.permissions.models as perm_models
import pcapi.core.users.models as users_models
from pcapi.models import db
from pcapi.routes.backoffice_v3 import autocomplete
from pcapi.routes.backoffice_v3.forms import empty as empty_forms
from pcapi.utils.clean_accents import clean_accents

from . import forms
from .. import utils


offer_validation_rules_blueprint = utils.child_backoffice_blueprint(
    "offer_validation_rules",
    __name__,
    url_prefix="/offer-validation-rules",
    permission=perm_models.Permissions.PRO_FRAUD_ACTIONS,
)


def _get_offerers_data_for_rules(rules: list[offers_models.OfferValidationRule]) -> dict:
    all_offerer_ids: set = set()
    for rule in rules:
        for sub_rule in rule.subRules:
            if (
                sub_rule.model == offers_models.OfferValidationModel.OFFERER
                and sub_rule.attribute == offers_models.OfferValidationAttribute.ID
            ):
                all_offerer_ids |= set(sub_rule.comparated["comparated"])

    offerers_from_rules = (
        offerers_models.Offerer.query.options(
            sa.orm.load_only(
                offerers_models.Offerer.id,
                offerers_models.Offerer.name,
                offerers_models.Offerer.siren,
            )
        )
        .filter(offerers_models.Offerer.id.in_(all_offerer_ids))
        .all()
    )
    offerer_dict = {offerer.id: f"{offerer.name} ({offerer.siren})" for offerer in offerers_from_rules}
    return offerer_dict


@offer_validation_rules_blueprint.route("", methods=["GET"])
def list_rules() -> utils.BackofficeResponse:
    form = forms.SearchRuleForm(formdata=utils.get_query_params())

    base_query = offers_models.OfferValidationRule.query.outerjoin(offers_models.OfferValidationSubRule).options(
        sa.orm.joinedload(offers_models.OfferValidationRule.latestAuthor).load_only(
            users_models.User.firstName, users_models.User.lastName, users_models.User.email
        )
    )

    if not form.validate():
        return (
            render_template("offer_validation_rules/list_rules.html", rows=[], form=form, dst=url_for(".list_rules")),
            400,
        )

    if form.is_empty():
        rules = base_query.all()

    else:
        query = clean_accents(form.q.data.replace(" ", "%").replace("-", "%"))
        rules = base_query.filter(
            sa.func.unaccent(offers_models.OfferValidationRule.name).ilike(f"%{query}%")
        ).distinct()

    offerer_dict = _get_offerers_data_for_rules(rules)

    return render_template(
        "offer_validation_rules/list_rules.html",
        rows=rules,
        offerer_dict=offerer_dict,
        form=form,
        dst=url_for(".list_rules"),
    )


@offer_validation_rules_blueprint.route("/create", methods=["GET"])
def get_create_offer_validation_rule_form() -> utils.BackofficeResponse:
    form = forms.CreateOfferValidationRuleForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_v3_web.offer_validation_rules.create_rule"),
        div_id="create-offer-validation-rule",  # must be consistent with parameter passed to build_lazy_modal
        title="Créer une règle de validation d'offre",
        button_text="Créer la règle",
    )


@offer_validation_rules_blueprint.route("/create", methods=["POST"])
def create_rule() -> utils.BackofficeResponse:
    form = forms.CreateOfferValidationRuleForm()

    if not form.validate():
        error_msg = utils.build_form_error_msg(form)
        flash(error_msg, "warning")
        return redirect(url_for("backoffice_v3_web.offer_validation_rules.list_rules"), code=303)

    try:
        new_rule = offers_models.OfferValidationRule(name=form.name.data, latestAuthor=current_user)
        db.session.add(new_rule)
        for sub_rule_data in form.sub_rules.data:
            comparated = (
                sub_rule_data["decimal_field"]
                or sub_rule_data["list_field"]
                or sub_rule_data["offer_type"]
                or sub_rule_data["offerer"]
                or sub_rule_data["subcategories"]
                or sub_rule_data["categories"]
                or sub_rule_data["show_sub_type"]
            )
            sub_rule = offers_models.OfferValidationSubRule(
                validationRule=new_rule,
                model=offers_models.OfferValidationSubRuleField[sub_rule_data["sub_rule_type"]].value["model"],
                attribute=offers_models.OfferValidationSubRuleField[sub_rule_data["sub_rule_type"]].value["attribute"],
                operator=offers_models.OfferValidationRuleOperator[sub_rule_data["operator"]],
                comparated={"comparated": comparated},
            )
            db.session.add(sub_rule)
        db.session.commit()
        flash("Règle créée avec succès", "success")

    except sa.exc.IntegrityError as err:
        db.session.rollback()
        flash(f"Erreur dans la création de la règle : {err}", "warning")

    return redirect(url_for("backoffice_v3_web.offer_validation_rules.list_rules"), code=303)


@offer_validation_rules_blueprint.route("/<int:rule_id>/delete", methods=["GET"])
def get_delete_offer_validation_rule_form(rule_id: int) -> utils.BackofficeResponse:
    rule_to_delete = offers_models.OfferValidationRule.query.get(rule_id)

    return render_template(
        "components/turbo/modal_form.html",
        form=empty_forms.EmptyForm(),
        dst=url_for("backoffice_v3_web.offer_validation_rules.delete_rule", rule_id=rule_id),
        div_id=f"delete-offer-validation-rule-{rule_id}",  # must be consistent with parameter passed to build_lazy_modal
        title="Supprimer une règle de validation d'offre",
        button_text="Supprimer la règle",
        information=f"La règle {rule_to_delete.name} et ses sous-règles seront définitivement supprimées de la base de données. Veuillez confirmer ce choix.",
    )


@offer_validation_rules_blueprint.route("/<int:rule_id>/delete", methods=["POST"])
def delete_rule(rule_id: int) -> utils.BackofficeResponse:
    rule_to_delete = offers_models.OfferValidationRule.query.get_or_404(rule_id)
    subrules_to_delete = offers_models.OfferValidationSubRule.query.filter_by(validationRuleId=rule_id).all()

    if rule_to_delete:
        try:
            for sub_rule in subrules_to_delete:
                db.session.delete(sub_rule)
            db.session.delete(rule_to_delete)
            db.session.commit()
        except sa.exc.IntegrityError as exc:
            db.session.rollback()
            flash(f"Une erreur s'est produite : {exc}", "warning")
        else:
            flash(f"La règle {rule_to_delete.name} et ses sous-règles ont été supprimées", "success")

    return redirect(url_for("backoffice_v3_web.offer_validation_rules.list_rules"), code=303)


@offer_validation_rules_blueprint.route("/<int:rule_id>/edit", methods=["GET"])
def get_edit_offer_validation_rule_form(rule_id: int) -> utils.BackofficeResponse:
    rule_to_update = offers_models.OfferValidationRule.query.get_or_404(rule_id)
    sub_rule_data = {}
    for sub_rule in rule_to_update.subRules:
        sub_rule_type = offers_models.OfferValidationSubRuleField(
            {
                "model": sub_rule.model,
                "attribute": sub_rule.attribute,
            }
        )
        field_to_fill = forms.OFFER_VALIDATION_SUB_RULE_FORM_FIELD_CONFIGURATION[sub_rule_type.name]["field"]
        if field_to_fill == "list_field":
            sub_rule_comparated = ", ".join(sub_rule.comparated["comparated"])
        else:
            sub_rule_comparated = sub_rule.comparated["comparated"]

        sub_rule_data[sub_rule.id] = {
            "id": sub_rule.id,
            "sub_rule_type": sub_rule_type.name,
            "operator": sub_rule.operator.name,
            field_to_fill: sub_rule_comparated,
        }
    form = forms.CreateOfferValidationRuleForm(
        name=rule_to_update.name,
        sub_rules=list(sub_rule_data.values()),
    )
    for sub_rule in form.sub_rules:
        if sub_rule.sub_rule_type.data == "ID_OFFERER":
            autocomplete.prefill_offerers_choices(sub_rule.offerer)

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_v3_web.offer_validation_rules.edit_rule", rule_id=rule_id),
        div_id=f"edit-offer-validation-rule-{rule_id}",  # must be consistent with parameter passed to build_lazy_modal
        title="Modifier une règle de validation d'offre",
        button_text="Modifier la règle",
    )


@offer_validation_rules_blueprint.route("/<int:rule_id>/edit", methods=["POST"])
def edit_rule(rule_id: int) -> utils.BackofficeResponse:
    rule_to_update = offers_models.OfferValidationRule.query.get(rule_id)

    form = forms.CreateOfferValidationRuleForm()
    if not form.validate():
        error_msg = utils.build_form_error_msg(form)
        flash(error_msg, "warning")
        return redirect(url_for("backoffice_v3_web.offer_validation_rules.list_rules"), code=303)

    try:
        # delete unwanted rules
        old_sub_rules = {sub_rule.id: sub_rule for sub_rule in rule_to_update.subRules}
        for sub_rule_id in old_sub_rules:
            if sub_rule_id not in [sub_rule_data["id"] for sub_rule_data in form.sub_rules.data]:
                db.session.delete(old_sub_rules[sub_rule_id])
        new_subrule_ids = []

        for sub_rule_data in form.sub_rules.data:
            comparated = (
                sub_rule_data["decimal_field"]
                or sub_rule_data["list_field"]
                or sub_rule_data["offer_type"]
                or sub_rule_data["offerer"]
                or sub_rule_data["subcategories"]
                or sub_rule_data["categories"]
                or sub_rule_data["show_sub_type"]
            )

            # edit existing subrule
            if sub_rule_data["id"]:
                sub_rule_to_update = offers_models.OfferValidationSubRule.query.get(int(sub_rule_data["id"]))
                sub_rule_to_update.model = offers_models.OfferValidationSubRuleField[
                    sub_rule_data["sub_rule_type"]
                ].value["model"]
                sub_rule_to_update.attribute = offers_models.OfferValidationSubRuleField[
                    sub_rule_data["sub_rule_type"]
                ].value["attribute"]
                sub_rule_to_update.operator = offers_models.OfferValidationRuleOperator[sub_rule_data["operator"]]
                sub_rule_to_update.comparated = {"comparated": comparated}
                db.session.add(sub_rule_to_update)
                new_subrule_ids.append(int(sub_rule_data["id"]))

            # create new subrule
            else:
                sub_rule = offers_models.OfferValidationSubRule(
                    validationRule=rule_to_update,
                    model=offers_models.OfferValidationSubRuleField[sub_rule_data["sub_rule_type"]].value["model"],
                    attribute=offers_models.OfferValidationSubRuleField[sub_rule_data["sub_rule_type"]].value[
                        "attribute"
                    ],
                    operator=offers_models.OfferValidationRuleOperator[sub_rule_data["operator"]],
                    comparated={"comparated": comparated},
                )
                db.session.add(sub_rule)
                new_subrule_ids.append(sub_rule.id)

        rule_to_update.name = form.name.data
        rule_to_update.dateModified = datetime.datetime.utcnow()
        rule_to_update.latestAuthor = current_user
        db.session.add(rule_to_update)
        db.session.commit()

    except sa.exc.IntegrityError as exc:
        db.session.rollback()
        flash(f"Une erreur s'est produite : {exc}", "warning")
    else:
        flash(f"La règle {rule_to_update.name} et ses sous-règles ont été modifiées", "success")

    return redirect(url_for("backoffice_v3_web.offer_validation_rules.list_rules"), code=303)
