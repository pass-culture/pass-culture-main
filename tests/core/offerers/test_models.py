from unittest.mock import patch

import pytest

from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.users import factories as users_factories


@pytest.mark.usefixtures("db_session")
class VenueTimezonePropertyTest:
    def test_europe_paris_is_default_timezone(self):
        venue = offers_factories.VenueFactory(postalCode="75000")

        assert venue.timezone == "Europe/Paris"

    def test_return_timezone_given_venue_departement_code(self):
        venue = offers_factories.VenueFactory(postalCode="97300")

        assert venue.timezone == "America/Cayenne"

    def test_return_managing_offerer_timezone_when_venue_is_virtual(self):
        venue = offers_factories.VirtualVenueFactory(managingOfferer__postalCode="97300")

        assert venue.timezone == "America/Cayenne"


@pytest.mark.usefixtures("db_session")
class VenueTimezoneSqlQueryTest:
    def test_europe_paris_is_default_timezone(self):
        offers_factories.VenueFactory(postalCode="75000")

        query_result = Venue.query.filter(Venue.timezone == "Europe/Paris").all()

        assert len(query_result) == 1

    def test_return_timezone_given_venue_departement_code(self):
        offers_factories.VenueFactory(postalCode="97300")

        query_result = Venue.query.filter(Venue.timezone == "America/Cayenne").all()

        assert len(query_result) == 1

    def test_return_managing_offerer_timezone_when_venue_is_virtual(self):
        offers_factories.VirtualVenueFactory(managingOfferer__postalCode="97300")

        query_result = Venue.query.filter(Venue.timezone == "America/Cayenne").all()

        assert len(query_result) == 1


@pytest.mark.usefixtures("db_session")
class OffererDepartementCodePropertyTest:
    def test_metropole_postal_code(self):
        offerer = offers_factories.OffererFactory(postalCode="75000")

        assert offerer.departementCode == "75"

    def test_drom_postal_code(self):
        offerer = offers_factories.OffererFactory(postalCode="97300")

        assert offerer.departementCode == "973"


@pytest.mark.usefixtures("db_session")
class OffererDepartementCodeSQLExpressionTest:
    def test_metropole_postal_code(self):
        offers_factories.OffererFactory(postalCode="75000")

        query_result = Offerer.query.filter(Offerer.departementCode == "75").all()

        assert len(query_result) == 1

    def test_drom_postal_code(self):
        offers_factories.OffererFactory(postalCode="97300")

        query_result = Offerer.query.filter(Offerer.departementCode == "973").all()

        assert len(query_result) == 1


@pytest.mark.usefixtures("db_session")
class OffererNValidatedOffersTest:
    def test_offerer_with_validated_offers(self):
        offerer = offers_factories.OffererFactory()
        offers_factories.OfferFactory.create_batch(
            size=2, validation=OfferValidationStatus.APPROVED, venue__managingOfferer=offerer
        )

        assert offerer.nApprovedOffers == 2

    def test_offerer_without_offer(self):
        offerer = offers_factories.OffererFactory()

        assert offerer.nApprovedOffers == 0

    def test_offerer_without_validated_offer(self):
        offerer = offers_factories.OffererFactory()
        offers_factories.OfferFactory(validation=OfferValidationStatus.DRAFT, venue__managingOfferer=offerer)
        offers_factories.OfferFactory(validation=OfferValidationStatus.REJECTED, venue__managingOfferer=offerer)
        offers_factories.OfferFactory(validation=OfferValidationStatus.PENDING, venue__managingOfferer=offerer)

        assert offerer.nApprovedOffers == 0


@pytest.mark.usefixtures("db_session")
class OffererLegalCategoryTest:
    @patch("pcapi.core.offerers.models.get_offerer_legal_category")
    def test_offerer_legal_category_called_many_times(self, mocked_get_offerer_legal_category):
        mocked_get_offerer_legal_category.return_value = {
            "legal_category_code": "5202",
            "legal_category_label": "Société en nom collectif",
        }
        offerer = offers_factories.OffererFactory()

        assert offerer.legal_category == "5202"
        assert offerer.legal_category == "5202"
        assert offerer.legal_category == "5202"
        assert mocked_get_offerer_legal_category.call_count == 1


@pytest.mark.usefixtures("db_session")
class OffererGrantAccessTest:
    def test_grant_access_to_offerer_to_given_pro(self):
        # Given
        offerer = offers_factories.OffererFactory()
        user = users_factories.ProFactory()

        # When
        created_user_offerer = offerer.grant_access(user)

        # Then
        assert created_user_offerer.user == user
        assert created_user_offerer.offerer == offerer

    def test_add_pro_role_to_user_if_he_does_not_possess_this_role(self):
        # Given
        offerer = offers_factories.OffererFactory()
        user = users_factories.UserFactory()

        # When
        created_user_offerer = offerer.grant_access(user)

        # Then
        assert created_user_offerer.user == user
        assert created_user_offerer.offerer == offerer
        assert user.has_pro_role

    def test_do_nothing_when_no_user_provided(self):
        # Given
        offerer = offers_factories.OffererFactory()

        # When
        created_user_offerer = offerer.grant_access(None)

        # Then
        assert created_user_offerer is None
