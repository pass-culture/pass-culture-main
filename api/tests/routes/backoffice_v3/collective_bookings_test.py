import datetime

from flask import url_for
import pytest

from pcapi.core.categories import subcategories_v2
from pcapi.core.educational import factories as educational_factories
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
    institution = educational_factories.EducationalInstitutionFactory(name="Collège Pépin le Bref")
    pending = educational_factories.PendingCollectiveBookingFactory()
    confirmed = educational_factories.CollectiveBookingFactory(
        educationalInstitution=institution,
        collectiveStock__collectiveOffer__name="Visite des locaux primitifs du pass Culture",
        collectiveStock__collectiveOffer__subcategoryId=subcategories_v2.VISITE_GUIDEE.id,
    )
    cancelled = educational_factories.CancelledCollectiveBookingFactory()
    used = educational_factories.UsedCollectiveBookingFactory()

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
        assert len(rows) == 1
        assert rows[0]["ID résa"] == searched_id
        assert rows[0]["Établissement"].startswith("Collège Pépin le Bref")
        assert rows[0]["Nom de l'offre"] == "Visite des locaux primitifs du pass Culture"
        assert rows[0]["ID offre"].isdigit()
        assert rows[0]["Catégorie"] == "Musée, patrimoine, architecture, arts visuels"
        assert rows[0]["Sous-catégorie"] == "Visite guidée"
        assert rows[0]["Statut"] == "Confirmée"
        assert rows[0]["Date de validation"] == (datetime.date.today() - datetime.timedelta(days=1)).strftime(
            "%d/%m/%Y"
        )
        assert not rows[0]["Date d'annulation"]

        assert html_parser.extract_pagination_info(response.data) == (1, 1, 1)

    def test_list_bookings_by_invalid_id(self, authenticated_client, collective_bookings):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint, q="AB"))

        # then
        assert response.status_code == 400
        assert html_parser.extract_warnings(response.data) == ["Le format de l'ID de réservation est incorrect"]
        assert html_parser.count_table_rows(response.data) == 0

    def test_list_bookings_by_token_not_found(self, authenticated_client, collective_bookings):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint, q=str(collective_bookings[-1].id + 1)))

        # then
        assert response.status_code == 200
        assert html_parser.count_table_rows(response.data) == 0
