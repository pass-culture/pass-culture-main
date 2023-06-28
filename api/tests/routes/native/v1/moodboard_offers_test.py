import pytest

from pcapi import settings
from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.categories import subcategories
from pcapi.core.categories import subcategories_v2
import pcapi.core.mails.testing as mails_testing
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import OfferReport
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.core.users.factories import UserFactory
import pcapi.local_providers.cinema_providers.constants as cinema_providers_constants
from pcapi.models.offer_mixin import OfferValidationStatus
import pcapi.notifications.push.testing as notifications_testing
from pcapi.routes.native.v1.serialization import moodboard_offers as serializers

from tests.conftest import TestClient
from tests.connectors.cgr import soap_definitions
from tests.local_providers.cinema_providers.boost import fixtures as boost_fixtures
from tests.local_providers.cinema_providers.cgr import fixtures as cgr_fixtures

from .utils import create_user_and_test_client


pytestmark = pytest.mark.usefixtures("db_session")


class GetMoodboardOffersTest:
    def test_get_moodboard_offers(self, app):
        response = TestClient(app.test_client()).post(f"/native/v1/moodboard_offers", {
            "temporality": serializers.Temporality.TODAY.value,
            "mood": serializers.Mood.FESTIVE.value,
            "theme": serializers.Theme.SUMMER_VIBE.value
        })

        assert response.status_code == 200
