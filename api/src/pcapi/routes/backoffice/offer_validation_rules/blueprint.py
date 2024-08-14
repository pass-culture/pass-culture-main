import typing

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.repository import atomic
from pcapi.repository import mark_transaction_as_invalid
from pcapi.routes.backoffice import autocomplete
from pcapi.routes.backoffice.forms import empty as empty_forms
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

    if not all_offerer_ids:
        return {}

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


def _get_venues_data_for_rules(rules: list[offers_models.OfferValidationRule]) -> dict:
    all_venue_ids: set = set()
    for rule in rules:
        for sub_rule in rule.subRules:
            if (
                sub_rule.model == offers_models.OfferValidationModel.VENUE
                and sub_rule.attribute == offers_models.OfferValidationAttribute.ID
            ):
                all_venue_ids |= set(sub_rule.comparated["comparated"])

    if not all_venue_ids:
        return {}

    venues_from_rules = (
        offerers_models.Venue.query.options(
            sa.orm.load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.siret,
            )
        )
        .filter(offerers_models.Venue.id.in_(all_venue_ids))
        .all()
    )
    venue_dict = {venue.id: f"{venue.common_name} ({venue.siret or 'Pas de SIRET'})" for venue in venues_from_rules}
    return venue_dict


@offer_validation_rules_blueprint.route("", methods=["GET"])
@atomic()
def list_rules() -> utils.BackofficeResponse:
    form = forms.SearchRuleForm(formdata=utils.get_query_params())

    query = (
        offers_models.OfferValidationRule.query.outerjoin(offers_models.OfferValidationSubRule)
        .options(sa.orm.contains_eager(offers_models.OfferValidationRule.subRules))
        .filter(offers_models.OfferValidationRule.isActive.is_(True))
        .order_by(offers_models.OfferValidationRule.name)
    )

    if not form.validate():
        mark_transaction_as_invalid()
        return (
            render_template("offer_validation_rules/list_rules.html", rows=[], form=form, dst=url_for(".list_rules")),
            400,
        )

    if not form.is_empty():
        if form.q.data:
            search_query = clean_accents(form.q.data)
            split_search = f'"{clean_accents(form.q.data.lower())}"'
            query = query.filter(
                sa.or_(
                    sa.func.unaccent(offers_models.OfferValidationRule.name).ilike(f"%{search_query}%"),
                    offers_models.OfferValidationRule.subRules.any(
                        sa.func.lower(
                            sa.func.unaccent(
                                sa.cast(offers_models.OfferValidationSubRule.comparated["comparated"], sa.Text)
                            )
                        ).ilike(f"%{split_search}%")
                    ),
                )
            )

        if form.offerer.data:
            offerer_ids = [int(id_str) for id_str in form.offerer.data]
            query = query.filter(
                sa.and_(
                    offers_models.OfferValidationRule.subRules.any(
                        offers_models.OfferValidationSubRule.model == offers_models.OfferValidationModel.OFFERER
                    ),
                    offers_models.OfferValidationRule.subRules.any(
                        # operator @> checks if `comparated` includes all filtered offerer ids
                        offers_models.OfferValidationSubRule.comparated["comparated"].op("@>")(offerer_ids)
                    ),
                )
            )

        if form.venue.data:
            venue_ids = [int(id_str) for id_str in form.venue.data]
            query = query.filter(
                sa.and_(
                    offers_models.OfferValidationRule.subRules.any(
                        offers_models.OfferValidationSubRule.model == offers_models.OfferValidationModel.VENUE
                    ),
                    offers_models.OfferValidationRule.subRules.any(
                        # operator @> checks if `comparated` includes all filtered venue ids
                        offers_models.OfferValidationSubRule.comparated["comparated"].op("@>")(venue_ids)
                    ),
                )
            )

        if form.category.data:
            query = query.filter(
                sa.and_(
                    offers_models.OfferValidationRule.subRules.any(
                        offers_models.OfferValidationSubRule.attribute
                        == offers_models.OfferValidationAttribute.CATEGORY_ID
                    ),
                    offers_models.OfferValidationRule.subRules.any(
                        # operator @> checks if `comparated` includes all filtered categories
                        offers_models.OfferValidationSubRule.comparated["comparated"].op("@>")(form.category.data)
                    ),
                )
            )

        if form.subcategory.data:
            query = query.filter(
                sa.and_(
                    offers_models.OfferValidationRule.subRules.any(
                        offers_models.OfferValidationSubRule.attribute
                        == offers_models.OfferValidationAttribute.SUBCATEGORY_ID
                    ),
                    offers_models.OfferValidationRule.subRules.any(
                        # operator @> checks if `comparated` includes all filtered subcategories
                        offers_models.OfferValidationSubRule.comparated["comparated"].op("@>")(form.subcategory.data)
                    ),
                )
            )

    rules = query.all()

    offerer_dict = _get_offerers_data_for_rules(rules)
    venue_dict = _get_venues_data_for_rules(rules)

    return render_template(
        "offer_validation_rules/list_rules.html",
        rows=rules,
        offerer_dict=offerer_dict,
        venue_dict=venue_dict,
        form=form,
        dst=url_for(".list_rules"),
        active_tab=request.args.get("active_tab", "rules"),
    )


