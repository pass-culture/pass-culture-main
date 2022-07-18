import pytest

from pcapi.core.bookings.exceptions import CannotDeleteVenueWithBookingsException
import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import Booking
import pcapi.core.criteria.factories as criteria_factories
import pcapi.core.criteria.models as criteria_models
from pcapi.core.educational import models as educational_models
import pcapi.core.educational.factories as educational_factories
import pcapi.core.finance.factories as finance_factories
from pcapi.core.finance.models import BankInformation
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import ActivationCode
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
from pcapi.scripts.offerer.delete_cascade_venue_by_id import delete_cascade_venue_by_id


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_venue_should_abort_when_venue_has_any_bookings():
    # Given
    booking = bookings_factories.BookingFactory()
    venue_to_delete = booking.venue

    # When
    with pytest.raises(CannotDeleteVenueWithBookingsException) as exception:
        delete_cascade_venue_by_id(venue_to_delete.id)

    # Then
    assert exception.value.errors["cannotDeleteVenueWithBookingsException"] == [
        "Lieu non supprimable car il contient des réservations"
    ]
    assert Venue.query.count() == 1
    assert Stock.query.count() == 1
    assert Booking.query.count() == 1


def test_delete_cascade_venue_should_abort_when_venue_has_any_collective_bookings(db_session):
    # Given
    booking = educational_factories.CollectiveBookingFactory()
    venue_to_delete = booking.venue

    # When
    with pytest.raises(CannotDeleteVenueWithBookingsException) as exception:
        delete_cascade_venue_by_id(venue_to_delete.id)

    # Then
    assert exception.value.errors["cannotDeleteVenueWithBookingsException"] == [
        "Lieu non supprimable car il contient des réservations"
    ]
    assert Venue.query.count() == 1
    assert educational_models.CollectiveStock.query.count() == 1
    assert educational_models.CollectiveBooking.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_venue_should_remove_offers_stocks_and_activation_codes():
    # Given
    venue_to_delete = offerers_factories.VenueFactory()
    offer_1 = offers_factories.OfferFactory(venue=venue_to_delete)
    offer_2 = offers_factories.OfferFactory(venue=venue_to_delete)
    stock = offers_factories.StockFactory(offer__venue=venue_to_delete)
    stock_with_another_venue = offers_factories.StockFactory(
        offer__venue__managingOfferer=venue_to_delete.managingOfferer
    )
    items_to_delete = [offer_1.id, offer_2.id, stock.offerId]
    offers_factories.ActivationCodeFactory(stock=stock)
    offers_factories.ActivationCodeFactory(stock=stock_with_another_venue)

    # When
    recap_data = delete_cascade_venue_by_id(venue_to_delete.id)

    # Then
    assert Venue.query.count() == 1
    assert Offer.query.count() == 1
    assert Stock.query.count() == 1
    assert ActivationCode.query.count() == 1
    assert sorted(recap_data["offer_ids_to_unindex"]) == sorted(items_to_delete)


def test_delete_cascade_venue_should_remove_collective_offers_stocks_and_templates(db_session):
    # Given
    venue_to_delete = offerers_factories.VenueFactory()
    offer_1 = educational_factories.CollectiveOfferFactory(venue=venue_to_delete)
    offer_2 = educational_factories.CollectiveOfferTemplateFactory(venue=venue_to_delete)
    stock = educational_factories.CollectiveStockFactory(collectiveOffer__venue=venue_to_delete)
    educational_factories.CollectiveStockFactory(
        collectiveOffer__venue__managingOfferer=venue_to_delete.managingOfferer
    )
    collective_offers_to_delete = [offer_1.id, stock.collectiveOfferId]
    # As the collective offer template will be deleted, we need to stock the information
    offer_2_id = offer_2.id

    # When
    recap_data = delete_cascade_venue_by_id(venue_to_delete.id)

    # Then
    assert Venue.query.count() == 1
    assert educational_models.CollectiveOffer.query.count() == 1
    assert educational_models.CollectiveOfferTemplate.query.count() == 0
    assert educational_models.CollectiveStock.query.count() == 1
    assert sorted(recap_data["collective_offer_ids_to_unindex"]) == sorted(collective_offers_to_delete)
    assert recap_data["collective_offer_template_ids_to_unindex"] == [offer_2_id]


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_venue_should_remove_bank_informations_of_venue():
    # Given
    venue_to_delete = offerers_factories.VenueFactory(businessUnit=None)
    finance_factories.BankInformationFactory(venue=venue_to_delete)
    finance_factories.BankInformationFactory()

    # When
    delete_cascade_venue_by_id(venue_to_delete.id)

    # Then
    assert Venue.query.count() == 0
    assert Offerer.query.count() == 1
    assert BankInformation.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_venue_should_remove_mediations_of_managed_offers():
    # Given
    venue = offerers_factories.VenueFactory()
    venue_to_delete = offerers_factories.VenueFactory()
    offers_factories.MediationFactory(offer__venue=venue_to_delete)
    offers_factories.MediationFactory(offer__venue=venue)

    # When
    delete_cascade_venue_by_id(venue_to_delete.id)

    # Then
    assert Venue.query.count() == 1
    assert Offer.query.count() == 1
    assert Mediation.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_venue_should_remove_favorites_of_managed_offers():
    # Given
    venue = offerers_factories.VenueFactory()
    venue_to_delete = offerers_factories.VenueFactory()
    users_factories.FavoriteFactory(offer__venue=venue_to_delete)
    users_factories.FavoriteFactory(offer__venue=venue)

    # When
    delete_cascade_venue_by_id(venue_to_delete.id)

    # Then
    assert Venue.query.count() == 1
    assert Offer.query.count() == 1
    assert Favorite.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_venue_should_remove_criterions():
    # Given
    offers_factories.OfferFactory(
        venue=offerers_factories.VenueFactory(), criteria=[criteria_factories.CriterionFactory()]
    )
    offer_venue_to_delete = offers_factories.OfferFactory(
        venue=offerers_factories.VenueFactory(), criteria=[criteria_factories.CriterionFactory()]
    )

    # When
    delete_cascade_venue_by_id(offer_venue_to_delete.venue.id)

    # Then
    assert Venue.query.count() == 1
    assert Offer.query.count() == 1
    assert criteria_models.OfferCriterion.query.count() == 1
    assert criteria_models.Criterion.query.count() == 2


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_venue_should_remove_synchronization_to_provider():
    # Given
    venue = offerers_factories.VenueFactory()
    venue_to_delete = offerers_factories.VenueFactory()
    providers_factories.VenueProviderFactory(venue=venue_to_delete)
    providers_factories.VenueProviderFactory(venue=venue)

    # When
    delete_cascade_venue_by_id(venue_to_delete.id)

    # Then
    assert Venue.query.count() == 1
    assert VenueProvider.query.count() == 1
    assert Provider.query.count() > 0


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_venue_should_remove_synchronization_to_allocine_provider():
    # Given
    venue = offerers_factories.VenueFactory()
    venue_to_delete = offerers_factories.VenueFactory()
    providers_factories.AllocineVenueProviderPriceRuleFactory(allocineVenueProvider__venue=venue_to_delete)
    providers_factories.AllocineVenueProviderPriceRuleFactory(allocineVenueProvider__venue=venue)

    # When
    delete_cascade_venue_by_id(venue_to_delete.id)

    # Then
    assert Venue.query.count() == 1
    assert VenueProvider.query.count() == 1
    assert AllocineVenueProvider.query.count() == 1
    assert AllocineVenueProviderPriceRule.query.count() == 1
    assert Provider.query.count() > 0
