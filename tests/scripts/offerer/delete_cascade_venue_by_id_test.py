import pytest

from pcapi.core.bookings.exceptions import CannotDeleteVenueWithBookingsException
import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import Booking
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Mediation
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
import pcapi.core.users.factories as users_factories
from pcapi.core.users.models import Favorite
from pcapi.models import AllocineVenueProvider
from pcapi.models import AllocineVenueProviderPriceRule
from pcapi.models import BankInformation
from pcapi.models import Criterion
from pcapi.models import OfferCriterion
from pcapi.models import Provider
from pcapi.models import VenueProvider
from pcapi.scripts.offerer.delete_cascade_venue_by_id import delete_cascade_venue_by_id


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_venue_should_abort_when_offerer_has_any_bookings():
    # Given
    booking = bookings_factories.BookingFactory()
    venue_to_delete = booking.stock.offer.venue

    # When
    with pytest.raises(CannotDeleteVenueWithBookingsException) as exception:
        delete_cascade_venue_by_id(venue_to_delete.id)

    # Then
    assert exception.value.errors["cannotDeleteVenueWithBookingsException"] == [
        "Lieu non supprimable car il contient des réservations"
    ]
    assert Offerer.query.count() == 1
    assert Venue.query.count() == 1
    assert Stock.query.count() == 1
    assert Booking.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_venue_should_remove_offers_and_stocks():
    # Given
    venue_to_delete = offers_factories.VenueFactory()
    offers_factories.OfferFactory(venue=venue_to_delete)
    offers_factories.StockFactory(offer__venue=venue_to_delete)
    offers_factories.StockFactory(offer__venue__managingOfferer=venue_to_delete.managingOfferer)

    # When
    delete_cascade_venue_by_id(venue_to_delete.id)

    # Then
    assert Offerer.query.count() == 1
    assert Venue.query.count() == 1
    assert Offer.query.count() == 1
    assert Stock.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_venue_should_remove_bank_informations_of_venue():
    # Given
    venue_to_delete = offers_factories.VenueFactory()
    offers_factories.BankInformationFactory(venue=venue_to_delete)
    offers_factories.BankInformationFactory()

    # When
    delete_cascade_venue_by_id(venue_to_delete.id)

    # Then
    assert Venue.query.count() == 0
    assert Offerer.query.count() == 1
    assert BankInformation.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_venue_should_remove_mediations_of_managed_offers():
    # Given
    venue = offers_factories.VenueFactory()
    venue_to_delete = offers_factories.VenueFactory()
    offers_factories.MediationFactory(offer__venue=venue_to_delete)
    offers_factories.MediationFactory(offer__venue=venue)

    # When
    delete_cascade_venue_by_id(venue_to_delete.id)

    # Then
    assert Offerer.query.count() == 2
    assert Venue.query.count() == 1
    assert Offer.query.count() == 1
    assert Mediation.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_venue_should_remove_favorites_of_managed_offers():
    # Given
    venue = offers_factories.VenueFactory()
    venue_to_delete = offers_factories.VenueFactory()
    users_factories.FavoriteFactory(offer__venue=venue_to_delete)
    users_factories.FavoriteFactory(offer__venue=venue)

    # When
    delete_cascade_venue_by_id(venue_to_delete.id)

    # Then
    assert Offerer.query.count() == 2
    assert Venue.query.count() == 1
    assert Offer.query.count() == 1
    assert Favorite.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_venue_should_remove_criterions():
    # Given
    venue = offers_factories.VenueFactory()
    venue_to_delete = offers_factories.VenueFactory()
    offers_factories.OfferCriterionFactory(offer__venue=venue_to_delete)
    offers_factories.OfferCriterionFactory(offer__venue=venue)

    # When
    delete_cascade_venue_by_id(venue_to_delete.id)

    # Then
    assert Offerer.query.count() == 2
    assert Venue.query.count() == 1
    assert Offer.query.count() == 1
    assert OfferCriterion.query.count() == 1
    assert Criterion.query.count() == 2


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_venue_should_remove_synchronization_to_provider():
    # Given
    venue = offers_factories.VenueFactory()
    venue_to_delete = offers_factories.VenueFactory()
    offerers_factories.VenueProviderFactory(venue=venue_to_delete)
    offerers_factories.VenueProviderFactory(venue=venue)

    # When
    delete_cascade_venue_by_id(venue_to_delete.id)

    # Then
    assert Offerer.query.count() == 2
    assert Venue.query.count() == 1
    assert VenueProvider.query.count() == 1
    assert Provider.query.count() > 0


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_venue_should_remove_synchronization_to_allocine_provider():
    # Given
    venue = offers_factories.VenueFactory()
    venue_to_delete = offers_factories.VenueFactory()
    offerers_factories.AllocineVenueProviderPriceRuleFactory(allocineVenueProvider__venue=venue_to_delete)
    offerers_factories.AllocineVenueProviderPriceRuleFactory(allocineVenueProvider__venue=venue)

    # When
    delete_cascade_venue_by_id(venue_to_delete.id)

    # Then
    assert Offerer.query.count() == 2
    assert Venue.query.count() == 1
    assert VenueProvider.query.count() == 1
    assert AllocineVenueProvider.query.count() == 1
    assert AllocineVenueProviderPriceRule.query.count() == 1
    assert Provider.query.count() > 0
