import datetime
from operator import itemgetter
from unittest.mock import patch

from flask import g
from flask import url_for
import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import categories
from pcapi.core.categories import subcategories
from pcapi.core.criteria import factories as criteria_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import assert_num_queries
import pcapi.core.users.factories as users_factories
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.routes.backoffice_v3.forms import offer as offer_forms

from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


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
        dateCreated=datetime.date.today() - datetime.timedelta(days=2),
        validation=offers_models.OfferValidationStatus.REJECTED,
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


class ListOffersTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.offer.list_offers"
    needed_permission = perm_models.Permissions.READ_OFFERS

    # Use assert_num_queries() instead of assert_no_duplicated_queries() which does not detect one extra query caused
    # by a field added in the jinja template.
    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch offers with joinedload including extra data (1 query)
    expected_num_queries = 3

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
        assert rows[0]["Stock restant"] == "Illimité / Illimité"
        assert rows[0]["Tag"] == offers[0].criteria[0].name
        assert rows[0]["Pond."] == ""
        assert rows[0]["État"] == "Validée"
        assert rows[0]["Date de création"] == (datetime.date.today()).strftime("%d/%m/%Y")
        assert rows[0]["Dernière validation"] == ""
        assert rows[0]["Dép."] == offers[0].venue.departementCode
        assert rows[0]["Structure"] == offers[0].venue.managingOfferer.name
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
        rows = sorted(rows, key=itemgetter("ID"))  # ensure deterministic order
        assert rows[0]["ID"] == str(offers[1].id)
        assert rows[0]["Nom de l'offre"] == offers[1].name
        assert rows[0]["Catégorie"] == offers[1].category.pro_label
        assert rows[0]["Sous-catégorie"] == offers[1].subcategory_v2.pro_label
        assert rows[0]["Stock restant"] == "15 / 20"
        assert rows[0]["Tag"] == ""
        assert rows[0]["Pond."] == ""
        assert rows[0]["État"] == "Validée"
        assert rows[0]["Date de création"] == (datetime.date.today()).strftime("%d/%m/%Y")
        assert rows[0]["Dernière validation"] == "22/02/2022"
        assert rows[0]["Dép."] == offers[1].venue.departementCode
        assert rows[0]["Structure"] == offers[1].venue.managingOfferer.name
        assert rows[0]["Lieu"] == offers[1].venue.name
        assert rows[1]["ID"] == str(offers[2].id)
        assert rows[1]["Nom de l'offre"] == offers[2].name

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

    def test_list_offers_by_date(self, authenticated_client, offers):
        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    from_date=(datetime.date.today() - datetime.timedelta(days=3)).isoformat(),
                    to_date=(datetime.date.today() - datetime.timedelta(days=1)).isoformat(),
                )
            )

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[2].id}

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

    def test_list_offers_by_offerer(self, authenticated_client, offers):
        # when
        offerer_id = offers[1].venue.managingOffererId
        with assert_num_queries(self.expected_num_queries + 1):  # +1 because of reloading selected offerer in the form
            response = authenticated_client.get(url_for(self.endpoint, offerer=[offerer_id]))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[1].id}

    def test_list_offers_by_status(self, authenticated_client, offers):
        # when
        status = offers[2].validation
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, status=[status.value]))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[2].id}
        assert rows[0]["État"] == "Rejetée"

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

    @pytest.mark.parametrize(
        "order,expected_list",
        [
            ("", ["Offre 4", "Offre 3", "Offre 2", "Offre 1"]),
            ("asc", ["Offre 4", "Offre 3", "Offre 2", "Offre 1"]),
            ("desc", ["Offre 1", "Offre 2", "Offre 3", "Offre 4"]),
        ],
    )
    def test_list_offers_pending_from_validated_offerers_sorted_by_date(
        self, authenticated_client, order, expected_list
    ):
        # test results when clicking on pending offers link (home page)
        # given
        offers_factories.OfferFactory(
            validation=offers_models.OfferValidationStatus.PENDING,
            venue__managingOfferer=offerers_factories.NotValidatedOffererFactory(),
        )

        validated_venue = offerers_factories.VenueFactory()
        for days_ago in (2, 4, 1, 3):
            offers_factories.OfferFactory(
                name=f"Offre {days_ago}",
                dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=days_ago),
                validation=offers_models.OfferValidationStatus.PENDING,
                venue=validated_venue,
            )

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    status=[offers_models.OfferValidationStatus.PENDING.value],
                    only_validated_offerers="on",
                    sort="dateCreated",
                    order=order,
                )
            )
            assert response.status_code == 200

        # then: must be sorted, older first
        rows = html_parser.extract_table_rows(response.data)
        assert [row["Nom de l'offre"] for row in rows] == expected_list


class EditOfferTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.offer.edit_offer"
    endpoint_kwargs = {"offer_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_OFFERS

    @patch("pcapi.core.search.reindex_offer_ids")
    def test_update_offer_tags(self, mock_reindex_offer_ids, legit_user, authenticated_client, criteria):
        offer_to_edit = offers_factories.OfferFactory(
            name="A Very Specific Name That Is Longer",
            criteria=[criteria[0]],
            venue__postalCode="74000",
            venue__departementCode="74",
            product__subcategoryId=subcategories.LIVRE_PAPIER.id,
        )
        choosen_ranking_weight = 22
        base_form = {"criteria": [criteria[0].id, criteria[1].id], "rankingWeight": choosen_ranking_weight}

        response = self.post_to_endpoint(authenticated_client, offer_id=offer_to_edit.id, form=base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_v3_web.offer.list_offers", _external=True)
        assert response.location == expected_url

        offer_list_url = url_for("backoffice_v3_web.offer.list_offers", q=offer_to_edit.id, _external=True)
        response = authenticated_client.get(offer_list_url)

        assert response.status_code == 200
        row = html_parser.extract_table_rows(response.data)
        assert len(row) == 1
        assert row[0]["Pond."] == str(choosen_ranking_weight)
        assert criteria[0].name in row[0]["Tag"]
        assert criteria[1].name in row[0]["Tag"]
        assert criteria[2].name not in row[0]["Tag"]

        # offer should be reindexed
        mock_reindex_offer_ids.assert_called_once_with([offer_to_edit.id])
        mock_reindex_offer_ids.reset_mock()

        # New Update without rankingWeight
        base_form = {"criteria": [criteria[2].id, criteria[1].id], "rankingWeight": ""}
        response = self.post_to_endpoint(authenticated_client, offer_id=offer_to_edit.id, form=base_form)
        assert response.status_code == 303

        offer_list_url = url_for("backoffice_v3_web.offer.list_offers", q=offer_to_edit.id, _external=True)
        response = authenticated_client.get(offer_list_url)

        assert response.status_code == 200
        row = html_parser.extract_table_rows(response.data)
        assert len(row) == 1
        assert row[0]["Pond."] == ""
        assert criteria[2].name in row[0]["Tag"]
        assert criteria[1].name in row[0]["Tag"]
        assert criteria[0].name not in row[0]["Tag"]
        assert criteria[3].name not in row[0]["Tag"]

        # offer should be reindexed
        mock_reindex_offer_ids.assert_called_once_with([offer_to_edit.id])


class GetEditOfferFormTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.offer.get_edit_offer_form"
    endpoint_kwargs = {"offer_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_OFFERS

    def test_get_edit_form_test(self, legit_user, authenticated_client):
        offer = offers_factories.OfferFactory()

        form_url = url_for(self.endpoint, offer_id=offer.id)

        with assert_num_queries(3):  # session + user + tested_query
            response = authenticated_client.get(form_url)
            assert response.status_code == 200


class GetBatchEditOfferFormTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.offer.get_batch_edit_offer_form"
    endpoint_kwargs = {"offer_ids": "1,2"}
    needed_permission = perm_models.Permissions.MANAGE_OFFERS

    def test_get_empty_edit_form_test(self, legit_user, authenticated_client):
        form_url = url_for(self.endpoint, _external=True)

        with assert_num_queries(2):  # session + user
            response = authenticated_client.get(form_url)
            assert response.status_code == 200

    def test_get_edit_form_with_values_test(self, legit_user, authenticated_client, criteria):
        offers = offers_factories.OfferFactory.create_batch(
            3, product__subcategoryId=subcategories.LIVRE_PAPIER.id, criteria=[criteria[2]], rankingWeight=22
        )
        selected_offers = offers[:-1]  # select all but the last offer

        offer_ids = ",".join(str(offer.id) for offer in selected_offers)
        base_form = {
            "object_ids": offer_ids,
            "criteria": [criteria[2].id],
            "rankingWeight": "0",
        }  # as it is already get in the modal form

        response = self._update_offers_form(authenticated_client, base_form)
        assert response.status_code == 200

        # Edit N°1 - The two first offers
        base_form["criteria"].extend([criteria[0].id, criteria[1].id])
        response = self._update_offers(authenticated_client, base_form)
        assert response.status_code == 303
        for offer in offers[:-1]:
            assert set(offer.criteria) == set(criteria[:3])
            assert offer.rankingWeight is None

        # Edit N°2 - Only the last offer
        choosen_ranking_weight = 12
        base_form = {
            "criteria": [criteria[2].id, criteria[3].id],
            "rankingWeight": choosen_ranking_weight,
        }  # new set of criteria
        response = self._update_offer(authenticated_client, offers[-1], base_form)
        assert response.status_code == 303

        assert offers[0].rankingWeight is None
        assert offers[1].rankingWeight is None
        assert offers[2].rankingWeight == choosen_ranking_weight

        assert set(offers[0].criteria) == set(criteria[:3])
        assert set(offers[1].criteria) == set(criteria[:3])
        assert set(offers[2].criteria) == set(criteria[2:])

    def _update_offers_form(self, authenticated_client, form):
        edit_url = url_for("backoffice_v3_web.offer.list_offers")
        authenticated_client.get(edit_url)

        url = url_for(self.endpoint)
        form["csrf_token"] = g.get("csrf_token", "")

        return authenticated_client.post(url, form=form)

    def _update_offers(self, authenticated_client, form):
        url = url_for("backoffice_v3_web.offer.batch_edit_offer")
        form["csrf_token"] = g.get("csrf_token", "")

        return authenticated_client.post(url, form=form)

    def _update_offer(self, authenticated_client, offer, form):
        url = url_for("backoffice_v3_web.offer.edit_offer", offer_id=offer.id)
        form["csrf_token"] = g.get("csrf_token", "")

        return authenticated_client.post(url, form=form)


class BatchEditOfferTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.offer.batch_edit_offer"
    endpoint_kwargs = {"offer_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_OFFERS

    @patch("pcapi.core.search.async_index_offer_ids")
    def test_batch_edit_offer(self, mock_async_index, legit_user, authenticated_client, criteria):
        offers = offers_factories.OfferFactory.create_batch(3)
        parameter_ids = ",".join(str(offer.id) for offer in offers)
        chosen_ranking_weight = 2
        base_form = {
            "criteria": [criteria[0].id, criteria[1].id],
            "rankingWeight": chosen_ranking_weight,
            "object_ids": parameter_ids,
        }

        response = self.post_to_endpoint(authenticated_client, form=base_form)
        assert response.status_code == 303

        for offer in offers:
            assert offer.rankingWeight == chosen_ranking_weight
            assert len(offer.criteria) == 2
            assert criteria[0] in offer.criteria
            assert criteria[2] not in offer.criteria

        mock_async_index.assert_called_once_with([offer.id for offer in offers])


class ValidateOfferTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.offer.validate_offer"
    endpoint_kwargs = {"offer_id": 1}
    needed_permission = perm_models.Permissions.FRAUD_ACTIONS

    def test_validate_offer(self, legit_user, authenticated_client):
        offer_to_validate = offers_factories.OfferFactory(validation=offers_models.OfferValidationStatus.REJECTED)

        response = self.post_to_endpoint(authenticated_client, offer_id=offer_to_validate.id)
        assert response.status_code == 303

        expected_url = url_for("backoffice_v3_web.offer.list_offers", _external=True)
        assert response.location == expected_url

        offer_list_url = url_for("backoffice_v3_web.offer.list_offers", q=offer_to_validate.id, _external=True)
        response = authenticated_client.get(offer_list_url)

        assert response.status_code == 200
        row = html_parser.extract_table_rows(response.data)
        assert len(row) == 1
        assert row[0]["État"] == "Validée"
        assert row[0]["Dernière validation"] == (datetime.date.today()).strftime("%d/%m/%Y")

        assert offer_to_validate.isActive is True
        assert offer_to_validate.lastValidationType == OfferValidationType.MANUAL


class GetValidateOfferFormTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.offer.get_validate_offer_form"
    endpoint_kwargs = {"offer_id": 1}
    needed_permission = perm_models.Permissions.FRAUD_ACTIONS

    def test_get_validate_form_test(self, legit_user, authenticated_client):
        offer = offers_factories.OfferFactory()

        form_url = url_for(self.endpoint, offer_id=offer.id)

        with assert_num_queries(3):  # session + user + tested_query
            response = authenticated_client.get(form_url)
            assert response.status_code == 200


class RejectOfferTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.offer.reject_offer"
    endpoint_kwargs = {"offer_id": 1}
    needed_permission = perm_models.Permissions.FRAUD_ACTIONS

    def test_reject_offer(self, legit_user, authenticated_client):
        offer_to_reject = offers_factories.OfferFactory(validation=offers_models.OfferValidationStatus.APPROVED)

        response = self.post_to_endpoint(authenticated_client, offer_id=offer_to_reject.id)
        assert response.status_code == 303

        expected_url = url_for("backoffice_v3_web.offer.list_offers", _external=True)
        assert response.location == expected_url

        offer_list_url = url_for("backoffice_v3_web.offer.list_offers", q=offer_to_reject.id, _external=True)
        response = authenticated_client.get(offer_list_url)

        assert response.status_code == 200
        row = html_parser.extract_table_rows(response.data)
        assert len(row) == 1
        assert row[0]["État"] == "Rejetée"
        assert row[0]["Dernière validation"] == (datetime.date.today()).strftime("%d/%m/%Y")

        assert offer_to_reject.isActive is False
        assert offer_to_reject.lastValidationType == OfferValidationType.MANUAL


class GetRejectOfferFormTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.offer.get_reject_offer_form"
    endpoint_kwargs = {"offer_id": 1}
    needed_permission = perm_models.Permissions.FRAUD_ACTIONS

    def test_get_edit_form_test(self, legit_user, authenticated_client):
        offer = offers_factories.OfferFactory()

        form_url = url_for(self.endpoint, offer_id=offer.id, _external=True)

        with assert_num_queries(3):  # session + user + tested_query
            response = authenticated_client.get(form_url)
            assert response.status_code == 200


class BatchOfferValidateTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.offer.batch_validate_offers"
    needed_permission = perm_models.Permissions.FRAUD_ACTIONS

    def test_batch_validate_offers(self, legit_user, authenticated_client):
        offers = offers_factories.OfferFactory.create_batch(3, validation=offers_models.OfferValidationStatus.DRAFT)
        parameter_ids = ",".join(str(offer.id) for offer in offers)
        response = self.post_to_endpoint(authenticated_client, form={"object_ids": parameter_ids})

        assert response.status_code == 303
        for offer in offers:
            db.session.refresh(offer)
            assert offer.lastValidationDate.strftime("%d/%m/%Y") == datetime.date.today().strftime("%d/%m/%Y")
            assert offer.isActive is True
            assert offer.lastValidationType is OfferValidationType.MANUAL
            assert offer.validation is offers_models.OfferValidationStatus.APPROVED


class BatchOfferRejectTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.offer.batch_reject_offers"
    needed_permission = perm_models.Permissions.FRAUD_ACTIONS

    def test_batch_reject_offers(self, legit_user, authenticated_client):
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        offers = offers_factories.OfferFactory.create_batch(3, validation=offers_models.OfferValidationStatus.DRAFT)
        confirmed_booking = bookings_factories.BookingFactory(
            user=beneficiary, stock__offer=offers[0], status=BookingStatus.CONFIRMED
        )
        parameter_ids = ",".join(str(offer.id) for offer in offers)

        assert confirmed_booking.status == BookingStatus.CONFIRMED

        response = self.post_to_endpoint(authenticated_client, form={"object_ids": parameter_ids})

        assert confirmed_booking.status == BookingStatus.CANCELLED
        assert response.status_code == 303
        for offer in offers:
            db.session.refresh(offer)
            assert offer.lastValidationDate.strftime("%d/%m/%Y") == datetime.date.today().strftime("%d/%m/%Y")
            assert offer.isActive is False
            assert offer.lastValidationType is OfferValidationType.MANUAL
            assert offer.validation is offers_models.OfferValidationStatus.REJECTED
