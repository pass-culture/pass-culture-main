import pytest

from pcapi.core.bookings.factories import BookingFactory
import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import override_features
import pcapi.core.users.factories as users_factories
from pcapi.scripts.payment.batch_steps import generate_new_payments

from tests.conftest import TestClient


class Get:
    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def when_user_has_an_offerer_attached(self, app):
            # Given
            offerer1 = offers_factories.OffererFactory()
            offerer2 = offers_factories.OffererFactory(siren="123456788")
            user = users_factories.UserFactory(email="user+plus@email.fr", offerers=[offerer1, offerer2])
            venue1 = offers_factories.VenueFactory(managingOfferer=offerer1)
            venue2 = offers_factories.VenueFactory(managingOfferer=offerer1, siret="12345678912346")
            venue3 = offers_factories.VenueFactory(managingOfferer=offerer1, siret="12345678912347")
            offers_factories.BankInformationFactory(applicationId=1, venue=venue1)
            offers_factories.BankInformationFactory(applicationId=7, venue=venue2)
            stock1 = offers_factories.ThingStockFactory(offer__venue=venue1, price=10)
            stock2 = offers_factories.ThingStockFactory(offer__venue=venue2, price=11)
            stock3 = offers_factories.ThingStockFactory(offer__venue=venue3, price=12)
            stock4 = offers_factories.ThingStockFactory(offer__venue=venue3, price=13)
            BookingFactory(user=user, stock=stock1, isUsed=True, token="ABCDEF")
            BookingFactory(user=user, stock=stock1, token="ABCDEG")
            BookingFactory(user=user, stock=stock2, isUsed=True, token="ABCDEH")
            BookingFactory(user=user, stock=stock3, isUsed=True, token="ABCDEI")
            BookingFactory(user=user, stock=stock4, isUsed=True, token="ABCDEJ")
            BookingFactory(user=user, stock=stock4, isUsed=True, token="ABCDEK")
            generate_new_payments()

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get("/reimbursements/csv")
            response_lines = response.data.decode("utf-8").split("\n")

            # Then
            assert response.status_code == 200
            assert response.headers["Content-type"] == "text/csv; charset=utf-8;"
            assert response.headers["Content-Disposition"] == "attachment; filename=remboursements_pass_culture.csv"
            assert len(response_lines) == 7

        @pytest.mark.usefixtures("db_session")
        def when_user_has_no_offerer_attached(self, app):
            # Given
            user = users_factories.UserFactory(email="user+plus@email.fr")

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get("/reimbursements/csv")
            response_lines = response.data.decode("utf-8").split("\n")

            # Then
            assert response.status_code == 200
            assert len(response_lines) == 2

        @override_features(DISABLE_BOOKINGS_RECAP_FOR_SOME_PROS=True)
        def when_user_has_blacklisted_offerer(self, app, db_session):
            # Given
            offerer1 = offers_factories.OffererFactory()
            offerer2 = offers_factories.OffererFactory(siren="343282380")
            user = users_factories.UserFactory(email="user+plus@email.fr", offerers=[offerer1, offerer2])
            venue1 = offers_factories.VenueFactory(managingOfferer=offerer1)
            venue2 = offers_factories.VenueFactory(managingOfferer=offerer1, siret="12345678912346")
            venue3 = offers_factories.VenueFactory(managingOfferer=offerer1, siret="12345678912347")
            offers_factories.BankInformationFactory(applicationId=1, venue=venue1)
            offers_factories.BankInformationFactory(applicationId=7, venue=venue2)
            stock1 = offers_factories.ThingStockFactory(offer__venue=venue1, price=10)
            stock2 = offers_factories.ThingStockFactory(offer__venue=venue2, price=11)
            stock3 = offers_factories.ThingStockFactory(offer__venue=venue3, price=12)
            stock4 = offers_factories.ThingStockFactory(offer__venue=venue3, price=13)
            BookingFactory(user=user, stock=stock1, isUsed=True, token="ABCDEF")
            BookingFactory(user=user, stock=stock1, token="ABCDEG")
            BookingFactory(user=user, stock=stock2, isUsed=True, token="ABCDEH")
            BookingFactory(user=user, stock=stock3, isUsed=True, token="ABCDEI")
            BookingFactory(user=user, stock=stock4, isUsed=True, token="ABCDEJ")
            BookingFactory(user=user, stock=stock4, isUsed=True, token="ABCDEK")
            generate_new_payments()

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get("/reimbursements/csv")
            response_lines = response.data.decode("utf-8").split("\n")

            # Then
            assert response.status_code == 200
            assert len(response_lines) == 2