class SubRuleHistorySerializer:
    model: offers_models.OfferValidationModel | None
    attribute: offers_models.OfferValidationAttribute
    operator: offers_models.OfferValidationRuleOperator

    def __init__(self, rule_history_extra_data: dict) -> None:
        self.model = (
            offers_models.OfferValidationModel[rule_history_extra_data["model"]]
            if rule_history_extra_data["model"]
            else None
        )
        self.attribute = offers_models.OfferValidationAttribute[rule_history_extra_data["attribute"]]
        self.operator = offers_models.OfferValidationRuleOperator[rule_history_extra_data["operator"]]


@offer_validation_rules_blueprint.route("/history", methods=["GET"])
@atomic()
def get_rules_history() -> utils.BackofficeResponse:
    actions_history = (
        history_models.ActionHistory.query.filter(history_models.ActionHistory.ruleId.is_not(None))
        .order_by(history_models.ActionHistory.actionDate.desc())
        .options(
            sa.orm.joinedload(history_models.ActionHistory.authorUser).load_only(
                users_models.User.id, users_models.User.firstName, users_models.User.lastName
            ),
            sa.orm.joinedload(history_models.ActionHistory.rule).load_only(offers_models.OfferValidationRule.name),
        )
        .all()
    )

    def sub_rule_info_serializer(info: dict) -> SubRuleHistorySerializer:
        return SubRuleHistorySerializer(info)

    return render_template(
        "offer_validation_rules/history.html",
        actions=actions_history,
        sub_rule_info_serializer=sub_rule_info_serializer,
        offerer_dict=_get_offerers_data_for_rule_history(actions_history),
        venue_dict=_get_venues_data_for_rule_history(actions_history),
    )


def _get_ids_for_rule_history(
    rules_history: list[history_models.ActionHistory], rule_model: offers_models.OfferValidationModel
) -> set:
    all_model_ids: set = set()
    for history in rules_history:
        assert history.extraData is not None  # if it's None, then the history is faulty
        for sub_rules_keys in history.extraData["sub_rules_info"]:
            for sub_rule_data in history.extraData["sub_rules_info"][sub_rules_keys]:
                if (
                    sub_rule_data["model"] == rule_model.name
                    and sub_rule_data["attribute"] == offers_models.OfferValidationAttribute.ID.name
                ):
                    all_model_ids |= (
                        set(sub_rule_data["comparated"]["added"]) | set(sub_rule_data["comparated"]["removed"])
                        if sub_rules_keys == "sub_rules_modified"
                        else set(sub_rule_data["comparated"])
                    )
    return all_model_ids


