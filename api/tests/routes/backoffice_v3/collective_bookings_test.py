import datetime

from flask import url_for
import pytest

from pcapi.core.categories import categories
from pcapi.core.categories import subcategories_v2
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import factories as offerers_factories
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_no_duplicated_queries

from .helpers import html_parser
from .helpers import unauthorized as unauthorized_helpers


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


@pytest.fixture(scope="function", name="collective_bookings")
def collective_bookings_fixture() -> tuple:
    institution1 = educational_factories.EducationalInstitutionFactory(name="Collège Pépin le Bref")
    institution2 = educational_factories.EducationalInstitutionFactory(name="Collège Bertrade de Laon")
    institution3 = educational_factories.EducationalInstitutionFactory(name="Lycée Charlemagne")
    venue = offerers_factories.VenueFactory()  # same venue and offerer for 2 bookings
    # 0
    pending = educational_factories.PendingCollectiveBookingFactory(
        educationalInstitution=institution2,
        collectiveStock__collectiveOffer__subcategoryId=subcategories_v2.EVENEMENT_PATRIMOINE.id,
        dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=4),
        venue=venue,
    )
    # 1
    confirmed = educational_factories.CollectiveBookingFactory(
        educationalInstitution=institution1,
        collectiveStock__collectiveOffer__name="Visite des locaux primitifs du pass Culture",
        collectiveStock__collectiveOffer__subcategoryId=subcategories_v2.VISITE_GUIDEE.id,
        dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=3),
    )
    # 2
    cancelled = educational_factories.CancelledCollectiveBookingFactory(
        educationalInstitution=institution2,
        collectiveStock__collectiveOffer__subcategoryId=subcategories_v2.DECOUVERTE_METIERS.id,
        dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=2),
        venue=venue,
    )
    # 3
    used = educational_factories.UsedCollectiveBookingFactory(
        educationalInstitution=institution3,
        collectiveStock__collectiveOffer__subcategoryId=subcategories_v2.CONFERENCE.id,
        dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=1),
    )

    return pending, confirmed, cancelled, used


