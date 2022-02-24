import pytest

from pcapi.core.bookings.exceptions import CannotDeleteOffererWithBookingsException
import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import Booking
import pcapi.core.finance.factories as finance_factories
from pcapi.core.finance.models import BusinessUnit
from pcapi.core.offerers.factories import ApiKeyFactory
from pcapi.core.offerers.models import ApiKey
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Mediation
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.models import AllocineVenueProvider
from pcapi.core.providers.models import AllocineVenueProviderPriceRule
from pcapi.core.providers.models import Provider
from pcapi.core.providers.models import VenueProvider
import pcapi.core.users.factories as users_factories
from pcapi.core.users.models import Favorite
from pcapi.core.users.models import User
from pcapi.models.bank_information import BankInformation
from pcapi.models.criterion import Criterion
from pcapi.models.offer_criterion import OfferCriterion
from pcapi.models.product import Product
from pcapi.models.user_offerer import UserOfferer
from pcapi.scripts.offerer.delete_cascade_offerer_by_id import delete_cascade_offerer_by_id


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_abort_when_offerer_has_any_bookings():
    # Given
    offerer_to_delete = offers_factories.OffererFactory()
    offers_factories.OfferFactory(venue__managingOfferer=offerer_to_delete)
    bookings_factories.BookingFactory(stock__offer__venue__managingOfferer=offerer_to_delete)

    # When
    with pytest.raises(CannotDeleteOffererWithBookingsException) as exception:
        delete_cascade_offerer_by_id(offerer_to_delete.id)

    # Then
    assert exception.value.errors["cannotDeleteOffererWithBookingsException"] == [
        "Structure juridique non supprimable car elle contient des réservations"
    ]
    assert Offerer.query.count() == 1
    assert Venue.query.count() == 2
    assert Offer.query.count() == 2
    assert Stock.query.count() == 1
    assert Booking.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_remove_managed_venues_offers_and_stocks():
    # Given
    offerer_to_delete = offers_factories.OffererFactory()
    offers_factories.OfferFactory(venue__managingOfferer=offerer_to_delete)
    offers_factories.StockFactory(offer__venue__managingOfferer=offerer_to_delete)
    offers_factories.StockFactory()

    # When
    delete_cascade_offerer_by_id(offerer_to_delete.id)

    # Then
    assert Offerer.query.count() == 1
    assert Venue.query.count() == 1
    assert Offer.query.count() == 1
    assert Stock.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_remove_all_user_attachments_to_deleted_offerer():
    # Given
    pro = users_factories.ProFactory()
    offerer_to_delete = offers_factories.OffererFactory()
    offers_factories.UserOffererFactory(user=pro, offerer=offerer_to_delete)
    offers_factories.UserOffererFactory(user=pro)

    # When
    delete_cascade_offerer_by_id(offerer_to_delete.id)

    # Then
    assert Offerer.query.count() == 1
    assert UserOfferer.query.count() == 1
    assert User.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_remove_api_key_of_offerer():
    # Given
    offerer_to_delete = offers_factories.OffererFactory()
    ApiKeyFactory(offerer=offerer_to_delete)
    ApiKeyFactory(prefix="other-prefix")

    # When
    delete_cascade_offerer_by_id(offerer_to_delete.id)

    # Then
    assert Offerer.query.count() == 1
    assert ApiKey.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_remove_products_owned_by_offerer():
    # Given
    offerer_to_delete = offers_factories.OffererFactory()
    offers_factories.ProductFactory(owningOfferer=offerer_to_delete)
    offers_factories.ProductFactory()

    # When
    delete_cascade_offerer_by_id(offerer_to_delete.id)

    # Then
    assert Offerer.query.count() == 0
    assert Product.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_remove_bank_informations_of_offerer():
    # Given
    offerer_to_delete = offers_factories.OffererFactory()
    offers_factories.BankInformationFactory(offerer=offerer_to_delete)
    offers_factories.BankInformationFactory()

    # When
    delete_cascade_offerer_by_id(offerer_to_delete.id)

    # Then
    assert Offerer.query.count() == 0
    assert BankInformation.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_remove_offers_of_offerer():
    # Given
    offerer_to_delete = offers_factories.OffererFactory()
    venue = offers_factories.VenueFactory(managingOfferer=offerer_to_delete)
    event_offer = offers_factories.EventOfferFactory(venue=venue)
    thing_offer = offers_factories.ThingOfferFactory(venue=venue)
    items_to_delete = [event_offer.id, thing_offer.id]

    # When
    recap_data = delete_cascade_offerer_by_id(offerer_to_delete.id)

    # Then
    assert Offerer.query.count() == 0
    assert Offer.query.count() == 0
    assert sorted(recap_data["offer_ids_to_unindex"]) == sorted(items_to_delete)


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_remove_business_unit_of_managed_venue():
    # Given
    venue = offers_factories.VenueFactory()
    assert BusinessUnit.query.count() == 1
    offerer_to_delete = venue.managingOfferer
    finance_factories.BusinessUnitFactory()
    assert BusinessUnit.query.count() == 2

    # When
    delete_cascade_offerer_by_id(offerer_to_delete.id)

    # Then
    assert Offerer.query.count() == 0
    assert BusinessUnit.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_remove_bank_informations_of_managed_venue():
    # Given
    venue = offers_factories.VenueFactory()
    offerer_to_delete = venue.managingOfferer
    offers_factories.BankInformationFactory()
    assert BankInformation.query.count() == 2

    # When
    delete_cascade_offerer_by_id(offerer_to_delete.id)

    # Then
    assert Offerer.query.count() == 0
    assert Venue.query.count() == 0
    assert BankInformation.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_remove_mediations_of_managed_offers():
    # Given
    offerer_to_delete = offers_factories.OffererFactory()
    offers_factories.MediationFactory(offer__venue__managingOfferer=offerer_to_delete)
    offers_factories.MediationFactory()

    # When
    delete_cascade_offerer_by_id(offerer_to_delete.id)

    # Then
    assert Offerer.query.count() == 1
    assert Venue.query.count() == 1
    assert Offer.query.count() == 1
    assert Mediation.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_remove_favorites_of_managed_offers():
    # Given
    offerer_to_delete = offers_factories.OffererFactory()
    users_factories.FavoriteFactory(offer__venue__managingOfferer=offerer_to_delete)
    users_factories.FavoriteFactory()

    # When
    delete_cascade_offerer_by_id(offerer_to_delete.id)

    # Then
    assert Offerer.query.count() == 1
    assert Venue.query.count() == 1
    assert Offer.query.count() == 1
    assert Favorite.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_remove_criterion_attachment_of_managed_offers():
    # Given
    offerer_to_delete = offers_factories.OffererFactory()
    offers_factories.OfferCriterionFactory(offer__venue__managingOfferer=offerer_to_delete)
    offers_factories.OfferCriterionFactory()

    # When
    delete_cascade_offerer_by_id(offerer_to_delete.id)

    # Then
    assert Offerer.query.count() == 1
    assert Venue.query.count() == 1
    assert Offer.query.count() == 1
    assert OfferCriterion.query.count() == 1
    assert Criterion.query.count() == 2


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_remove_venue_synchronization_to_provider():
    # Given
    offerer_to_delete = offers_factories.OffererFactory()
    providers_factories.VenueProviderFactory(venue__managingOfferer=offerer_to_delete)
    providers_factories.VenueProviderFactory()

    # When
    delete_cascade_offerer_by_id(offerer_to_delete.id)

    # Then
    assert Offerer.query.count() == 1
    assert Venue.query.count() == 1
    assert VenueProvider.query.count() == 1
    assert Provider.query.count() > 0


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_remove_venue_synchronization_to_allocine_provider():
    # Given
    offerer_to_delete = offers_factories.OffererFactory()
    providers_factories.AllocineVenueProviderPriceRuleFactory(
        allocineVenueProvider__venue__managingOfferer=offerer_to_delete
    )
    providers_factories.AllocineVenueProviderPriceRuleFactory()

    # When
    delete_cascade_offerer_by_id(offerer_to_delete.id)

    # Then
    assert Offerer.query.count() == 1
    assert Venue.query.count() == 1
    assert VenueProvider.query.count() == 1
    assert AllocineVenueProvider.query.count() == 1
    assert AllocineVenueProviderPriceRule.query.count() == 1
    assert Provider.query.count() > 0
