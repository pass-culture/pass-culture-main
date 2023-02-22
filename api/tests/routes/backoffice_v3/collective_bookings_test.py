import datetime

from flask import g
from flask import url_for
import pytest

from pcapi.core.categories import categories
from pcapi.core.categories import subcategories_v2
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import factories as offerers_factories
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import assert_num_queries
from pcapi.models import db

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
    # 4
    reimbursed = educational_factories.ReimbursedCollectiveBookingFactory(
        educationalInstitution=institution3,
        collectiveStock__collectiveOffer__subcategoryId=subcategories_v2.VISITE_GUIDEE.id,
        dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=5),
    )

    return pending, confirmed, cancelled, used, reimbursed


class ListCollectiveBookingsTest:
    endpoint = "backoffice_v3_web.collective_bookings.list_collective_bookings"

    # Use assert_num_queries() instead of assert_no_duplicated_queries() which does not detect one extra query caused
    # by a field added in the jinja template.
    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch collective bookings with extra data (1 query)
    expected_num_queries = 3

    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.collective_bookings.list_collective_bookings"
        endpoint_kwargs = {"offerer_id": 1}
        needed_permission = perm_models.Permissions.READ_BOOKINGS

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
        with assert_num_queries(self.expected_num_queries):
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
        search_query = str(collective_bookings[-1].id * 1000)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=search_query))

        # then
        assert response.status_code == 200
        assert html_parser.count_table_rows(response.data) == 0

    def test_list_bookings_by_offer_id(self, authenticated_client, collective_bookings):
        # when
        searched_id = str(collective_bookings[2].collectiveStock.collectiveOffer.id)
        with assert_num_queries(self.expected_num_queries):
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
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=search_query))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        # Warning: test may return more than 1 row when an offer id is the same as expected institution id
        assert len(rows) >= 1
        assert str(collective_bookings[1].id) in set(row["ID résa"] for row in rows)

    @pytest.mark.parametrize(
        "search_query, expected_idx",
        [
            ("Collège", (0, 1, 2)),
            ("Bref", (1,)),
            (
                "lycee charlemagne",
                (
                    3,
                    4,
                ),
            ),
        ],
    )
    def test_list_bookings_by_institution_name(
        self, authenticated_client, collective_bookings, search_query, expected_idx
    ):
        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=search_query))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(row["ID résa"] for row in rows) == {str(collective_bookings[idx].id) for idx in expected_idx}

    def test_list_bookings_by_category(self, authenticated_client, collective_bookings):
        # when
        with assert_num_queries(self.expected_num_queries):
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
            ([educational_models.CollectiveBookingStatus.REIMBURSED.name], (4,)),
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
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, status=status))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(row["ID résa"] for row in rows) == {str(collective_bookings[idx].id) for idx in expected_idx}

    def test_list_bookings_by_date(self, authenticated_client, collective_bookings):
        # when
        with assert_num_queries(self.expected_num_queries):
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
        with assert_num_queries(self.expected_num_queries + 1):
            response = authenticated_client.get(url_for(self.endpoint, offerer=offerer_ids))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID résa"]) for row in rows) == {collective_bookings[1].id, collective_bookings[3].id}

    def test_list_bookings_by_venue(self, authenticated_client, collective_bookings):
        # when
        venue_id = collective_bookings[0].venueId
        with assert_num_queries(self.expected_num_queries + 1):
            response = authenticated_client.get(url_for(self.endpoint, venue=venue_id))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID résa"]) for row in rows) == {collective_bookings[0].id, collective_bookings[2].id}

    def test_list_bookings_more_than_max(self, authenticated_client):
        # given
        educational_factories.CollectiveBookingFactory.create_batch(
            25, status=educational_models.CollectiveBookingStatus.CONFIRMED
        )

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, status=educational_models.CollectiveBookingStatus.CONFIRMED.name, limit=20)
            )

        # then
        assert response.status_code == 200
        assert html_parser.count_table_rows(response.data) == 20
        assert "Il y a plus de 20 résultats dans la base de données" in html_parser.extract_alert(response.data)


def send_request(authenticated_client, url, form_data=None):
    # generate and fetch (inside g) csrf token
    booking_list_url = url_for("backoffice_v3_web.collective_bookings.list_collective_bookings")
    authenticated_client.get(booking_list_url)

    form_data = form_data if form_data else {}
    form = {"csrf_token": g.get("csrf_token", ""), **form_data}

    return authenticated_client.post(url, form=form)


