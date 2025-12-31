from operator import attrgetter

import pytest
from flask import url_for

from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.utils import date as date_utils

from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
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
    endpoint = "backoffice_web.offer_validation_rules.list_rules"
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    # session
    expected_num_queries = 2
    # offerer names and siren
    expected_num_queries_when_using_offerer = expected_num_queries + 1
    # venue names and siret
    expected_num_queries_when_using_venue = expected_num_queries + 1

    def test_list_rules(self, authenticated_client):
        rule = offers_factories.OfferValidationRuleFactory(name="Règles de fraude")
        offers_factories.OfferValidationSubRuleFactory(
            validationRule=rule,
            model=offers_models.OfferValidationModel.OFFER,
            attribute=offers_models.OfferValidationAttribute.NAME,
            operator=offers_models.OfferValidationRuleOperator.CONTAINS,
            comparated={"comparated": ["interdit", "suspicious", "verboten"]},
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)

        assert rows[0]["ID"] == str(rule.id)
        assert rows[0]["Nom"] == rule.name

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

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=q))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == expected_nb_results
        count = 0
        for index, key in enumerate(expected_results_key):
            for row in rows:
                if count < expected_nb_results and row[index]["Nom"] == rules.get(key).name:
                    count += 1
                    break

    def test_search_rule_by_rule_name(self, authenticated_client):
        rule = offers_factories.OfferValidationRuleFactory(name="Ma règle de conformité")

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="ma regle"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(rule.id)

    def test_search_rule_by_key_word(self, authenticated_client):
        rule = offers_factories.OfferValidationRuleFactory(name="Ma règle de conformité")

        offers_factories.OfferValidationSubRuleFactory(
            validationRule=rule,
            model=offers_models.OfferValidationModel.OFFER,
            attribute=offers_models.OfferValidationAttribute.NAME,
            operator=offers_models.OfferValidationRuleOperator.CONTAINS,
            comparated={"comparated": ["àCCêNTüé", "xxx", "yyy", "zzz"]},
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="Accentué"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(rule.id)

        extra_data = html_parser.extract(response.data, tag="tr", class_="collapse accordion-collapse")[0]
        assert "Le nom de l'offre individuelle" in extra_data
        assert "àCCêNTüé" in extra_data

    def test_search_rule_by_offerer(self, authenticated_client, offerer):
        rule = offers_factories.OfferValidationRuleFactory(name="Ma règle de conformité")
        offers_factories.OfferValidationSubRuleFactory(
            validationRule=rule,
            model=offers_models.OfferValidationModel.OFFERER,
            attribute=offers_models.OfferValidationAttribute.ID,
            operator=offers_models.OfferValidationRuleOperator.IN,
            comparated={"comparated": [offerer.id]},
        )

        offerer_id = offerer.id
        with assert_num_queries(self.expected_num_queries_when_using_offerer + 1):  # +1 to prefill offerers filter
            response = authenticated_client.get(url_for(self.endpoint, offerer=offerer_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(rule.id)

    def test_search_rule_by_offerer_which_does_no_longer_exist(
        self,
        authenticated_client,
    ):
        rule = offers_factories.OfferValidationRuleFactory(name="Ma règle de conformité")
        offers_factories.OfferValidationSubRuleFactory(
            validationRule=rule,
            model=offers_models.OfferValidationModel.OFFERER,
            attribute=offers_models.OfferValidationAttribute.ID,
            operator=offers_models.OfferValidationRuleOperator.IN,
            comparated={"comparated": [42]},
        )

        with assert_num_queries(self.expected_num_queries_when_using_offerer + 1):  # +1 to prefill offerers filter
            response = authenticated_client.get(url_for(self.endpoint, offerer=42))
            assert response.status_code == 200

        assert "L'entité juridique proposant l'offre est parmi Offerer ID : 42" in html_parser.content_as_text(
            response.data
        )

    def test_search_rule_by_venue(self, authenticated_client):
        venue = offerers_factories.VenueFactory(publicName="Your flowers are beautiful")
        other_venue = offerers_factories.VenueFactory(publicName="Your flowers are not beautiful")
        rule = offers_factories.OfferValidationRuleFactory(name="Ma règle de conformité")
        offers_factories.OfferValidationSubRuleFactory(
            validationRule=rule,
            model=offers_models.OfferValidationModel.VENUE,
            attribute=offers_models.OfferValidationAttribute.ID,
            operator=offers_models.OfferValidationRuleOperator.IN,
            comparated={"comparated": [venue.id, other_venue.id]},
        )

        venue_id = venue.id
        with assert_num_queries(self.expected_num_queries_when_using_venue + 1):  # +1 to prefill venues filter
            response = authenticated_client.get(url_for(self.endpoint, venue=venue_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(rule.id)

    def test_search_rule_by_venue_which_does_no_longer_exist(
        self,
        authenticated_client,
    ):
        rule = offers_factories.OfferValidationRuleFactory(name="Ma règle de conformité")
        offers_factories.OfferValidationSubRuleFactory(
            validationRule=rule,
            model=offers_models.OfferValidationModel.VENUE,
            attribute=offers_models.OfferValidationAttribute.ID,
            operator=offers_models.OfferValidationRuleOperator.IN,
            comparated={"comparated": [42]},
        )

        with assert_num_queries(self.expected_num_queries_when_using_venue + 1):  # +1 to prefill venues filter
            response = authenticated_client.get(url_for(self.endpoint, venue=42))
            assert response.status_code == 200

        assert "Le partenaire culturel proposant l'offre est parmi Venue ID : 42" in html_parser.content_as_text(
            response.data
        )

    def test_search_rule_by_category(self, authenticated_client):
        rule = offers_factories.OfferValidationRuleFactory(name="Ma règle de conformité")
        offers_factories.OfferValidationSubRuleFactory(
            validationRule=rule,
            model=offers_models.OfferValidationModel.OFFER,
            attribute=offers_models.OfferValidationAttribute.CATEGORY_ID,
            operator=offers_models.OfferValidationRuleOperator.IN,
            comparated={"comparated": ["CINEMA"]},
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, category="CINEMA"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(rule.id)

    def test_search_rule_by_subcategory(self, authenticated_client):
        rule = offers_factories.OfferValidationRuleFactory(name="Ma règle de conformité")
        offers_factories.OfferValidationSubRuleFactory(
            validationRule=rule,
            model=offers_models.OfferValidationModel.OFFER,
            attribute=offers_models.OfferValidationAttribute.SUBCATEGORY_ID,
            operator=offers_models.OfferValidationRuleOperator.IN,
            comparated={"comparated": ["ABO_CONCERT"]},
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, subcategory="ABO_CONCERT"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(rule.id)

    def test_search_rule_with_multiple_filters(self, authenticated_client, offerer):
        rule = offers_factories.OfferValidationRuleFactory(name="Ma règle de conformité")

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

        offerer_id = offerer.id
        with assert_num_queries(self.expected_num_queries_when_using_offerer + 1):  # +1 to prefill offerers filter
            response = authenticated_client.get(
                url_for(self.endpoint, q="suspicious", offerer=offerer_id, category="CINEMA", subcategory="ABO_CONCERT")
            )
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(rule.id)

    def test_search_rule_with_multiple_filters_matching_twice(self, authenticated_client):
        rule = offers_factories.OfferValidationRuleFactory(name="Ma règle de conformité")

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
            attribute=offers_models.OfferValidationAttribute.DESCRIPTION,
            operator=offers_models.OfferValidationRuleOperator.CONTAINS,
            comparated={"comparated": ["suspicious"]},
        )
        offers_factories.OfferValidationSubRuleFactory(
            validationRule=rule,
            model=offers_models.OfferValidationModel.OFFER,
            attribute=offers_models.OfferValidationAttribute.CATEGORY_ID,
            operator=offers_models.OfferValidationRuleOperator.IN,
            comparated={"comparated": ["CINEMA"]},
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="suspicious"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(rule.id)

        extra_data = html_parser.extract(response.data, tag="tr", class_="collapse accordion-collapse")[0]
        assert "La catégorie de l'offre individuelle est parmi Cinéma" in extra_data
        assert "La description de l'offre individuelle contient suspicious" in extra_data
        assert "Le nom de l'offre individuelle contient suspicious" in extra_data


class GetCreateOfferValidationRuleFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.offer_validation_rules.create_rule"
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_get_create_form_test(self, legit_user, authenticated_client):
        form_url = url_for(self.endpoint)

        with assert_num_queries(1):  # session
            response = authenticated_client.get(form_url)
            assert response.status_code == 200


class CreateOfferValidationRuleTest(PostEndpointHelper):
    endpoint = "backoffice_web.offer_validation_rules.create_rule"
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    @pytest.mark.parametrize(
        "form_data, expected_result",
        [
            (
                {
                    "sub_rules-0-sub_rule_type": "DESCRIPTION_OFFER",
                    "sub_rules-0-operator": "CONTAINS_EXACTLY",
                    "sub_rules-0-list_field": "âne, Célèbre, Interdit",
                },
                {
                    "model": offers_models.OfferValidationModel.OFFER,
                    "attribute": offers_models.OfferValidationAttribute.DESCRIPTION,
                    "operator": offers_models.OfferValidationRuleOperator.CONTAINS_EXACTLY,
                    "comparated": {"comparated": ["âne", "Célèbre", "Interdit"]},
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
            (
                {
                    "sub_rules-0-sub_rule_type": "FORMATS_COLLECTIVE_OFFER",
                    "sub_rules-0-operator": "INTERSECTS",
                    "sub_rules-0-formats": ["CONCERT", "VISITE_LIBRE"],
                },
                {
                    "model": offers_models.OfferValidationModel.COLLECTIVE_OFFER,
                    "attribute": offers_models.OfferValidationAttribute.FORMATS,
                    "operator": offers_models.OfferValidationRuleOperator.INTERSECTS,
                    "comparated": {"comparated": ["CONCERT", "VISITE_LIBRE"]},
                },
            ),
            (
                {
                    "sub_rules-0-sub_rule_type": "FORMATS_COLLECTIVE_OFFER_TEMPLATE",
                    "sub_rules-0-operator": "NOT_INTERSECTS",
                    "sub_rules-0-formats": ["CONCERT", "VISITE_LIBRE"],
                },
                {
                    "model": offers_models.OfferValidationModel.COLLECTIVE_OFFER_TEMPLATE,
                    "attribute": offers_models.OfferValidationAttribute.FORMATS,
                    "operator": offers_models.OfferValidationRuleOperator.NOT_INTERSECTS,
                    "comparated": {"comparated": ["CONCERT", "VISITE_LIBRE"]},
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
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "La nouvelle règle a été créée"
        )

        rule = db.session.query(offers_models.OfferValidationRule).one()
        assert rule.name == "First rule of robotics"
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
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "La nouvelle règle a été créée"
        )

        rule = db.session.query(offers_models.OfferValidationRule).one()
        assert rule.name == "First rule of robotics"
        assert rule.subRules[0].model == offers_models.OfferValidationModel.OFFERER
        assert rule.subRules[0].attribute == offers_models.OfferValidationAttribute.ID
        assert rule.subRules[0].operator == offers_models.OfferValidationRuleOperator.IN
        assert rule.subRules[0].comparated == {"comparated": [offerers[0].id, offerers[1].id]}

    def test_create_offer_validation_rule_with_venue_id(self, legit_user, authenticated_client):
        venues = offerers_factories.VenueFactory.create_batch(2)
        sub_rule_data = get_empty_sub_rule_data() | {
            "sub_rules-0-sub_rule_type": "ID_VENUE",
            "sub_rules-0-operator": "IN",
            "sub_rules-0-venue": [venues[0].id, venues[1].id],
        }
        form = {"name": "First rule of robotics"} | sub_rule_data

        response = self.post_to_endpoint(
            authenticated_client,
            form=form,
        )
        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "La nouvelle règle a été créée"
        )

        rule = db.session.query(offers_models.OfferValidationRule).one()
        assert rule.name == "First rule of robotics"
        assert rule.subRules[0].model == offers_models.OfferValidationModel.VENUE
        assert rule.subRules[0].attribute == offers_models.OfferValidationAttribute.ID
        assert rule.subRules[0].operator == offers_models.OfferValidationRuleOperator.IN
        assert rule.subRules[0].comparated == {"comparated": [venues[0].id, venues[1].id]}

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
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "La nouvelle règle a été créée"
        )

        rule = db.session.query(offers_models.OfferValidationRule).one()
        assert rule.name == "First rule of robotics"
        assert rule.subRules[0].model == offers_models.OfferValidationModel.OFFER
        assert rule.subRules[0].attribute == offers_models.OfferValidationAttribute.MAX_PRICE
        assert rule.subRules[0].operator == offers_models.OfferValidationRuleOperator.GREATER_THAN
        assert rule.subRules[0].comparated == {"comparated": 200}
        assert rule.subRules[1].model == offers_models.OfferValidationModel.OFFER
        assert rule.subRules[1].attribute == offers_models.OfferValidationAttribute.CATEGORY_ID
        assert rule.subRules[1].operator == offers_models.OfferValidationRuleOperator.NOT_IN
        assert rule.subRules[1].comparated == {"comparated": ["INSTRUMENT"]}

        action_history = db.session.query(history_models.ActionHistory).one()
        assert action_history.authorUser == legit_user
        assert action_history.actionType == history_models.ActionType.RULE_CREATED
        assert action_history.rule.name == rule.name

        assert len(action_history.extraData["sub_rules_info"]["sub_rules_created"]) == 2
        assert {
            "id": rule.subRules[0].id,
            "model": "OFFER",
            "attribute": "MAX_PRICE",
            "operator": "GREATER_THAN",
            "comparated": 200,
        } in action_history.extraData["sub_rules_info"]["sub_rules_created"]
        assert {
            "id": rule.subRules[1].id,
            "model": "OFFER",
            "attribute": "CATEGORY_ID",
            "operator": "NOT_IN",
            "comparated": ["INSTRUMENT"],
        } in action_history.extraData["sub_rules_info"]["sub_rules_created"]

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
        assert db.session.query(offers_models.OfferValidationRule).count() == 0

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
        assert db.session.query(offers_models.OfferValidationRule).count() == 0

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
        assert db.session.query(offers_models.OfferValidationRule).count() == 0

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
        assert db.session.query(offers_models.OfferValidationRule).count() == 0

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
        assert db.session.query(offers_models.OfferValidationRule).count() == 0


class GetDeleteOfferValidationRuleFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.offer_validation_rules.get_delete_offer_validation_rule_form"
    endpoint_kwargs = {"rule_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    expected_num_queries = 2  # session + rule

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

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(form_url)
            assert response.status_code == 200

    def test_no_script_injection_in_rule_name(self, legit_user, authenticated_client):
        rule = offers_factories.OfferValidationRuleFactory(name="<script>alert('coucou')</script>")
        form_url = url_for(self.endpoint, rule_id=rule.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(form_url)
            assert response.status_code == 200

        assert (
            "La règle <script>alert('coucou')</script> et ses sous-règles seront définitivement supprimées de la base "
            "de données. Veuillez confirmer ce choix." in html_parser.content_as_text(response.data)
        )


class DeleteOfferValidationRuleTest(PostEndpointHelper):
    endpoint = "backoffice_web.offer_validation_rules.delete_rule"
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

        rule = db.session.query(offers_models.OfferValidationRule).one()
        assert rule.isActive is False
        assert db.session.query(offers_models.OfferValidationSubRule).filter_by(id=sub_rule_1.id).one_or_none() is None
        assert db.session.query(offers_models.OfferValidationSubRule).filter_by(id=sub_rule_2.id).one_or_none() is None

        action_history = db.session.query(history_models.ActionHistory).one()
        assert action_history.authorUser == legit_user
        assert action_history.actionType == history_models.ActionType.RULE_DELETED
        assert action_history.rule.name == rule.name
        assert len(action_history.extraData["sub_rules_info"]["sub_rules_deleted"]) == 2
        assert {
            "id": sub_rule_1.id,
            "model": "OFFER",
            "attribute": "NAME",
            "operator": "CONTAINS",
            "comparated": ["interdit", "suspicious", "verboten"],
        } in action_history.extraData["sub_rules_info"]["sub_rules_deleted"]
        assert {
            "id": sub_rule_2.id,
            "model": "OFFER",
            "attribute": "DESCRIPTION",
            "operator": "CONTAINS_EXACTLY",
            "comparated": ["interdit", "suspicious", "verboten"],
        } in action_history.extraData["sub_rules_info"]["sub_rules_deleted"]

    def test_no_script_injection_in_rule_name(self, legit_user, authenticated_client):
        rule = offers_factories.OfferValidationRuleFactory(name="<script>alert('coucou')</script>")

        response = self.post_to_endpoint(authenticated_client, rule_id=rule.id)
        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "La règle <script>alert('coucou')</script> et ses sous-règles ont été supprimées"
        )


class GetEditOfferValidationRuleFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.offer_validation_rules.edit_rule"
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

        with assert_num_queries(3):  # session + rule + sub rule
            response = authenticated_client.get(form_url)
            assert response.status_code == 200


class EditOfferValidationRuleTest(PostEndpointHelper):
    endpoint = "backoffice_web.offer_validation_rules.edit_rule"
    endpoint_kwargs = {"rule_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_edit_offer_validation_rule(self, legit_user, authenticated_client):
        rule = offers_factories.OfferValidationRuleFactory(name="First rule of robotics")
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

        rule = db.session.query(offers_models.OfferValidationRule).one()
        assert rule.name == "Second rule of robotics"
        assert rule.subRules[0].id == sub_rule.id
        assert rule.subRules[0].model == offers_models.OfferValidationModel.OFFER
        assert rule.subRules[0].attribute == offers_models.OfferValidationAttribute.DESCRIPTION
        assert rule.subRules[0].operator == offers_models.OfferValidationRuleOperator.CONTAINS
        assert rule.subRules[0].comparated == {"comparated": ["ajout", "interdit", "suspicious", "verboten"]}

    def test_edit_offer_validation_rule_add_sub_rule(self, legit_user, authenticated_client):
        rule = offers_factories.OfferValidationRuleFactory(name="First rule of robotics")
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

        rule = db.session.query(offers_models.OfferValidationRule).one()
        assert rule.name == "Second rule of robotics"

        # sort to avoid flaky test
        sub_rules = sorted(rule.subRules, key=attrgetter("id"))
        assert sub_rules[0].id == old_sub_rule_id
        assert sub_rules[0].model == offers_models.OfferValidationModel.OFFER
        assert sub_rules[0].attribute == offers_models.OfferValidationAttribute.DESCRIPTION
        assert sub_rules[0].operator == offers_models.OfferValidationRuleOperator.CONTAINS
        assert sub_rules[0].comparated == {"comparated": ["ajout", "interdit", "suspicious", "verboten"]}
        assert sub_rules[1].id != old_sub_rule_id
        assert sub_rules[1].model == offers_models.OfferValidationModel.COLLECTIVE_OFFER
        assert sub_rules[1].attribute == offers_models.OfferValidationAttribute.DESCRIPTION
        assert sub_rules[1].operator == offers_models.OfferValidationRuleOperator.CONTAINS_EXACTLY
        assert sub_rules[1].comparated == {"comparated": ["interdit", "suspicious", "verboten"]}

        action_history = db.session.query(history_models.ActionHistory).one()
        assert action_history.authorUser == legit_user
        assert action_history.actionType == history_models.ActionType.RULE_MODIFIED
        assert action_history.rule.name == rule.name
        assert len(action_history.extraData["sub_rules_info"]["sub_rules_deleted"]) == 1
        assert len(action_history.extraData["sub_rules_info"]["sub_rules_modified"]) == 0
        assert len(action_history.extraData["sub_rules_info"]["sub_rules_created"]) == 2
        assert {
            "id": sub_rules[0].id,
            "model": "OFFER",
            "attribute": "NAME",
            "operator": "CONTAINS",
            "comparated": ["interdit", "suspicious", "verboten"],
        } in action_history.extraData["sub_rules_info"]["sub_rules_deleted"]
        assert {
            "id": sub_rules[1].id,
            "model": "COLLECTIVE_OFFER",
            "attribute": "DESCRIPTION",
            "operator": "CONTAINS_EXACTLY",
            "comparated": ["interdit", "suspicious", "verboten"],
        } in action_history.extraData["sub_rules_info"]["sub_rules_created"]
        assert {
            "id": sub_rules[0].id,
            "model": "OFFER",
            "attribute": "DESCRIPTION",
            "operator": "CONTAINS",
            "comparated": ["ajout", "interdit", "suspicious", "verboten"],
        } in action_history.extraData["sub_rules_info"]["sub_rules_created"]

    def test_edit_offer_validation_rule_delete_sub_rule(self, legit_user, authenticated_client):
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
            "sub_rules-1-sub_rule_type": "NAME_OFFER",
            "sub_rules-1-operator": "CONTAINS",
            "sub_rules-1-list_field": "Astérix, Obélix, verboten",
        }
        form = {"name": "Second rule of robotics"} | sub_rule_data_0 | sub_rule_data_1

        response = self.post_to_endpoint(authenticated_client, rule_id=rule.id, form=form)
        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == f"La règle {rule.name} et ses sous-règles ont été modifiées"
        )

        rule = db.session.query(offers_models.OfferValidationRule).one()

        assert rule.name == "Second rule of robotics"

        # sort to avoid flaky test
        sub_rules = sorted(rule.subRules, key=attrgetter("id"))
        assert sub_rules[0].id == sub_rule_1.id
        assert sub_rules[0].model == offers_models.OfferValidationModel.OFFER
        assert sub_rules[0].attribute == offers_models.OfferValidationAttribute.NAME
        assert sub_rules[0].operator == offers_models.OfferValidationRuleOperator.CONTAINS
        assert sub_rules[0].comparated == {"comparated": ["Astérix", "Obélix", "verboten"]}
        assert sub_rules[1].id != sub_rule_1.id
        assert sub_rules[1].model == offers_models.OfferValidationModel.OFFER
        assert sub_rules[1].attribute == offers_models.OfferValidationAttribute.DESCRIPTION
        assert sub_rules[1].operator == offers_models.OfferValidationRuleOperator.CONTAINS
        assert sub_rules[1].comparated == {"comparated": ["Fifi", "Loulou", "Riri"]}

        assert not db.session.query(offers_models.OfferValidationSubRule).filter_by(id=sub_rule_2.id).one_or_none()

        action_history = db.session.query(history_models.ActionHistory).one()
        assert action_history.authorUser == legit_user
        assert action_history.actionType == history_models.ActionType.RULE_MODIFIED
        assert action_history.rule.name == rule.name
        assert len(action_history.extraData["sub_rules_info"]["sub_rules_deleted"]) == 1
        assert len(action_history.extraData["sub_rules_info"]["sub_rules_modified"]) == 1
        assert len(action_history.extraData["sub_rules_info"]["sub_rules_created"]) == 1
        assert {
            "id": sub_rule_2.id,
            "model": "COLLECTIVE_OFFER",
            "attribute": "NAME",
            "operator": "CONTAINS_EXACTLY",
            "comparated": ["interdit", "suspicious", "verboten"],
        } in action_history.extraData["sub_rules_info"]["sub_rules_deleted"]
        assert {
            "id": sub_rule_1.id,
            "model": "OFFER",
            "attribute": "NAME",
            "operator": "CONTAINS",
            "comparated": {"added": ["Astérix", "Obélix"], "removed": ["interdit", "suspicious"]},
        } in action_history.extraData["sub_rules_info"]["sub_rules_modified"]
        assert {
            "id": sub_rules[1].id,
            "model": "OFFER",
            "attribute": "DESCRIPTION",
            "operator": "CONTAINS",
            "comparated": ["Fifi", "Loulou", "Riri"],
        } in action_history.extraData["sub_rules_info"]["sub_rules_created"]


class ListRulesHistoryTest(GetEndpointHelper):
    endpoint = "backoffice_web.offer_validation_rules.get_rules_history"
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    # session
    expected_num_queries = 2
    # offerer names and siren
    expected_num_queries_when_using_offerer = expected_num_queries + 1

    def test_list_rules_history(self, authenticated_client, legit_user):
        rule = offers_factories.OfferValidationRuleFactory(name="Règles de fraude")
        rule_creation_history = history_factories.ActionHistoryFactory(
            ruleId=rule.id,
            actionType=history_models.ActionType.RULE_CREATED,
            actionDate=date_utils.get_naive_utc_now(),
            authorUser=legit_user,
            comment=None,
            extraData={
                "sub_rules_info": {
                    "sub_rules_created": [
                        {
                            "id": 1,
                            "model": "OFFER",
                            "attribute": "SUBCATEGORY_ID",
                            "operator": "CONTAINS",
                            "comparated": ["ESCAPE_GAME", "RENCONTRE_JEU"],
                        },
                        {
                            "id": 2,
                            "model": "OFFER",
                            "attribute": "DESCRIPTION",
                            "operator": "CONTAINS",
                            "comparated": ["Fifi", "Loulou", "Riri"],
                        },
                    ]
                },
            },
        )
        # totally change the first one; change the comparated only for the second one
        rule_modification_history = history_factories.ActionHistoryFactory(
            ruleId=rule.id,
            actionType=history_models.ActionType.RULE_MODIFIED,
            actionDate=date_utils.get_naive_utc_now(),
            authorUser=legit_user,
            comment=None,
            extraData={
                "sub_rules_info": {
                    "sub_rules_created": [
                        {
                            "id": 1,
                            "model": "OFFER",
                            "attribute": "MAX_PRICE",
                            "operator": "GREATER_THAN",
                            "comparated": 12,
                        },
                    ],
                    "sub_rules_modified": [
                        {
                            "id": 2,
                            "model": "OFFER",
                            "attribute": "DESCRIPTION",
                            "operator": "CONTAINS",
                            "comparated": {"added": ["Foufou, Rourou"], "removed": ["Fifi, Riri"]},
                        },
                    ],
                    "sub_rules_deleted": [
                        {
                            "id": 1,
                            "model": "OFFER",
                            "attribute": "SUBCATEGORY_ID",
                            "operator": "CONTAINS",
                            "comparated": ["ESCAPE_GAME", "RENCONTRE_JEU"],
                        },
                    ],
                },
            },
        )
        rule_deletion_history = history_factories.ActionHistoryFactory(
            ruleId=rule.id,
            actionType=history_models.ActionType.RULE_DELETED,
            actionDate=date_utils.get_naive_utc_now(),
            authorUser=legit_user,
            comment=None,
            extraData={
                "sub_rules_info": {
                    "sub_rules_deleted": [
                        {
                            "id": 1,
                            "model": "OFFER",
                            "attribute": "MAX_PRICE",
                            "operator": "GREATER_THAN",
                            "comparated": 12,
                        },
                        {
                            "id": 2,
                            "model": "OFFER",
                            "attribute": "DESCRIPTION",
                            "operator": "CONTAINS",
                            "comparated": ["Foufou, Loulou, Rourou"],
                        },
                    ],
                },
            },
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        deletion_history_row, modification_history_row, creation_history_row = rows[0], rows[1], rows[2]

        assert creation_history_row["Type"] == "Création d'une règle de conformité"
        assert creation_history_row["Date/Heure"].startswith(rule_creation_history.actionDate.strftime("%d/%m/%Y à"))
        assert creation_history_row["Auteur"] == legit_user.full_name
        for text in [
            rule.name,
            "Ajout de sous-règle(s) :",
            "La sous-catégorie de l'offre individuelle contient",
            "Escape game",
            "Rencontres - jeux",
            "La description de l'offre individuelle contient",
            "Riri",
            "Fifi",
            "Loulou",
        ]:
            assert text in creation_history_row["Commentaire"]
        assert "Modification de sous-règle(s) :" not in creation_history_row["Commentaire"]
        assert "Suppression de sous-règle(s) :" not in creation_history_row["Commentaire"]

        assert modification_history_row["Type"] == "Modification d'une règle de conformité"
        assert modification_history_row["Date/Heure"].startswith(
            rule_modification_history.actionDate.strftime("%d/%m/%Y à")
        )
        assert modification_history_row["Auteur"] == legit_user.full_name

        for text in [
            rule.name,
            "Ajout de sous-règle(s) :",
            "Le prix max de l'offre individuelle est supérieur à 12",
            "Suppression de sous-règle(s) :",
            "La sous-catégorie de l'offre individuelle contient",
            "Escape game",
            "Rencontres - jeux",
            "Modification de sous-règle(s) :",
            "La description de l'offre individuelle contient",
            "Ajout de : Foufou, Rourou",
            "Suppression de : Fifi, Riri",
        ]:
            assert text in modification_history_row["Commentaire"]
        assert "Loulou" not in modification_history_row["Commentaire"]

        assert deletion_history_row["Type"] == "Suppression d'une règle de conformité"
        assert deletion_history_row["Date/Heure"].startswith(rule_deletion_history.actionDate.strftime("%d/%m/%Y à"))
        assert deletion_history_row["Auteur"] == legit_user.full_name
        for text in [
            rule.name,
            "Suppression de sous-règle(s) :",
            "Le prix max de l'offre individuelle est supérieur à 12",
            "La description de l'offre individuelle contient",
            "Foufou",
            "Loulou",
            "Rourou",
        ]:
            assert text in deletion_history_row["Commentaire"]
        assert "Modification de sous-règle(s) :" not in deletion_history_row["Commentaire"]
        assert "Création de sous-règle(s) :" not in deletion_history_row["Commentaire"]
