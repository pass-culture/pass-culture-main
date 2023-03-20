import datetime

from flask import g
from flask import url_for
import pytest

from pcapi.core.categories import categories
from pcapi.core.categories import subcategories
from pcapi.core.criteria import factories as criteria_factories
from pcapi.core.offers import factories as offers_factories
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import assert_num_queries
from pcapi.routes.backoffice_v3.forms import offer as offer_forms

from .helpers import html_parser
from .helpers import unauthorized as unauthorized_helpers


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


@pytest.fixture(scope="function", name="criteria")
def criteria_fixture() -> list:
    return criteria_factories.CriterionFactory.create_batch(4)


@pytest.fixture(scope="function", name="offers")
def offers_fixture(criteria) -> tuple:
    offer_with_unlimited_stock = offers_factories.OfferFactory(
        criteria=[criteria[0]],
        venue__postalCode="47000",
        venue__departementCode="47",
        product__subcategoryId=subcategories.MATERIEL_ART_CREATIF.id,
    )
    offer_with_limited_stock = offers_factories.OfferFactory(
        name="A Very Specific Name",
        lastValidationDate=datetime.date(2022, 2, 22),
        venue__postalCode="97400",
        venue__departementCode="974",
        product__subcategoryId=subcategories.LIVRE_AUDIO_PHYSIQUE.id,
        extraData={"visa": "2023123456"},
    )
    offer_with_two_criteria = offers_factories.OfferFactory(
        name="A Very Specific Name That Is Longer",
        criteria=[criteria[0], criteria[1]],
        venue__postalCode="74000",
        venue__departementCode="74",
        product__subcategoryId=subcategories.LIVRE_PAPIER.id,
        extraData={"isbn": "9781234567890"},
    )
    offers_factories.StockFactory(quantity=None, offer=offer_with_unlimited_stock)
    offers_factories.StockFactory(offer=offer_with_unlimited_stock)
    offers_factories.StockFactory(quantity=10, dnBookedQuantity=0, offer=offer_with_limited_stock)
    offers_factories.StockFactory(quantity=10, dnBookedQuantity=5, offer=offer_with_limited_stock)
    return offer_with_unlimited_stock, offer_with_limited_stock, offer_with_two_criteria