def _get_offerers_data_for_rule_history(rules_history: list[history_models.ActionHistory]) -> dict:
    all_offerer_ids = _get_ids_for_rule_history(rules_history, offers_models.OfferValidationModel.OFFERER)

    if not all_offerer_ids:
        return {}

    offerers_from_history = (
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
    offerer_dict = {offerer.id: f"{offerer.name} ({offerer.siren})" for offerer in offerers_from_history}
    return offerer_dict


def _get_venues_data_for_rule_history(rules_history: list[history_models.ActionHistory]) -> dict:
    all_venue_ids = _get_ids_for_rule_history(rules_history, offers_models.OfferValidationModel.VENUE)

    if not all_venue_ids:
        return {}

    venues_from_history = (
        offerers_models.Venue.query.options(
            sa.orm.load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.siret,
            )
        )
        .filter(offerers_models.Venue.id.in_(all_venue_ids))
        .all()
    )
    venue_dict = {venue.id: f"{venue.common_name} ({venue.siret or 'Pas de SIRET'})" for venue in venues_from_history}
    return venue_dict


@offer_validation_rules_blueprint.route("/create", methods=["GET"])
@atomic()
def get_create_offer_validation_rule_form() -> utils.BackofficeResponse:
    form = forms.CreateOfferValidationRuleForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.offer_validation_rules.create_rule"),
        div_id="create-offer-validation-rule",  # must be consistent with parameter passed to build_lazy_modal
        title="Créer une règle de validation d'offre",
        button_text="Créer la règle",
    )


@offer_validation_rules_blueprint.route("/create", methods=["POST"])
@atomic()
def create_rule() -> utils.BackofficeResponse:
    form = forms.CreateOfferValidationRuleForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        mark_transaction_as_invalid()
        return redirect(url_for("backoffice_web.offer_validation_rules.list_rules"), code=303)

    try:
        new_rule = offers_models.OfferValidationRule(name=form.name.data)
        db.session.add(new_rule)
        sub_rules_info: dict[str, list] = {"sub_rules_created": []}
        for sub_rule_data in form.sub_rules.data:
            comparated = (
                sub_rule_data["decimal_field"]
                or sub_rule_data["list_field"]
                or sub_rule_data["offer_type"]
                or sub_rule_data["venue"]
                or sub_rule_data["offerer"]
                or sub_rule_data["subcategories"]
                or sub_rule_data["categories"]
                or sub_rule_data["show_sub_type"]
                or sub_rule_data["formats"]
            )
            sub_rule = offers_models.OfferValidationSubRule(
                validationRule=new_rule,
                model=offers_models.OfferValidationSubRuleField[sub_rule_data["sub_rule_type"]].value["model"],
                attribute=offers_models.OfferValidationSubRuleField[sub_rule_data["sub_rule_type"]].value["attribute"],
                operator=offers_models.OfferValidationRuleOperator[sub_rule_data["operator"]],
                comparated={"comparated": comparated},
            )
            db.session.add(sub_rule)
            db.session.flush()
            _add_sub_rule_data_to_history(sub_rule, sub_rules_info["sub_rules_created"])
        history_api.add_action(
            history_models.ActionType.RULE_CREATED,
            current_user,
            rule=new_rule,
            sub_rules_info=sub_rules_info,
        )
        db.session.flush()
        flash("La nouvelle règle a été créée", "success")

    except sa.exc.IntegrityError as err:
        mark_transaction_as_invalid()
        flash(Markup("Erreur dans la création de la règle : {message}").format(message=str(err)), "warning")

    return redirect(url_for("backoffice_web.offer_validation_rules.list_rules"), code=303)


@offer_validation_rules_blueprint.route("/<int:rule_id>/delete", methods=["GET"])
@atomic()
def get_delete_offer_validation_rule_form(rule_id: int) -> utils.BackofficeResponse:
    rule_to_delete = offers_models.OfferValidationRule.query.filter_by(id=rule_id).one_or_none()
    if not rule_to_delete:
        mark_transaction_as_invalid()
        raise NotFound()

    return render_template(
        "components/turbo/modal_form.html",
        form=empty_forms.EmptyForm(),
        dst=url_for("backoffice_web.offer_validation_rules.delete_rule", rule_id=rule_id),
        div_id=f"delete-offer-validation-rule-{rule_id}",  # must be consistent with parameter passed to build_lazy_modal
        title="Supprimer une règle de validation d'offre",
        button_text="Supprimer la règle",
        information=Markup(
            "La règle {name} et ses sous-règles seront définitivement supprimées de la base de données. "
            "Veuillez confirmer ce choix."
        ).format(name=rule_to_delete.name),
    )