class ListCollectiveBookingsTest:
    endpoint = "backoffice_v3_web.collective_bookings.list_collective_bookings"

    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.collective_bookings.list_collective_bookings"
        endpoint_kwargs = {"offerer_id": 1}
        needed_permission = perm_models.Permissions.MANAGE_BOOKINGS

    def test_list_bookings_without_filter(self, authenticated_client, collective_bookings):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint))

        # then
        assert response.status_code == 200
        assert html_parser.count_table_rows(response.data) == 0

    def test_list_bookings_by_id(self, authenticated_client, collective_bookings):
        # when
        searched_id = str(collective_bookings[1].id)
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint, q=searched_id))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        # Warning: test may return more than 1 row when an offer id or institution id is the same as booking id
        assert len(rows) >= 1
        result = [row for row in rows if row["ID résa"] == searched_id][0]
        assert result["Établissement"].startswith("Collège Pépin le Bref")
        assert result["Nom de l'offre"] == "Visite des locaux primitifs du pass Culture"
        assert result["ID offre"].isdigit()
        assert result["Catégorie"] == categories.MUSEE.pro_label
        assert result["Sous-catégorie"] == subcategories_v2.VISITE_GUIDEE.pro_label
        assert result["Statut"] == "Confirmée"
        assert result["Date de réservation"] == (datetime.date.today() - datetime.timedelta(days=3)).strftime(
            "%d/%m/%Y"
        )
        assert result["Date de validation"] == (datetime.date.today() - datetime.timedelta(days=1)).strftime("%d/%m/%Y")
        assert not result["Date d'annulation"]

        assert html_parser.extract_pagination_info(response.data) == (1, 1, len(rows))

    def test_list_bookings_by_id_not_found(self, authenticated_client, collective_bookings):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint, q=str(collective_bookings[-1].id * 1000)))

        # then
        assert response.status_code == 200
        assert html_parser.count_table_rows(response.data) == 0

    def test_list_bookings_by_offer_id(self, authenticated_client, collective_bookings):
        # when
        searched_id = str(collective_bookings[2].collectiveStock.collectiveOffer.id)
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint, q=searched_id))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        # Warning: test may return more than 1 row when a booking id or institution id is the same as offer id
        assert len(rows) >= 1
        result = [row for row in rows if row["ID offre"] == searched_id][0]
        assert result["ID résa"] == str(collective_bookings[2].id)
        assert result["Établissement"].startswith("Collège Bertrade de Laon")
        assert result["Nom de l'offre"] == collective_bookings[2].collectiveStock.collectiveOffer.name
        assert result["Catégorie"] == categories.CONFERENCE_RENCONTRE.pro_label
        assert result["Sous-catégorie"] == subcategories_v2.DECOUVERTE_METIERS.pro_label
        assert result["Statut"] == "Annulée"
        assert result["Date de réservation"] == (datetime.date.today() - datetime.timedelta(days=2)).strftime(
            "%d/%m/%Y"
        )
        assert result["Date d'annulation"] == datetime.date.today().strftime("%d/%m/%Y")

        assert html_parser.extract_pagination_info(response.data) == (1, 1, len(rows))

    def test_list_bookings_by_institution_id(self, authenticated_client, collective_bookings):
        # when
        search_query = str(collective_bookings[1].educationalInstitution.id)
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint, q=search_query))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        # Warning: test may return more than 1 row when an offer id is the same as expected institution id
        assert len(rows) >= 1
        assert str(collective_bookings[1].id) in set(row["ID résa"] for row in rows)

    @pytest.mark.parametrize(
        "search_query, expected_idx", [("Collège", (0, 1, 2)), ("Bref", (1,)), ("lycee charlemagne", (3,))]
    )
    def test_list_bookings_by_institution_name(
        self, authenticated_client, collective_bookings, search_query, expected_idx
    ):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint, q=search_query))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(row["ID résa"] for row in rows) == {str(collective_bookings[idx].id) for idx in expected_idx}

    def test_list_bookings_by_category(self, authenticated_client, collective_bookings):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint, category=categories.CONFERENCE_RENCONTRE.id))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID résa"]) for row in rows) == {collective_bookings[2].id, collective_bookings[3].id}

    @pytest.mark.parametrize(
        "status, expected_idx",
        [
            ([educational_models.CollectiveBookingStatus.PENDING.name], (0,)),
            ([educational_models.CollectiveBookingStatus.CONFIRMED.name], (1,)),
            ([educational_models.CollectiveBookingStatus.CANCELLED.name], (2,)),
            ([educational_models.CollectiveBookingStatus.USED.name], (3,)),
            ([educational_models.CollectiveBookingStatus.REIMBURSED.name], ()),
            (
                [
                    educational_models.CollectiveBookingStatus.CONFIRMED.name,
                    educational_models.CollectiveBookingStatus.USED.name,
                ],
                (1, 3),
            ),
        ],
    )
    def test_list_bookings_by_status(self, authenticated_client, collective_bookings, status, expected_idx):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint, status=status))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(row["ID résa"] for row in rows) == {str(collective_bookings[idx].id) for idx in expected_idx}

    def test_list_bookings_by_date(self, authenticated_client, collective_bookings):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    from_date=(datetime.date.today() - datetime.timedelta(days=3)).isoformat(),
                    to_date=(datetime.date.today() - datetime.timedelta(days=2)).isoformat(),
                )
            )

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID résa"]) for row in rows) == {collective_bookings[1].id, collective_bookings[2].id}

    def test_list_bookings_by_offerer(self, authenticated_client, collective_bookings):
        # when
        offerer_ids = [collective_bookings[1].offererId, collective_bookings[3].offererId]
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint, offerer=offerer_ids))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID résa"]) for row in rows) == {collective_bookings[1].id, collective_bookings[3].id}

    def test_list_bookings_by_venue(self, authenticated_client, collective_bookings):
        # when
        venue_id = collective_bookings[0].venueId
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint, venue=venue_id))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID résa"]) for row in rows) == {collective_bookings[0].id, collective_bookings[2].id}