class ListOffersTest:
    endpoint = "backoffice_v3_web.offer.list_offers"

    # Use assert_num_queries() instead of assert_no_duplicated_queries() which does not detect one extra query caused
    # by a field added in the jinja template.
    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch offers with joinedload including extra data (1 query)
    expected_num_queries = 3

    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.offer.list_offers"
        endpoint_kwargs = {"offerer_id": 1}
        needed_permission = perm_models.Permissions.MANAGE_OFFERS

    def test_list_offers_without_filter(self, authenticated_client, offers):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint))

        # then
        assert response.status_code == 200
        assert html_parser.count_table_rows(response.data) == 0

    @pytest.mark.parametrize(
        "where", [None, offer_forms.OfferSearchColumn.ALL.name, offer_forms.OfferSearchColumn.ID.name]
    )
    def test_list_offers_by_id(self, authenticated_client, offers, where):
        # when
        searched_id = str(offers[0].id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=searched_id, where=where))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == searched_id
        assert rows[0]["Nom de l'offre"] == offers[0].name
        assert rows[0]["Catégorie"] == offers[0].category.pro_label
        assert rows[0]["Sous-catégorie"] == offers[0].subcategory_v2.pro_label
        assert rows[0]["Stock initial"] == "Illimité"
        assert rows[0]["Stock restant"] == "Illimité"
        assert rows[0]["Tag"] == offers[0].criteria[0].name
        assert rows[0]["Pondération"] == ""
        assert rows[0]["État"] == "Validée"
        assert rows[0]["Dernière date de validation"] == ""
        assert rows[0]["Dép."] == offers[0].venue.departementCode
        assert rows[0]["Lieu"] == offers[0].venue.name

    @pytest.mark.parametrize(
        "where", [None, offer_forms.OfferSearchColumn.ALL.name, offer_forms.OfferSearchColumn.ID.name]
    )
    def test_list_offers_by_ids_list(self, authenticated_client, offers, where):
        # when
        searched_ids = f"{offers[0].id}, {offers[2].id}\n"
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=searched_ids, where=where))

            # then
            assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        assert set(int(row["ID"]) for row in rows) == {offers[0].id, offers[2].id}

    def test_list_offers_by_invalid_id(self, authenticated_client, offers):
        # when
        response = authenticated_client.get(
            url_for(self.endpoint, q="Cinéma", where=offer_forms.OfferSearchColumn.ID.name)
        )

        # then
        assert response.status_code == 400
        assert "La recherche ne correspond pas à un ID ou une liste d'ID" in html_parser.extract_warnings(response.data)

    @pytest.mark.parametrize(
        "where", [None, offer_forms.OfferSearchColumn.ALL.name, offer_forms.OfferSearchColumn.NAME.name]
    )
    def test_list_offers_by_name(self, authenticated_client, offers, where):
        # when
        searched_name = offers[1].name
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=searched_name, where=where))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        assert rows[0]["ID"] == str(offers[1].id)
        assert rows[0]["Nom de l'offre"] == offers[1].name
        assert rows[0]["Catégorie"] == offers[1].category.pro_label
        assert rows[0]["Sous-catégorie"] == offers[1].subcategory_v2.pro_label
        assert rows[0]["Stock initial"] == "20"
        assert rows[0]["Stock restant"] == "15"
        assert rows[0]["Tag"] == ""
        assert rows[0]["Pondération"] == ""
        assert rows[0]["État"] == "Validée"
        assert rows[0]["Dernière date de validation"] == "22/02/2022"
        assert rows[0]["Dép."] == offers[1].venue.departementCode
        assert rows[0]["Lieu"] == offers[1].venue.name

    @pytest.mark.parametrize(
        "isbn, where",
        [
            ("9781234567890", None),
            (" 978-1234567890", offer_forms.OfferSearchColumn.ALL.name),
            ("978 1234567890\t", offer_forms.OfferSearchColumn.ISBN.name),
        ],
    )
    def test_list_offers_by_isbn(self, authenticated_client, offers, isbn, where):
        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=isbn, where=where))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert int(rows[0]["ID"]) == offers[2].id

    def test_list_offers_by_invalid_isbn(self, authenticated_client, offers):
        # when
        response = authenticated_client.get(
            url_for(self.endpoint, q="1234567890", where=offer_forms.OfferSearchColumn.ISBN.name)
        )

        # then
        assert response.status_code == 400
        assert "La recherche ne correspond pas au format d'un ISBN" in html_parser.extract_warnings(response.data)

    @pytest.mark.parametrize(
        "visa, where",
        [
            ("2023123456", None),
            (" 2023 123456 ", offer_forms.OfferSearchColumn.ALL.name),
            ("2023-123456\t", offer_forms.OfferSearchColumn.VISA.name),
        ],
    )
    def test_list_offers_by_visa(self, authenticated_client, offers, visa, where):
        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=visa, where=where))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert int(rows[0]["ID"]) == offers[1].id

    def test_list_offers_by_invalid_visa(self, authenticated_client, offers):
        # when
        response = authenticated_client.get(
            url_for(self.endpoint, q="Visa n°12345", where=offer_forms.OfferSearchColumn.VISA.name)
        )

        # then
        assert response.status_code == 400
        assert "La recherche ne correspond pas au format d'un visa" in html_parser.extract_warnings(response.data)

    def test_list_offers_by_criteria(self, authenticated_client, criteria, offers):
        # when
        criterion_id = criteria[0].id
        with assert_num_queries(
            self.expected_num_queries + 1
        ):  # +1 because of reloading selected criterion in the form
            response = authenticated_client.get(url_for(self.endpoint, criteria=[criterion_id]))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[0].id, offers[2].id}

    def test_list_offers_by_category(self, authenticated_client, offers):
        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, category=[categories.LIVRE.id]))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[1].id, offers[2].id}

    def test_list_offers_by_department(self, authenticated_client, offers):
        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, department=["74", "47", "971"]))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[0].id, offers[2].id}

    def test_list_offers_by_venue(self, authenticated_client, offers):
        # when
        venue_id = offers[1].venueId
        with assert_num_queries(self.expected_num_queries + 1):  # +1 because of reloading selected venue in the form
            response = authenticated_client.get(url_for(self.endpoint, venue=[venue_id]))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[1].id}

    def test_list_offers_by_all_filters(self, authenticated_client, criteria, offers):
        # when
        criterion_id = criteria[1].id
        venue_id = offers[2].venueId
        with assert_num_queries(self.expected_num_queries + 2):  # +2 because of reloading selected criterion and venue
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    q="specific name",
                    criteria=[criterion_id],
                    category=[categories.LIVRE.id],
                    department=["74"],
                    venue=[venue_id],
                )
            )

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[2].id}


class EditOffersTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
        method = "post"
        endpoint = "backoffice_v3_web.offer.edit_offer"
        endpoint_kwargs = {"offer_id": 1}
        needed_permission = perm_models.Permissions.MANAGE_OFFERS

    def test_update_offer_tags(self, legit_user, authenticated_client, criteria):
        offer_to_edit = offers_factories.OfferFactory(
            name="A Very Specific Name That Is Longer",
            criteria=[criteria[0]],
            venue__postalCode="74000",
            venue__departementCode="74",
            product__subcategoryId=subcategories.LIVRE_PAPIER.id,
        )
        choosenRankingWeight = 22
        base_form = {"criteria": [criteria[0].id, criteria[1].id], "rankingWeight": choosenRankingWeight}

        response = self._update_offerer(authenticated_client, offer_to_edit, base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_v3_web.offer.list_offers", _external=True)
        assert response.location == expected_url

        offer_list_url = url_for("backoffice_v3_web.offer.list_offers", q=offer_to_edit.id, _external=True)
        response = authenticated_client.get(offer_list_url)

        assert response.status_code == 200
        row = html_parser.extract_table_rows(response.data)
        assert len(row) == 1
        assert row[0]["Pondération"] == str(choosenRankingWeight)
        assert criteria[0].name in row[0]["Tag"]
        assert criteria[1].name in row[0]["Tag"]
        assert criteria[2].name not in row[0]["Tag"]

        # New Update without rankingWeight
        base_form = {"criteria": [criteria[2].id, criteria[1].id], "rankingWeight": ""}
        response = self._update_offerer(authenticated_client, offer_to_edit, base_form)
        assert response.status_code == 303

        offer_list_url = url_for("backoffice_v3_web.offer.list_offers", q=offer_to_edit.id, _external=True)
        response = authenticated_client.get(offer_list_url)

        assert response.status_code == 200
        row = html_parser.extract_table_rows(response.data)
        assert len(row) == 1
        assert row[0]["Pondération"] == ""
        assert criteria[2].name in row[0]["Tag"]
        assert criteria[1].name in row[0]["Tag"]
        assert criteria[0].name not in row[0]["Tag"]
        assert criteria[3].name not in row[0]["Tag"]

    def _update_offerer(self, authenticated_client, offer, form):
        edit_url = url_for("backoffice_v3_web.offer.list_offers")
        authenticated_client.get(edit_url)

        url = url_for("backoffice_v3_web.offer.edit_offer", offer_id=offer.id)
        form["csrf_token"] = g.get("csrf_token", "")

        return authenticated_client.post(url, form=form)


class EditOfferFormTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
        method = "post"
        endpoint = "backoffice_v3_web.offer.get_edit_offer_form"
        endpoint_kwargs = {"offer_id": 1}
        needed_permission = perm_models.Permissions.MANAGE_OFFERS

    def test_get_edit_form_test(self, legit_user, authenticated_client):
        offer = offers_factories.OfferFactory()

        form_url = url_for("backoffice_v3_web.offer.get_edit_offer_form", offer_id=offer.id, _external=True)

        with assert_num_queries(3):  # session + user + tested_query
            response = authenticated_client.get(form_url)
            assert response.status_code == 200


class BatchEditOfferTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
        method = "post"
        endpoint = "backoffice_v3_web.offer.batch_edit_offer"
        endpoint_kwargs = {"offer_id": 1}
        needed_permission = perm_models.Permissions.MANAGE_OFFERS

    def test_batch_edit_offer(self, legit_user, authenticated_client, criteria):
        offers = offers_factories.OfferFactory.create_batch(10)
        parameter_ids = ",".join(str(offer.id) for offer in offers)
        choosenRankingWeight = 2
        base_form = {
            "criteria": [criteria[0].id, criteria[1].id],
            "rankingWeight": choosenRankingWeight,
            "object_ids": parameter_ids,
        }

        response = self._update_offers(authenticated_client, base_form)
        assert response.status_code == 303

        for offer in offers:
            assert offer.rankingWeight == choosenRankingWeight
            assert len(offer.criteria) == 2
            assert criteria[0] in offer.criteria
            assert criteria[2] not in offer.criteria

    def _update_offers(self, authenticated_client, form):
        edit_url = url_for("backoffice_v3_web.offer.list_offers")
        authenticated_client.get(edit_url)

        url = url_for("backoffice_v3_web.offer.batch_edit_offer")
        form["csrf_token"] = g.get("csrf_token", "")

        return authenticated_client.post(url, form=form)