@offer_validation_rules_blueprint.route("/<int:rule_id>/delete", methods=["POST"])
@atomic()
def delete_rule(rule_id: int) -> utils.BackofficeResponse:
    rule_to_delete = offers_models.OfferValidationRule.query.filter_by(id=rule_id).one_or_none()
    if not rule_to_delete:
        mark_transaction_as_invalid()
        raise NotFound()

    subrules_to_delete = offers_models.OfferValidationSubRule.query.filter_by(validationRuleId=rule_id).all()

    if rule_to_delete:
        try:
            sub_rules_info: dict[str, list] = {"sub_rules_deleted": []}
            for sub_rule in subrules_to_delete:
                _add_sub_rule_data_to_history(sub_rule, sub_rules_info["sub_rules_deleted"])
                db.session.delete(sub_rule)
            rule_to_delete.isActive = False
            history_api.add_action(
                history_models.ActionType.RULE_DELETED,
                current_user,
                rule=rule_to_delete,
                sub_rules_info=sub_rules_info,
            )
            db.session.flush()
        except sa.exc.IntegrityError as exc:
            mark_transaction_as_invalid()
            flash(Markup("Une erreur s'est produite : {message}").format(message=str(exc)), "warning")
        else:
            flash(
                Markup("La règle {name} et ses sous-règles ont été supprimées").format(name=rule_to_delete.name),
                "success",
            )

    return redirect(url_for("backoffice_web.offer_validation_rules.list_rules"), code=303)


@offer_validation_rules_blueprint.route("/<int:rule_id>/edit", methods=["GET"])
@atomic()
def get_edit_offer_validation_rule_form(rule_id: int) -> utils.BackofficeResponse:
    rule_to_update = offers_models.OfferValidationRule.query.filter_by(id=rule_id).one_or_none()
    if not rule_to_update:
        mark_transaction_as_invalid()
        raise NotFound()

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
        if sub_rule.sub_rule_type.data == "ID_VENUE":
            autocomplete.prefill_venues_choices(sub_rule.venue)
        if sub_rule.sub_rule_type.data == "ID_OFFERER":
            autocomplete.prefill_offerers_choices(sub_rule.offerer)

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.offer_validation_rules.edit_rule", rule_id=rule_id),
        div_id=f"edit-offer-validation-rule-{rule_id}",  # must be consistent with parameter passed to build_lazy_modal
        title="Modifier une règle de validation d'offre",
        button_text="Modifier la règle",
    )