class MarkCollectiveBookingAsUsedTest:
    class MarkCollectiveBookingAsUsedUnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
        method = "post"
        endpoint = "backoffice_v3_web.collective_bookings.mark_booking_as_used"
        endpoint_kwargs = {"collective_booking_id": 1}
        needed_permission = perm_models.Permissions.MANAGE_BOOKINGS

    def test_uncancel_and_mark_as_used(self, authenticated_client, collective_bookings):
        # give
        cancelled = collective_bookings[2]

        # when
        url = url_for("backoffice_v3_web.collective_bookings.mark_booking_as_used", collective_booking_id=cancelled.id)
        response = send_request(authenticated_client, url)

        # then
        assert response.status_code == 303

        db.session.refresh(cancelled)
        assert cancelled.status is educational_models.CollectiveBookingStatus.CONFIRMED

        redirected_response = authenticated_client.get(response.headers["location"])
        assert f"La réservation {cancelled.id} a été validée" in html_parser.extract_alert(redirected_response.data)

    def test_uncancel_non_cancelled_booking(self, authenticated_client, collective_bookings):
        # give
        non_cancelled = collective_bookings[3]
        old_status = non_cancelled.status

        # when
        url = url_for(
            "backoffice_v3_web.collective_bookings.mark_booking_as_used", collective_booking_id=non_cancelled.id
        )
        response = send_request(authenticated_client, url)

        # then
        assert response.status_code == 303

        db.session.refresh(non_cancelled)
        assert non_cancelled.status == old_status

        redirected_response = authenticated_client.get(response.headers["location"])
        assert "Impossible de valider une réservation qui n'est pas annulée" in html_parser.extract_alert(
            redirected_response.data
        )


class CancelCollectiveBookingTest:
    class CancelCollectiveBookingUnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
        method = "post"
        endpoint = "backoffice_v3_web.collective_bookings.mark_booking_as_cancelled"
        endpoint_kwargs = {"collective_booking_id": 1}
        needed_permission = perm_models.Permissions.MANAGE_BOOKINGS

    def test_cancel_booking(self, authenticated_client, collective_bookings):
        # give
        confirmed = collective_bookings[1]

        # when
        url = url_for(
            "backoffice_v3_web.collective_bookings.mark_booking_as_cancelled", collective_booking_id=confirmed.id
        )
        response = send_request(authenticated_client, url)

        # then
        assert response.status_code == 303

        db.session.refresh(confirmed)
        assert confirmed.status is educational_models.CollectiveBookingStatus.CANCELLED

        redirected_response = authenticated_client.get(response.headers["location"])
        assert f"La réservation {confirmed.id} a été annulée" in html_parser.extract_alert(redirected_response.data)

    def test_cant_cancel_reimbursed_booking(self, authenticated_client, collective_bookings):
        # give
        reimbursed = collective_bookings[4]
        old_status = reimbursed.status

        # when
        url = url_for(
            "backoffice_v3_web.collective_bookings.mark_booking_as_cancelled", collective_booking_id=reimbursed.id
        )
        response = send_request(authenticated_client, url)
        print(response.data.decode("utf8"))
        # then
        assert response.status_code == 303

        db.session.refresh(reimbursed)
        assert reimbursed.status == old_status

        redirected_response = authenticated_client.get(response.headers["location"])
        assert "Impossible d'annuler une réservation remboursée" in html_parser.extract_alert(redirected_response.data)

    def test_cant_cancel_cancelled_booking(self, authenticated_client, collective_bookings):
        # give
        cancelled = collective_bookings[2]
        old_status = cancelled.status

        # when
        url = url_for(
            "backoffice_v3_web.collective_bookings.mark_booking_as_cancelled", collective_booking_id=cancelled.id
        )
        response = send_request(authenticated_client, url)

        # then
        assert response.status_code == 303

        db.session.refresh(cancelled)
        assert cancelled.status == old_status

        redirected_response = authenticated_client.get(response.headers["location"])
        print(html_parser.extract_alert(redirected_response.data))
        assert "Impossible d'annuler une réservation déjà annulée" in html_parser.extract_alert(
            redirected_response.data
        )
