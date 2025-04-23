from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models


def create_industrial_offer_validation_rules() -> None:
    offer_name_rule = offers_factories.OfferValidationRuleFactory.create(name="Règle sur les noms d'offres")
    offers_factories.OfferValidationSubRuleFactory.create(
        validationRule=offer_name_rule,
        model=offers_models.OfferValidationModel.OFFER,
        attribute=offers_models.OfferValidationAttribute.NAME,
        operator=offers_models.OfferValidationRuleOperator.CONTAINS,
        comparated={"comparated": ["suspicious", "verboten", "interdit"]},
    )
    create_rule_history_data_from_rule(offer_name_rule)

    collective_offer_description_rule = offers_factories.OfferValidationRuleFactory.create(
        name="Règle sur les descriptions d'offres collectives"
    )
    offers_factories.OfferValidationSubRuleFactory.create(
        validationRule=collective_offer_description_rule,
        model=offers_models.OfferValidationModel.COLLECTIVE_OFFER,
        attribute=offers_models.OfferValidationAttribute.DESCRIPTION,
        operator=offers_models.OfferValidationRuleOperator.CONTAINS,
        comparated={"comparated": ["suspicious", "verboten", "interdit"]},
    )
    create_rule_history_data_from_rule(collective_offer_description_rule)

    collective_offer_template_exact_name_rule = offers_factories.OfferValidationRuleFactory.create(
        name="Règle exacte sur les noms d'offres collective templates"
    )
    offers_factories.OfferValidationSubRuleFactory.create(
        validationRule=collective_offer_template_exact_name_rule,
        model=offers_models.OfferValidationModel.COLLECTIVE_OFFER_TEMPLATE,
        attribute=offers_models.OfferValidationAttribute.NAME,
        operator=offers_models.OfferValidationRuleOperator.CONTAINS_EXACTLY,
        comparated={"comparated": ["bon", "lot", "go"]},
    )
    create_rule_history_data_from_rule(collective_offer_template_exact_name_rule)

    offerers_to_reject = offerers_factories.OffererFactory.create_batch(5)
    offerer_siren_rule = offers_factories.OfferValidationRuleFactory.create(name="Règle sur les structures")
    offers_factories.OfferValidationSubRuleFactory.create(
        validationRule=offerer_siren_rule,
        model=offers_models.OfferValidationModel.OFFERER,
        attribute=offers_models.OfferValidationAttribute.ID,
        operator=offers_models.OfferValidationRuleOperator.IN,
        comparated={"comparated": [offerer.id for offerer in offerers_to_reject]},
    )
    create_rule_history_data_from_rule(offerer_siren_rule)

    collective_offer_and_template_siren_rule = offers_factories.OfferValidationRuleFactory.create(
        name="Règle sur les structures et les offres collectives et vitrines"
    )
    offers_factories.OfferValidationSubRuleFactory.create(
        validationRule=collective_offer_and_template_siren_rule,
        model=offers_models.OfferValidationModel.OFFERER,
        attribute=offers_models.OfferValidationAttribute.ID,
        operator=offers_models.OfferValidationRuleOperator.IN,
        comparated={"comparated": [offerers_to_reject[0].id, offerers_to_reject[1].id]},
    )
    offers_factories.OfferValidationSubRuleFactory.create(
        validationRule=collective_offer_and_template_siren_rule,
        model=None,
        attribute=offers_models.OfferValidationAttribute.CLASS_NAME,
        operator=offers_models.OfferValidationRuleOperator.IN,
        comparated={"comparated": ["CollectiveOffer", "CollectiveOfferTemplate"]},
    )
    create_rule_history_data_from_rule(collective_offer_and_template_siren_rule)

    cabaret_show_sub_type_offer_rule = offers_factories.OfferValidationRuleFactory.create(
        name="Vérification des sous-types Cabaret des offres"
    )
    offers_factories.OfferValidationSubRuleFactory.create(
        validationRule=cabaret_show_sub_type_offer_rule,
        model=offers_models.OfferValidationModel.OFFER,
        attribute=offers_models.OfferValidationAttribute.SHOW_SUB_TYPE,
        operator=offers_models.OfferValidationRuleOperator.IN,
        comparated={"comparated": ["1101"]},
    )
    create_rule_history_data_from_rule(cabaret_show_sub_type_offer_rule)

    offer_max_price_rule = offers_factories.OfferValidationRuleFactory.create(
        name="Vérification de prix maximum de l'offre"
    )
    offers_factories.OfferValidationSubRuleFactory.create(
        validationRule=offer_max_price_rule,
        model=offers_models.OfferValidationModel.OFFER,
        attribute=offers_models.OfferValidationAttribute.MAX_PRICE,
        operator=offers_models.OfferValidationRuleOperator.GREATER_THAN,
        comparated={"comparated": 150},
    )
    create_rule_history_data_from_rule(offer_max_price_rule)


def create_rule_history_data_from_rule(rule: offers_models.OfferValidationRule) -> None:
    history_factories.ActionHistoryFactory.create(
        ruleId=rule.id,
        authorUser=None,
        actionType=history_models.ActionType.RULE_CREATED,
        comment=None,
        extraData={
            "sub_rules_info": {
                "sub_rules_created": [
                    {
                        "id": sub_rule.id,
                        "model": sub_rule.model.name if sub_rule.model else None,
                        "attribute": sub_rule.attribute.name,
                        "operator": sub_rule.operator.name,
                        "comparated": sub_rule.comparated["comparated"],
                    }
                    for sub_rule in rule.subRules
                ]
            }
        },
    )