@offer_validation_rules_blueprint.route("/<int:rule_id>/edit", methods=["POST"])
@atomic()
def edit_rule(rule_id: int) -> utils.BackofficeResponse:
    rule_to_update = offers_models.OfferValidationRule.query.filter_by(id=rule_id).one_or_none()
    if not rule_to_update:
        mark_transaction_as_invalid()
        raise NotFound()

    form = forms.CreateOfferValidationRuleForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for("backoffice_web.offer_validation_rules.list_rules"), code=303)

    sub_rules_info: dict[str, list] = {"sub_rules_deleted": [], "sub_rules_created": [], "sub_rules_modified": []}
    try:
        # delete unwanted rules
        old_sub_rules = {sub_rule.id: sub_rule for sub_rule in rule_to_update.subRules}
        for sub_rule_id in old_sub_rules:
            if sub_rule_id not in [sub_rule_data["id"] for sub_rule_data in form.sub_rules.data]:
                _add_sub_rule_data_to_history(old_sub_rules[sub_rule_id], sub_rules_info["sub_rules_deleted"])
                rule_to_update.subRules.remove(old_sub_rules[sub_rule_id])
                db.session.delete(old_sub_rules[sub_rule_id])

        for sub_rule_data in form.sub_rules.data:
            comparated = (
                sub_rule_data["decimal_field"]
                or sub_rule_data["list_field"]
                or sub_rule_data["offer_type"]
                or sub_rule_data["venue"]
                or sub_rule_data["offerer"]
                or sub_rule_data["subcategories"]
                or sub_rule_data["categories"]
                or sub_rule_data["show_sub_type"]
                or sub_rule_data["formats"]
            )

            # edit existing subrule
            if sub_rule_data["id"]:
                sub_rule_to_update = offers_models.OfferValidationSubRule.query.filter_by(
                    id=int(sub_rule_data["id"])
                ).one()
                is_different_sub_rule = any(
                    [
                        sub_rule_to_update.model
                        != offers_models.OfferValidationSubRuleField[sub_rule_data["sub_rule_type"]].value["model"],
                        sub_rule_to_update.attribute
                        != offers_models.OfferValidationSubRuleField[sub_rule_data["sub_rule_type"]].value["attribute"],
                        sub_rule_to_update.operator
                        != offers_models.OfferValidationRuleOperator[sub_rule_data["operator"]],
                    ]
                )

                # the sub_rule is heavily modified, so it's like deleting it and recreating a new one
                if is_different_sub_rule:
                    _add_sub_rule_data_to_history(sub_rule_to_update, sub_rules_info["sub_rules_deleted"])
                    sub_rule_to_update.model = offers_models.OfferValidationSubRuleField[
                        sub_rule_data["sub_rule_type"]
                    ].value["model"]
                    sub_rule_to_update.attribute = offers_models.OfferValidationSubRuleField[
                        sub_rule_data["sub_rule_type"]
                    ].value["attribute"]
                    sub_rule_to_update.operator = offers_models.OfferValidationRuleOperator[sub_rule_data["operator"]]
                    sub_rule_to_update.comparated = {"comparated": comparated}
                    _add_sub_rule_data_to_history(sub_rule_to_update, sub_rules_info["sub_rules_created"])
                # only the comparated is modified, so we keep the diff
                elif sub_rule_to_update.comparated != {"comparated": comparated}:
                    old_comparated = sub_rule_to_update.comparated["comparated"]
                    sub_rule_to_update.comparated = {"comparated": comparated}
                    _add_sub_rule_data_to_history(
                        sub_rule_to_update, sub_rules_info["sub_rules_modified"], old_comparated
                    )
                db.session.add(sub_rule_to_update)

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
                db.session.flush()
                _add_sub_rule_data_to_history(sub_rule, sub_rules_info["sub_rules_created"])

        rule_to_update.name = form.name.data
        db.session.add(rule_to_update)
        if any(
            [
                sub_rules_info["sub_rules_deleted"],
                sub_rules_info["sub_rules_modified"],
                sub_rules_info["sub_rules_created"],
            ]
        ):
            history_api.add_action(
                history_models.ActionType.RULE_MODIFIED,
                current_user,
                rule=rule_to_update,
                sub_rules_info=sub_rules_info,
            )
        db.session.flush()

    except sa.exc.IntegrityError as exc:
        mark_transaction_as_invalid()
        flash(Markup("Une erreur s'est produite : {message}").format(message=str(exc)), "warning")
    else:
        flash(
            Markup("La règle <b>{name}</b> et ses sous-règles ont été modifiées").format(name=rule_to_update.name),
            "success",
        )

    return redirect(url_for("backoffice_web.offer_validation_rules.list_rules"), code=303)


def _add_sub_rule_data_to_history(
    sub_rule: offers_models.OfferValidationSubRule, history_info: list[dict], old_comparated: typing.Any | None = None
) -> None:
    if old_comparated:
        if isinstance(sub_rule.comparated["comparated"], list):
            comparated_info = {
                "added": sorted(set(sub_rule.comparated["comparated"]) - set(old_comparated)),
                "removed": sorted(set(old_comparated) - set(sub_rule.comparated["comparated"])),
            }
        else:
            comparated_info = {
                "added": sub_rule.comparated["comparated"],
                "removed": old_comparated,
            }
    else:
        comparated_info = sub_rule.comparated["comparated"]
    history_info.append(
        {
            "id": sub_rule.id,
            "model": sub_rule.model.name if sub_rule.model else None,
            "attribute": sub_rule.attribute.name,
            "operator": sub_rule.operator.name,
            "comparated": comparated_info,
        }
    )
