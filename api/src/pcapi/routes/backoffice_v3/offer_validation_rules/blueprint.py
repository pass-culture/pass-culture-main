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
    offerer_dict = {str(offerer.id): f"{offerer.name} ({offerer.siren})" for offerer in offerers_from_rules}
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
