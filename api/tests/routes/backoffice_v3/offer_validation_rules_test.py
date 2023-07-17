import datetime

from flask import url_for
import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.routes.backoffice_v3.offer_validation_rules import utils

from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


def get_empty_sub_rule_data(i: int | None = 0) -> dict:
    return {
        f"sub_rules-{i}-sub_rule_type": None,
        f"sub_rules-{i}-operator": None,
        f"sub_rules-{i}-decimal_field": None,
        f"sub_rules-{i}-list_field": "",
        f"sub_rules-{i}-offer_type": [],
        f"sub_rules-{i}-offerer": [],
        f"sub_rules-{i}-subcategories": [],
        f"sub_rules-{i}-categories": [],
        f"sub_rules-{i}-show_sub_type": [],
    }


class ListRulesTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.offer_validation_rules.list_rules"
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_list_rules(self, authenticated_client):
        rule = offers_factories.OfferValidationRuleFactory(
            name="Règles de fraude", dateModified=datetime.datetime.utcnow()
        )
        offers_factories.OfferValidationSubRuleFactory(
            validationRule=rule,
            model=offers_models.OfferValidationModel.OFFER,
            attribute=offers_models.OfferValidationAttribute.NAME,
            operator=offers_models.OfferValidationRuleOperator.CONTAINS,
            comparated={"comparated": ["interdit", "suspicious", "verboten"]},
        )

        response = authenticated_client.get(url_for(self.endpoint))

        assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)

        assert rows[0]["ID"] == str(rule.id)
        assert rows[0]["Nom"] == rule.name
        assert rows[0]["Dernier auteur"] == rule.latestAuthor.full_name
        assert datetime.datetime.utcnow().strftime("%d/%m/%Y") in rows[0]["Date de dernière modification"]

        extra_data = html_parser.extract(response.data, tag="tr", class_="collapse accordion-collapse")[0]
        assert "Le nom de l'offre individuelle" in extra_data
        assert "suspicious" in extra_data

    @pytest.mark.parametrize(
        "q,expected_nb_results,expected_results_key",
        [
            ("", 2, ["rule1", "rule2"]),
            ("magique", 1, ["rule1"]),
            ("moldue", 1, ["rule2"]),
            ("REGLE", 2, ["rule1", "rule2"]),
            ("pouet", 0, []),
        ],
    )
    def search_list_rules(self, authenticated_client, q, expected_nb_results, expected_results_key):
        rules = {
            "rule1": offers_factories.OfferValidationRuleFactory(name="Règle sur les offres magiques"),
            "rule2": offers_factories.OfferValidationRuleFactory(name="Règle sur les offres moldues"),
        }

        response = authenticated_client.get(url_for(self.endpoint, q=q))

        assert response.status_code == 200

        nb_results = html_parser.count_table_rows(response.data)
        assert nb_results == expected_nb_results

        rows = html_parser.extract_table_rows(response.data)
        count = 0
        for index, key in enumerate(expected_results_key):
            for row in rows:
                if count < expected_nb_results and row[index]["Nom"] == rules.get(key).name:
                    count += 1
                    break


class GetCreateOfferValidationRuleFormTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.offer_validation_rules.create_rule"
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_get_create_form_test(self, legit_user, authenticated_client):
        form_url = url_for(self.endpoint)

        with assert_num_queries(2):  # session + user
            response = authenticated_client.get(form_url)
            assert response.status_code == 200


class CreateOfferValidationRuleTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.offer_validation_rules.create_rule"
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    @pytest.mark.parametrize(
        "form_data, expected_result",
        [
            (
                {
                    "sub_rules-0-sub_rule_type": "DESCRIPTION_OFFER",
                    "sub_rules-0-operator": "CONTAINS_EXACTLY",
                    "sub_rules-0-list_field": "Interdit, âne, Célèbre",
                },
                {
                    "model": offers_models.OfferValidationModel.OFFER,
                    "attribute": offers_models.OfferValidationAttribute.DESCRIPTION,
                    "operator": offers_models.OfferValidationRuleOperator.CONTAINS_EXACTLY,
                    "comparated": {"comparated": ["celebre", "interdit", "ane"]},
                },
            ),
            (
                {
                    "sub_rules-0-sub_rule_type": "TEXT_OFFER",
                    "sub_rules-0-operator": "CONTAINS_EXACTLY",
                    "sub_rules-0-list_field": "interdit, suspicious, verboten",
                },
                {
                    "model": offers_models.OfferValidationModel.OFFER,
                    "attribute": offers_models.OfferValidationAttribute.TEXT,
                    "operator": offers_models.OfferValidationRuleOperator.CONTAINS_EXACTLY,
                    "comparated": {"comparated": ["interdit", "suspicious", "verboten"]},
                },
            ),
            (
                {
                    "sub_rules-0-sub_rule_type": "TEXT_COLLECTIVE_OFFER",
                    "sub_rules-0-operator": "CONTAINS_EXACTLY",
                    "sub_rules-0-list_field": "interdit, suspicious, verboten",
                },
                {
                    "model": offers_models.OfferValidationModel.COLLECTIVE_OFFER,
                    "attribute": offers_models.OfferValidationAttribute.TEXT,
                    "operator": offers_models.OfferValidationRuleOperator.CONTAINS_EXACTLY,
                    "comparated": {"comparated": ["interdit", "suspicious", "verboten"]},
                },
            ),
            (
                {
                    "sub_rules-0-sub_rule_type": "TEXT_COLLECTIVE_OFFER_TEMPLATE",
                    "sub_rules-0-operator": "CONTAINS_EXACTLY",
                    "sub_rules-0-list_field": "interdit, suspicious, verboten",
                },
                {
                    "model": offers_models.OfferValidationModel.COLLECTIVE_OFFER_TEMPLATE,
                    "attribute": offers_models.OfferValidationAttribute.TEXT,
                    "operator": offers_models.OfferValidationRuleOperator.CONTAINS_EXACTLY,
                    "comparated": {"comparated": ["interdit", "suspicious", "verboten"]},
                },
            ),
            (
                {
                    "sub_rules-0-sub_rule_type": "MAX_PRICE_OFFER",
                    "sub_rules-0-operator": "NOT_EQUALS",
                    "sub_rules-0-decimal_field": "300",
                },
                {
                    "model": offers_models.OfferValidationModel.OFFER,
                    "attribute": offers_models.OfferValidationAttribute.MAX_PRICE,
                    "operator": offers_models.OfferValidationRuleOperator.NOT_EQUALS,
                    "comparated": {"comparated": 300},
                },
            ),
            (
                {
                    "sub_rules-0-sub_rule_type": "OFFER_TYPE",
                    "sub_rules-0-operator": "NOT_IN",
                    "sub_rules-0-offer_type": ["CollectiveOfferTemplate"],
                },
                {
                    "model": None,
                    "attribute": offers_models.OfferValidationAttribute.CLASS_NAME,
                    "operator": offers_models.OfferValidationRuleOperator.NOT_IN,
                    "comparated": {"comparated": ["CollectiveOfferTemplate"]},
                },
            ),
            (
                {
                    "sub_rules-0-sub_rule_type": "CATEGORY_OFFER",
                    "sub_rules-0-operator": "IN",
                    "sub_rules-0-categories": ["FILM", "CINEMA"],
                },
                {
                    "model": offers_models.OfferValidationModel.OFFER,
                    "attribute": offers_models.OfferValidationAttribute.CATEGORY_ID,
                    "operator": offers_models.OfferValidationRuleOperator.IN,
                    "comparated": {"comparated": ["FILM", "CINEMA"]},
                },
            ),
            (
                {
                    "sub_rules-0-sub_rule_type": "SUBCATEGORY_OFFER",
                    "sub_rules-0-operator": "IN",
                    "sub_rules-0-subcategories": ["ABO_LIVRE_NUMERIQUE", "ABO_JEU_VIDEO"],
                },
                {
                    "model": offers_models.OfferValidationModel.OFFER,
                    "attribute": offers_models.OfferValidationAttribute.SUBCATEGORY_ID,
                    "operator": offers_models.OfferValidationRuleOperator.IN,
                    "comparated": {"comparated": ["ABO_LIVRE_NUMERIQUE", "ABO_JEU_VIDEO"]},
                },
            ),
            (
                {
                    "sub_rules-0-sub_rule_type": "SHOW_SUB_TYPE_OFFER",
                    "sub_rules-0-operator": "IN",
                    "sub_rules-0-show_sub_type": ["1101"],
                },
                {
                    "model": offers_models.OfferValidationModel.OFFER,
                    "attribute": offers_models.OfferValidationAttribute.SHOW_SUB_TYPE,
                    "operator": offers_models.OfferValidationRuleOperator.IN,
                    "comparated": {"comparated": ["1101"]},
                },
            ),
        ],
    )
    def test_create_offer_validation_rule_with_one_rule(
        self, legit_user, authenticated_client, form_data, expected_result
    ):
        sub_rule_data = get_empty_sub_rule_data() | form_data
        form = {"name": "First rule of robotics"} | sub_rule_data

        response = self.post_to_endpoint(
            authenticated_client,
            form=form,
        )
        assert response.status_code == 303
        assert html_parser.extract_alert(authenticated_client.get(response.location).data) == "Règle créée avec succès"

        rule = offers_models.OfferValidationRule.query.one()
        assert rule.name == "First rule of robotics"
        assert rule.latestAuthor == legit_user
        assert rule.dateModified.date() == datetime.date.today()
        assert rule.subRules[0].model == expected_result["model"]
        assert rule.subRules[0].attribute == expected_result["attribute"]
        assert rule.subRules[0].operator == expected_result["operator"]
        assert rule.subRules[0].comparated == expected_result["comparated"]

    def test_create_offer_validation_rule_with_offerer_id(self, legit_user, authenticated_client):
        offerers = offerers_factories.OffererFactory.create_batch(2)
        sub_rule_data = get_empty_sub_rule_data() | {
            "sub_rules-0-sub_rule_type": "ID_OFFERER",
            "sub_rules-0-operator": "IN",
            "sub_rules-0-offerer": [offerers[0].id, offerers[1].id],
        }
        form = {"name": "First rule of robotics"} | sub_rule_data

        response = self.post_to_endpoint(
            authenticated_client,
            form=form,
        )
        assert response.status_code == 303
        assert html_parser.extract_alert(authenticated_client.get(response.location).data) == "Règle créée avec succès"

        rule = offers_models.OfferValidationRule.query.one()
        assert rule.name == "First rule of robotics"
        assert rule.latestAuthor == legit_user
        assert rule.dateModified.date() == datetime.date.today()
        assert rule.subRules[0].model == offers_models.OfferValidationModel.OFFERER
        assert rule.subRules[0].attribute == offers_models.OfferValidationAttribute.ID
        assert rule.subRules[0].operator == offers_models.OfferValidationRuleOperator.IN
        assert rule.subRules[0].comparated == {"comparated": [offerers[0].id, offerers[1].id]}

    def test_create_offer_validation_rule_with_multiple_rules(self, legit_user, authenticated_client):
        sub_rule_data_0 = get_empty_sub_rule_data(0) | {
            "sub_rules-0-sub_rule_type": "MAX_PRICE_OFFER",
            "sub_rules-0-operator": "GREATER_THAN",
            "sub_rules-0-decimal_field": "200",
        }
        sub_rule_data_1 = get_empty_sub_rule_data(1) | {
            "sub_rules-1-sub_rule_type": "CATEGORY_OFFER",
            "sub_rules-1-operator": "NOT_IN",
            "sub_rules-1-categories": ["INSTRUMENT"],
        }
        form = {"name": "First rule of robotics"} | sub_rule_data_0 | sub_rule_data_1

        response = self.post_to_endpoint(
            authenticated_client,
            form=form,
        )
        assert response.status_code == 303
        assert html_parser.extract_alert(authenticated_client.get(response.location).data) == "Règle créée avec succès"

        rule = offers_models.OfferValidationRule.query.one()
        assert rule.name == "First rule of robotics"
        assert rule.latestAuthor == legit_user
        assert rule.dateModified.date() == datetime.date.today()
        assert rule.subRules[0].model == offers_models.OfferValidationModel.OFFER
        assert rule.subRules[0].attribute == offers_models.OfferValidationAttribute.MAX_PRICE
        assert rule.subRules[0].operator == offers_models.OfferValidationRuleOperator.GREATER_THAN
        assert rule.subRules[0].comparated == {"comparated": 200}
        assert rule.subRules[1].model == offers_models.OfferValidationModel.OFFER
        assert rule.subRules[1].attribute == offers_models.OfferValidationAttribute.CATEGORY_ID
        assert rule.subRules[1].operator == offers_models.OfferValidationRuleOperator.NOT_IN
        assert rule.subRules[1].comparated == {"comparated": ["INSTRUMENT"]}

    def test_create_offer_validation_rule_without_name(self, authenticated_client):
        sub_rule_data = get_empty_sub_rule_data() | {
            "sub_rules-0-sub_rule_type": "DESCRIPTION_OFFER",
            "sub_rules-0-operator": "CONTAINS_EXACTLY",
            "sub_rules-0-list_field": "interdit, suspicious, verboten",
        }
        form = {"name": ""} | sub_rule_data

        response = self.post_to_endpoint(
            authenticated_client,
            form=form,
        )
        assert response.status_code == 303
        assert "Les données envoyées comportent des erreurs." in html_parser.extract_alert(
            authenticated_client.get(response.location).data
        )
        assert offers_models.OfferValidationRule.query.count() == 0

    def test_create_offer_validation_rule_without_chosen_type(self, authenticated_client):
        sub_rule_data = get_empty_sub_rule_data()
        form = {"name": "First rule of robotics"} | sub_rule_data

        response = self.post_to_endpoint(
            authenticated_client,
            form=form,
        )
        assert response.status_code == 303
        assert "Les données envoyées comportent des erreurs." in html_parser.extract_alert(
            authenticated_client.get(response.location).data
        )
        assert offers_models.OfferValidationRule.query.count() == 0

    def test_create_offer_validation_rule_without_operator(self, authenticated_client):
        sub_rule_data = get_empty_sub_rule_data() | {
            "sub_rules-0-sub_rule_type": "DESCRIPTION_OFFER",
            "sub_rules-0-list_field": "interdit, suspicious, verboten",
        }
        form = {"name": "First rule of robotics"} | sub_rule_data

        response = self.post_to_endpoint(
            authenticated_client,
            form=form,
        )
        assert response.status_code == 303
        assert "Les données envoyées comportent des erreurs." in html_parser.extract_alert(
            authenticated_client.get(response.location).data
        )
        assert offers_models.OfferValidationRule.query.count() == 0

    def test_create_offer_validation_rule_with_empty_comparated_data(self, authenticated_client):
        sub_rule_data = get_empty_sub_rule_data() | {
            "sub_rules-0-sub_rule_type": "DESCRIPTION_OFFER",
            "sub_rules-0-operator": "CONTAINS_EXACTLY",
            "sub_rules-0-list_field": "",
        }
        form = {"name": "First rule of robotics"} | sub_rule_data

        response = self.post_to_endpoint(
            authenticated_client,
            form=form,
        )
        assert response.status_code == 303
        assert "Les données envoyées comportent des erreurs." in html_parser.extract_alert(
            authenticated_client.get(response.location).data
        )
        assert offers_models.OfferValidationRule.query.count() == 0

    def test_create_offer_validation_rule_with_impossible_type_and_operator_combination(self, authenticated_client):
        sub_rule_data = get_empty_sub_rule_data() | {
            "sub_rules-0-sub_rule_type": "DESCRIPTION_OFFER",
            "sub_rules-0-operator": "EQUALS",
            "sub_rules-0-list_field": "interdit, suspicious, verboten",
        }
        form = {"name": ""} | sub_rule_data

        response = self.post_to_endpoint(
            authenticated_client,
            form=form,
        )
        assert response.status_code == 303
        assert "Les données envoyées comportent des erreurs." in html_parser.extract_alert(
            authenticated_client.get(response.location).data
        )
        assert offers_models.OfferValidationRule.query.count() == 0


class GetDeleteOfferValidationRuleFormTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.offer_validation_rules.delete_rule"
    endpoint_kwargs = {"rule_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_get_delete_form_test(self, legit_user, authenticated_client):
        rule = offers_factories.OfferValidationRuleFactory(name="First rule of robotics")
        offers_factories.OfferValidationSubRuleFactory(
            validationRule=rule,
            model=offers_models.OfferValidationModel.OFFER,
            attribute=offers_models.OfferValidationAttribute.NAME,
            operator=offers_models.OfferValidationRuleOperator.CONTAINS,
            comparated={"comparated": ["interdit", "suspicious", "verboten"]},
        )
        form_url = url_for(self.endpoint, rule_id=rule.id)

        with assert_num_queries(2):  # session + user
            response = authenticated_client.get(form_url)
            assert response.status_code == 200


class DeleteOfferValidationRuleTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.offer_validation_rules.delete_rule"
    endpoint_kwargs = {"rule_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_delete_offer_validation_rule(self, legit_user, authenticated_client):
        rule = offers_factories.OfferValidationRuleFactory(name="First rule of robotics")
        sub_rule_1 = offers_factories.OfferValidationSubRuleFactory(
            validationRule=rule,
            model=offers_models.OfferValidationModel.OFFER,
            attribute=offers_models.OfferValidationAttribute.NAME,
            operator=offers_models.OfferValidationRuleOperator.CONTAINS,
            comparated={"comparated": ["interdit", "suspicious", "verboten"]},
        )
        sub_rule_2 = offers_factories.OfferValidationSubRuleFactory(
            validationRule=rule,
            model=offers_models.OfferValidationModel.OFFER,
            attribute=offers_models.OfferValidationAttribute.DESCRIPTION,
            operator=offers_models.OfferValidationRuleOperator.CONTAINS_EXACTLY,
            comparated={"comparated": ["interdit", "suspicious", "verboten"]},
        )

        response = self.post_to_endpoint(authenticated_client, rule_id=rule.id)
        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == f"La règle {rule.name} et ses sous-règles ont été supprimées"
        )

        assert not offers_models.OfferValidationRule.query.filter_by(id=rule.id).one_or_none()
        assert not offers_models.OfferValidationRule.query.filter_by(id=sub_rule_1.id).one_or_none()
        assert not offers_models.OfferValidationRule.query.filter_by(id=sub_rule_2.id).one_or_none()


class GetEditOfferValidationRuleFormTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.offer_validation_rules.edit_rule"
    endpoint_kwargs = {"rule_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_get_edit_form_test(self, legit_user, authenticated_client):
        rule = offers_factories.OfferValidationRuleFactory(name="First rule of robotics")
        offers_factories.OfferValidationSubRuleFactory(
            validationRule=rule,
            model=offers_models.OfferValidationModel.OFFER,
            attribute=offers_models.OfferValidationAttribute.NAME,
            operator=offers_models.OfferValidationRuleOperator.CONTAINS,
            comparated={"comparated": ["interdit", "suspicious", "verboten"]},
        )
        form_url = url_for(self.endpoint, rule_id=rule.id)

        with assert_num_queries(3):  # session + user
            response = authenticated_client.get(form_url)
            assert response.status_code == 200


class EditOfferValidationRuleTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.offer_validation_rules.edit_rule"
    endpoint_kwargs = {"rule_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_edit_offer_validation_rule(self, legit_user, authenticated_client):
        rule = offers_factories.OfferValidationRuleFactory(
            name="First rule of robotics", dateModified=datetime.datetime.utcnow() - datetime.timedelta(days=1)
        )
        sub_rule = offers_factories.OfferValidationSubRuleFactory(
            validationRule=rule,
            model=offers_models.OfferValidationModel.OFFER,
            attribute=offers_models.OfferValidationAttribute.NAME,
            operator=offers_models.OfferValidationRuleOperator.CONTAINS,
            comparated={"comparated": ["interdit", "suspicious", "verboten"]},
        )
        sub_rule_data = get_empty_sub_rule_data() | {
            "sub_rules-0-id": str(sub_rule.id),
            "sub_rules-0-sub_rule_type": "DESCRIPTION_OFFER",
            "sub_rules-0-operator": "CONTAINS",
            "sub_rules-0-list_field": "interdit, suspicious, verboten, ajout",
        }
        form = {"name": "Second rule of robotics"} | sub_rule_data

        response = self.post_to_endpoint(authenticated_client, rule_id=rule.id, form=form)
        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == f"La règle {rule.name} et ses sous-règles ont été modifiées"
        )

        rule = offers_models.OfferValidationRule.query.one()
        assert rule.name == "Second rule of robotics"
        assert rule.latestAuthor == legit_user
        assert rule.dateModified.date() == datetime.date.today()
        assert rule.subRules[0].id == sub_rule.id
        assert rule.subRules[0].model == offers_models.OfferValidationModel.OFFER
        assert rule.subRules[0].attribute == offers_models.OfferValidationAttribute.DESCRIPTION
        assert rule.subRules[0].operator == offers_models.OfferValidationRuleOperator.CONTAINS
        assert rule.subRules[0].comparated == {"comparated": ["ajout", "interdit", "suspicious", "verboten"]}

    def test_edit_offer_validation_rule_add_sub_rule(self, legit_user, authenticated_client):
        rule = offers_factories.OfferValidationRuleFactory(
            name="First rule of robotics", dateModified=datetime.datetime.utcnow() - datetime.timedelta(days=1)
        )
        sub_rule = offers_factories.OfferValidationSubRuleFactory(
            validationRule=rule,
            model=offers_models.OfferValidationModel.OFFER,
            attribute=offers_models.OfferValidationAttribute.NAME,
            operator=offers_models.OfferValidationRuleOperator.CONTAINS,
            comparated={"comparated": ["interdit", "suspicious", "verboten"]},
        )
        old_sub_rule_id = sub_rule.id
        sub_rule_data_0 = get_empty_sub_rule_data(0) | {
            "sub_rules-0-id": str(old_sub_rule_id),
            "sub_rules-0-sub_rule_type": "DESCRIPTION_OFFER",
            "sub_rules-0-operator": "CONTAINS",
            "sub_rules-0-list_field": "interdit, suspicious, verboten, ajout",
        }
        sub_rule_data_1 = get_empty_sub_rule_data(1) | {
            "sub_rules-1-id": None,
            "sub_rules-1-sub_rule_type": "DESCRIPTION_COLLECTIVE_OFFER",
            "sub_rules-1-operator": "CONTAINS_EXACTLY",
            "sub_rules-1-list_field": "interdit, suspicious, verboten",
        }
        form = {"name": "Second rule of robotics"} | sub_rule_data_0 | sub_rule_data_1

        response = self.post_to_endpoint(authenticated_client, rule_id=rule.id, form=form)
        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == f"La règle {rule.name} et ses sous-règles ont été modifiées"
        )

        rule = offers_models.OfferValidationRule.query.one()
        assert rule.name == "Second rule of robotics"
        assert rule.latestAuthor == legit_user
        assert rule.dateModified.date() == datetime.date.today()
        assert rule.subRules[0].id == old_sub_rule_id
        assert rule.subRules[0].model == offers_models.OfferValidationModel.OFFER
        assert rule.subRules[0].attribute == offers_models.OfferValidationAttribute.DESCRIPTION
        assert rule.subRules[0].operator == offers_models.OfferValidationRuleOperator.CONTAINS
        assert rule.subRules[0].comparated == {"comparated": ["ajout", "interdit", "suspicious", "verboten"]}
        assert rule.subRules[1].id != old_sub_rule_id
        assert rule.subRules[1].model == offers_models.OfferValidationModel.COLLECTIVE_OFFER
        assert rule.subRules[1].attribute == offers_models.OfferValidationAttribute.DESCRIPTION
        assert rule.subRules[1].operator == offers_models.OfferValidationRuleOperator.CONTAINS_EXACTLY
        assert rule.subRules[1].comparated == {"comparated": ["interdit", "suspicious", "verboten"]}

    def test_edit_offer_validation_rule_delete_sub_rule(self, legit_user, authenticated_client):
        rule = offers_factories.OfferValidationRuleFactory(
            name="First rule of robotics", dateModified=datetime.datetime.utcnow() - datetime.timedelta(days=1)
        )
        sub_rule_1 = offers_factories.OfferValidationSubRuleFactory(
            validationRule=rule,
            model=offers_models.OfferValidationModel.OFFER,
            attribute=offers_models.OfferValidationAttribute.NAME,
            operator=offers_models.OfferValidationRuleOperator.CONTAINS,
            comparated={"comparated": ["interdit", "suspicious", "verboten"]},
        )
        sub_rule_2 = offers_factories.OfferValidationSubRuleFactory(
            validationRule=rule,
            model=offers_models.OfferValidationModel.COLLECTIVE_OFFER,
            attribute=offers_models.OfferValidationAttribute.NAME,
            operator=offers_models.OfferValidationRuleOperator.CONTAINS_EXACTLY,
            comparated={"comparated": ["interdit", "suspicious", "verboten"]},
        )
        sub_rule_data_0 = get_empty_sub_rule_data(0) | {
            "sub_rules-0-id": None,
            "sub_rules-0-sub_rule_type": "DESCRIPTION_OFFER",
            "sub_rules-0-operator": "CONTAINS",
            "sub_rules-0-list_field": "Riri, Fifi, Loulou",
        }
        sub_rule_data_1 = get_empty_sub_rule_data(1) | {
            "sub_rules-1-id": str(sub_rule_1.id),
            "sub_rules-1-sub_rule_type": "DESCRIPTION_COLLECTIVE_OFFER",
            "sub_rules-1-operator": "CONTAINS_EXACTLY",
            "sub_rules-1-list_field": "Astérix, Obélix",
        }
        form = {"name": "Second rule of robotics"} | sub_rule_data_0 | sub_rule_data_1

        response = self.post_to_endpoint(authenticated_client, rule_id=rule.id, form=form)
        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == f"La règle {rule.name} et ses sous-règles ont été modifiées"
        )

        rule = offers_models.OfferValidationRule.query.one()

        assert rule.name == "Second rule of robotics"
        assert rule.latestAuthor == legit_user
        assert rule.dateModified.date() == datetime.date.today()
        assert rule.subRules[0].id == sub_rule_1.id
        assert rule.subRules[0].model == offers_models.OfferValidationModel.COLLECTIVE_OFFER
        assert rule.subRules[0].attribute == offers_models.OfferValidationAttribute.DESCRIPTION
        assert rule.subRules[0].operator == offers_models.OfferValidationRuleOperator.CONTAINS_EXACTLY
        assert rule.subRules[0].comparated == {"comparated": ["asterix", "obelix"]}
        assert rule.subRules[1].id != sub_rule_1.id
        assert rule.subRules[1].model == offers_models.OfferValidationModel.OFFER
        assert rule.subRules[1].attribute == offers_models.OfferValidationAttribute.DESCRIPTION
        assert rule.subRules[1].operator == offers_models.OfferValidationRuleOperator.CONTAINS
        assert rule.subRules[1].comparated == {"comparated": ["fifi", "loulou", "riri"]}

        assert not offers_models.OfferValidationSubRule.query.filter_by(id=sub_rule_2.id).one_or_none()


class SearchRulesTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.offer_validation_rules.list_rules"
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_search_rule_by_rule_name(self, authenticated_client):
        rule = offers_factories.OfferValidationRuleFactory(
            name="Ma règle de conformité", dateModified=datetime.datetime.utcnow()
        )

        response = authenticated_client.get(url_for(self.endpoint, q="ma regle"))

        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)

        assert rows[0]["ID"] == str(rule.id)

    def test_search_rule_by_key_word(self, authenticated_client):
        rule = offers_factories.OfferValidationRuleFactory(
            name="Ma règle de conformité", dateModified=datetime.datetime.utcnow()
        )

        offers_factories.OfferValidationSubRuleFactory(
            validationRule=rule,
            model=offers_models.OfferValidationModel.OFFER,
            attribute=offers_models.OfferValidationAttribute.NAME,
            operator=offers_models.OfferValidationRuleOperator.CONTAINS,
            comparated={"comparated": ["suspicious"]},
        )

        response = authenticated_client.get(url_for(self.endpoint, q="suspicious"))

        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)

        assert rows[0]["ID"] == str(rule.id)

        extra_data = html_parser.extract(response.data, tag="tr", class_="collapse accordion-collapse")[0]
        assert "Le nom de l'offre individuelle" in extra_data
        assert "suspicious" in extra_data

    def test_search_rule_by_offerer(self, authenticated_client, offerer):
        rule = offers_factories.OfferValidationRuleFactory(
            name="Ma règle de conformité", dateModified=datetime.datetime.utcnow()
        )
        offers_factories.OfferValidationSubRuleFactory(
            validationRule=rule,
            model=offers_models.OfferValidationModel.OFFERER,
            attribute=offers_models.OfferValidationAttribute.ID,
            operator=offers_models.OfferValidationRuleOperator.IN,
            comparated={"comparated": [offerer.id]},
        )

        response = authenticated_client.get(url_for(self.endpoint, offerer=offerer.id))

        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)

        assert rows[0]["ID"] == str(rule.id)

    def test_search_rule_by_category(self, authenticated_client):
        rule = offers_factories.OfferValidationRuleFactory(
            name="Ma règle de conformité", dateModified=datetime.datetime.utcnow()
        )
        offers_factories.OfferValidationSubRuleFactory(
            validationRule=rule,
            model=offers_models.OfferValidationModel.OFFER,
            attribute=offers_models.OfferValidationAttribute.CATEGORY_ID,
            operator=offers_models.OfferValidationRuleOperator.IN,
            comparated={"comparated": ["CINEMA"]},
        )

        response = authenticated_client.get(url_for(self.endpoint, category="CINEMA"))

        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)

        assert rows[0]["ID"] == str(rule.id)

    def test_search_rule_by_subcategory(self, authenticated_client):
        rule = offers_factories.OfferValidationRuleFactory(
            name="Ma règle de conformité", dateModified=datetime.datetime.utcnow()
        )
        offers_factories.OfferValidationSubRuleFactory(
            validationRule=rule,
            model=offers_models.OfferValidationModel.OFFER,
            attribute=offers_models.OfferValidationAttribute.SUBCATEGORY_ID,
            operator=offers_models.OfferValidationRuleOperator.IN,
            comparated={"comparated": ["ABO_CONCERT"]},
        )

        response = authenticated_client.get(url_for(self.endpoint, subcategory="ABO_CONCERT"))

        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)

        assert rows[0]["ID"] == str(rule.id)

    def test_search_rule_with_multiple_filters(self, authenticated_client, offerer):
        rule = offers_factories.OfferValidationRuleFactory(
            name="Ma règle de conformité", dateModified=datetime.datetime.utcnow()
        )

        offers_factories.OfferValidationSubRuleFactory(
            validationRule=rule,
            model=offers_models.OfferValidationModel.OFFERER,
            attribute=offers_models.OfferValidationAttribute.ID,
            operator=offers_models.OfferValidationRuleOperator.IN,
            comparated={"comparated": [offerer.id]},
        )
        offers_factories.OfferValidationSubRuleFactory(
            validationRule=rule,
            model=offers_models.OfferValidationModel.OFFER,
            attribute=offers_models.OfferValidationAttribute.NAME,
            operator=offers_models.OfferValidationRuleOperator.CONTAINS,
            comparated={"comparated": ["suspicious"]},
        )
        offers_factories.OfferValidationSubRuleFactory(
            validationRule=rule,
            model=offers_models.OfferValidationModel.OFFER,
            attribute=offers_models.OfferValidationAttribute.SUBCATEGORY_ID,
            operator=offers_models.OfferValidationRuleOperator.IN,
            comparated={"comparated": ["ABO_CONCERT"]},
        )
        offers_factories.OfferValidationSubRuleFactory(
            validationRule=rule,
            model=offers_models.OfferValidationModel.OFFER,
            attribute=offers_models.OfferValidationAttribute.CATEGORY_ID,
            operator=offers_models.OfferValidationRuleOperator.IN,
            comparated={"comparated": ["CINEMA"]},
        )

        response = authenticated_client.get(
            url_for(self.endpoint, q="suspicious", offerer=offerer.id, category="CINEMA", subcategory="ABO_CONCERT")
        )

        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)

        assert rows[0]["ID"] == str(rule.id)


class UtilsTest:
    @pytest.mark.parametrize(
        "input_str,expected", [("mot-clé", "mot-cle"), ("MAJ", "maj"), ("Je suis un MOT-CLÉ", "je suis un mot-cle")]
    )
    def test_format_key_word(self, input_str, expected):
        assert utils.convert_to_unaccent_lowercase(input_str) == expected
