import datetime

from flask import url_for
import pytest

from pcapi.core.categories import subcategories_v2
from pcapi.core.finance import factories as finance_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_num_queries

from .helpers import html_parser
from .helpers import unauthorized as unauthorized_helpers


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class ListCustomReimbursementRulesTest:
    endpoint = "backoffice_v3_web.reimbursement_rules.list_custom_reimbursement_rules"

    # Use assert_num_queries() instead of assert_no_duplicated_queries() which does not detect one extra query caused
    # by a field added in the jinja template.
    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch custom reimbursement rules with extra data (1 query)
    expected_num_queries = 3

    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.reimbursement_rules.list_custom_reimbursement_rules"
        needed_permission = perm_models.Permissions.READ_REIMBURSEMENT_RULES

    def test_list_custom_reimbursement_rules(self, authenticated_client):
        start = datetime.datetime.utcnow() - datetime.timedelta(days=365)
        end = datetime.datetime.utcnow() + datetime.timedelta(days=365)
        offer_rule = finance_factories.CustomReimbursementRuleFactory(amount=27, timespan=(start, None))
        offerer = offerers_factories.OffererFactory()
        offerer_rule = finance_factories.CustomReimbursementRuleFactory(
            offerer=offerer, rate=0.5, subcategories=["FESTIVAL_LIVRE"]
        )

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2

        rows = sorted(rows, key=lambda row: int(row["ID règle"]))

        assert rows[0]["ID règle"] == str(offer_rule.id)
        assert rows[0]["Structure"] == offer_rule.offer.venue.managingOfferer.name
        assert rows[0]["SIREN"] == offer_rule.offer.venue.managingOfferer.siren
        assert rows[0]["Lieu"] == offer_rule.offer.venue.name
        assert rows[0]["Offre"] == offer_rule.offer.name
        assert rows[0]["Taux de remboursement"] == ""
        assert rows[0]["Montant remboursé"] == "27,00 €"
        assert rows[0]["Sous-catégories"] == ""
        assert rows[0]["Date d'application"] == start.strftime("%d/%m/%Y") + " → ∞"

        assert rows[1]["ID règle"] == str(offerer_rule.id)
        assert rows[1]["Structure"] == offerer_rule.offerer.name
        assert rows[1]["SIREN"] == offerer_rule.offerer.siren
        assert rows[1]["Lieu"] == ""
        assert rows[1]["Offre"] == ""
        assert rows[1]["Taux de remboursement"] == "50,00 %"
        assert rows[1]["Montant remboursé"] == ""
        assert rows[1]["Sous-catégories"] == subcategories_v2.FESTIVAL_LIVRE.pro_label
        assert rows[1]["Date d'application"] == start.strftime("%d/%m/%Y") + " → " + end.strftime("%d/%m/%Y")

        assert html_parser.extract_pagination_info(response.data) == (1, 1, len(rows))

    def test_list_rules_by_offer_id(self, authenticated_client):
        offer_rule = finance_factories.CustomReimbursementRuleFactory()
        searched_id = str(offer_rule.offerId)
        finance_factories.CustomReimbursementRuleFactory.create_batch(2)

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=searched_id))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID règle"] == str(offer_rule.id)

        assert html_parser.extract_pagination_info(response.data) == (1, 1, len(rows))

    def test_list_rules_by_offer_name(self, authenticated_client):
        offer = offers_factories.OfferFactory(name="Comment obtenir un tarif dérogatoire au pass")
        offer_rule = finance_factories.CustomReimbursementRuleFactory(offer=offer)
        finance_factories.CustomReimbursementRuleFactory.create_batch(2)
        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, q="Comment obtenir un tarif dérogatoire au pass")
            )

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID règle"] == str(offer_rule.id)

        assert html_parser.extract_pagination_info(response.data) == (1, 1, len(rows))

    def test_list_rules_by_id_not_found(self, authenticated_client):
        rules = finance_factories.CustomReimbursementRuleFactory.create_batch(5)
        # when
        search_query = str(rules[-1].id * 1000)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=search_query))

        # then
        assert response.status_code == 200
        assert html_parser.count_table_rows(response.data) == 0

    def test_list_rules_by_offerer(self, authenticated_client):
        offerer_1 = offerers_factories.OffererFactory()
        offerer_rule_1 = finance_factories.CustomReimbursementRuleFactory(offerer=offerer_1)
        offerer_2 = offerers_factories.OffererFactory()
        offerer_rule_2 = finance_factories.CustomReimbursementRuleFactory(offerer=offerer_2)
        other_offerer = offerers_factories.OffererFactory()
        finance_factories.CustomReimbursementRuleFactory(offerer=other_offerer)
        offer = offers_factories.OfferFactory(venue__managingOfferer=offerer_1)
        offerer_rule_3 = finance_factories.CustomReimbursementRuleFactory(offer=offer)

        # when
        offerer_ids = [offerer_1.id, offerer_2.id]
        with assert_num_queries(self.expected_num_queries + 1):
            response = authenticated_client.get(url_for(self.endpoint, offerer=offerer_ids))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID règle"]) for row in rows) == {offerer_rule_1.id, offerer_rule_2.id, offerer_rule_3.id}

    def test_list_rules_more_than_max(self, authenticated_client):
        # given
        finance_factories.CustomReimbursementRuleFactory.create_batch(30)

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, limit=25))

        # then
        assert response.status_code == 200
        assert html_parser.count_table_rows(response.data) == 25  # extra data in second row for each booking
        assert "Il y a plus de 25 résultats dans la base de données" in html_parser.extract_alert(response.data)
