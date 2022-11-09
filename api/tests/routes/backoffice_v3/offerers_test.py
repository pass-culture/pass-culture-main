from flask import url_for
import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerers_models
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features

from .helpers import unauthorized as unauthorized_helpers


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(scope="function", name="offerer")
def offerer_fixture():  # type: ignore
    offerer = offerers_factories.OffererFactory(
        postalCode="46150", validationStatus=offerers_models.ValidationStatus.VALIDATED
    )
    return offerer


@pytest.fixture(scope="function", name="venue_with_accepted_bank_info")
def venue_with_accepted_bank_info_fixture(offerer):  # type: ignore
    venue = offerers_factories.VenueFactory(managingOfferer=offerer)
    finance_factories.BankInformationFactory(
        venue=venue,
        status=finance_models.BankInformationStatus.ACCEPTED,
    )
    return venue


@pytest.fixture(scope="function", name="offerer_active_individual_offer")
def offerer_active_individual_offer_fixture(venue_with_accepted_bank_info):  # type: ignore
    return offers_factories.OfferFactory(
        venue=venue_with_accepted_bank_info,
        isActive=True,
        validation=offers_models.OfferValidationStatus.APPROVED.value,
    )


@pytest.fixture(scope="function", name="individual_offerer_booking")
def individual_offerer_booking_fixture(offerer_active_individual_offer):  # type: ignore
    stock = offers_factories.StockFactory(offer=offerer_active_individual_offer)
    return bookings_factories.BookingFactory(
        status=bookings_models.BookingStatus.USED,
        quantity=1,
        amount=10,
        stock=stock,
    )


class GetOffererUnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
    endpoint = "backoffice_v3_web.offerer.get"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY


class GetOffererTest:
    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_get_offerer(self, authenticated_client):  # type: ignore
        offerer = offerers_factories.UserOffererFactory().offerer
        url = url_for("backoffice_v3_web.offerer.get", offerer_id=offerer.id)

        # get session (1 query)
        # get user with profile and permissions (1 query)
        # get FF (1 query)
        # get pro user/ offerer / venue (1 query)
        with assert_num_queries(4):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content = response.data.decode("utf-8")

        assert offerer.name in content
        assert str(offerer.id) in content
        assert offerer.siren in content
        assert "Structure" in content


class GetOffererStatsUnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
    endpoint = "backoffice_v3_web.offerer.get_offerer_stats"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY


class GetOffererStatsTest:
    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_get_stats(  # type: ignore
        self, authenticated_client, offerer, offerer_active_individual_offer, individual_offerer_booking
    ):
        url = url_for("backoffice_v3_web.offerer.get_offerer_stats", offerer_id=offerer.id)

        # get session (1 query)
        # get user with profile and permissions (1 query)
        # get FF (1 query)
        # get total revenue (1 query)
        # get offerers offers stats (1 query)
        with assert_num_queries(5):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content = response.data.decode("utf-8")

        # cast to integer to avoid errors due to amount formatting
        assert str(int(individual_offerer_booking.amount)) in content
        assert "1 IND" in content  # one active individual offer
