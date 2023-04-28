from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models


def create_industrial_offer_validation_rules() -> None:
    offer_name_rule = offers_factories.OfferValidationRuleFactory(name="Règle sur les noms d'offres")
    offers_factories.OfferValidationSubRuleFactory(
        validationRule=offer_name_rule,
        model=offers_models.OfferValidationModel.OFFER,
        attribute=offers_models.OfferValidationAttribute.NAME,
        operator=offers_models.OfferValidationRuleOperator.CONTAINS,
        comparated={"comparated": ["suspicious", "verboten", "interdit"]},
    )

    collective_offer_description_rule = offers_factories.OfferValidationRuleFactory(
        name="Règle sur les descriptions d'offres collectives"
    )
    offers_factories.OfferValidationSubRuleFactory(
        validationRule=collective_offer_description_rule,
        model=offers_models.OfferValidationModel.COLLECTIVE_OFFER,
        attribute=offers_models.OfferValidationAttribute.DESCRIPTION,
        operator=offers_models.OfferValidationRuleOperator.CONTAINS,
        comparated={"comparated": ["suspicious", "verboten", "interdit"]},
    )

    collective_offer_template_exact_name_rule = offers_factories.OfferValidationRuleFactory(
        name="Règle exacte sur les noms d'offres collective templates"
    )
    offers_factories.OfferValidationSubRuleFactory(
        validationRule=collective_offer_template_exact_name_rule,
        model=offers_models.OfferValidationModel.COLLECTIVE_OFFER_TEMPLATE,
        attribute=offers_models.OfferValidationAttribute.NAME,
        operator=offers_models.OfferValidationRuleOperator.CONTAINS_EXACTLY,
        comparated={"comparated": ["bon", "lot", "go"]},
    )

    offerer_siren_rule = offers_factories.OfferValidationRuleFactory(name="Règle sur les SIREN")
    offers_factories.OfferValidationSubRuleFactory(
        validationRule=offerer_siren_rule,
        model=offers_models.OfferValidationModel.OFFERER,
        attribute=offers_models.OfferValidationAttribute.SIREN,
        operator=offers_models.OfferValidationRuleOperator.IN,
        comparated={"comparated": ["777777770", "777777772", "777777774"]},
    )

    collective_offer_and_template_siren_rule = offers_factories.OfferValidationRuleFactory(
        name="Règle sur les SIRET et les offres collectives et vitrines"
    )
    offers_factories.OfferValidationSubRuleFactory(
        validationRule=collective_offer_and_template_siren_rule,
        model=offers_models.OfferValidationModel.OFFERER,
        attribute=offers_models.OfferValidationAttribute.SIREN,
        operator=offers_models.OfferValidationRuleOperator.IN,
        comparated={"comparated": ["777777776", "777777778"]},
    )
    offers_factories.OfferValidationSubRuleFactory(
        validationRule=collective_offer_and_template_siren_rule,
        model=None,
        attribute=offers_models.OfferValidationAttribute.CLASS_NAME,
        operator=offers_models.OfferValidationRuleOperator.IN,
        comparated={"comparated": ["CollectiveOffer", "CollectiveOfferTemplate"]},
    )

    cabaret_show_sub_type_offer_rule = offers_factories.OfferValidationRuleFactory(
        name="Vérification des sous-types Cabaret des offres"
    )
    offers_factories.OfferValidationSubRuleFactory(
        validationRule=cabaret_show_sub_type_offer_rule,
        model=offers_models.OfferValidationModel.OFFER,
        attribute=offers_models.OfferValidationAttribute.SHOW_SUB_TYPE,
        operator=offers_models.OfferValidationRuleOperator.EQUALS,
        comparated={"comparated": "1011"},
    )

    offer_max_price_rule = offers_factories.OfferValidationRuleFactory(name="Vérification de prix maximum de l'offre")
    offers_factories.OfferValidationSubRuleFactory(
        validationRule=offer_max_price_rule,
        model=offers_models.OfferValidationModel.OFFER,
        attribute=offers_models.OfferValidationAttribute.MAX_PRICE,
        operator=offers_models.OfferValidationRuleOperator.GREATER_THAN,
        comparated={"comparated": 150},
    )
