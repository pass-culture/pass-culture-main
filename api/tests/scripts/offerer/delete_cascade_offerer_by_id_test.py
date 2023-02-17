import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.bookings.models as bookings_models
import pcapi.core.criteria.factories as criteria_factories
import pcapi.core.criteria.models as criteria_models
import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.exceptions as offerers_exceptions
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.factories as providers_factories
import pcapi.core.providers.models as providers_models
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
from pcapi.scripts.offerer.delete_cascade_offerer_by_id import delete_cascade_offerer_by_id


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_abort_when_offerer_has_any_bookings():
    # Given
    offerer_to_delete = offerers_factories.OffererFactory()
    offers_factories.OfferFactory(venue__managingOfferer=offerer_to_delete)
    bookings_factories.BookingFactory(stock__offer__venue__managingOfferer=offerer_to_delete)

    # When
    with pytest.raises(offerers_exceptions.CannotDeleteOffererWithBookingsException) as exception:
        delete_cascade_offerer_by_id(offerer_to_delete.id)

    # Then
    assert exception.value.errors["cannotDeleteOffererWithBookingsException"] == [
        "Structure juridique non supprimable car elle contient des réservations"
    ]
    assert offerers_models.Offerer.query.count() == 1
    assert offerers_models.Venue.query.count() == 2
    assert offers_models.Offer.query.count() == 2
    assert offers_models.Stock.query.count() == 1
    assert bookings_models.Booking.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_remove_managed_venues_offers_stocks_and_activation_codes():
    # Given
    offerer_to_delete = offerers_factories.OffererFactory()
    offers_factories.OfferFactory(venue__managingOfferer=offerer_to_delete)
    stock_1 = offers_factories.StockFactory(offer__venue__managingOfferer=offerer_to_delete)
    stock_2 = offers_factories.StockFactory()
    offers_factories.ActivationCodeFactory(stock=stock_1)
    offers_factories.ActivationCodeFactory(stock=stock_2)

    # When
    delete_cascade_offerer_by_id(offerer_to_delete.id)

    # Then
    assert offerers_models.Offerer.query.count() == 1
    assert offerers_models.Venue.query.count() == 1
    assert offers_models.Offer.query.count() == 1
    assert offers_models.Stock.query.count() == 1
    assert offers_models.ActivationCode.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_remove_all_user_attachments_to_deleted_offerer():
    # Given
    pro = users_factories.ProFactory()
    offerer_to_delete = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer_to_delete)
    offerers_factories.UserOffererFactory(user=pro)

    # When
    delete_cascade_offerer_by_id(offerer_to_delete.id)

    # Then
    assert offerers_models.Offerer.query.count() == 1
    assert offerers_models.UserOfferer.query.count() == 1
    assert users_models.User.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_remove_api_key_of_offerer():
    # Given
    offerer_to_delete = offerers_factories.OffererFactory()
    offerers_factories.ApiKeyFactory(offerer=offerer_to_delete)
    offerers_factories.ApiKeyFactory(prefix="other-prefix")

    # When
    delete_cascade_offerer_by_id(offerer_to_delete.id)

    # Then
    assert offerers_models.Offerer.query.count() == 1
    assert offerers_models.ApiKey.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_remove_products_owned_by_offerer():
    # Given
    offerer_to_delete = offerers_factories.OffererFactory()
    offers_factories.ProductFactory(owningOfferer=offerer_to_delete)
    offers_factories.ProductFactory()

    # When
    delete_cascade_offerer_by_id(offerer_to_delete.id)

    # Then
    assert offerers_models.Offerer.query.count() == 0
    assert offers_models.Product.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_remove_bank_informations_of_offerer():
    # Given
    offerer_to_delete = offerers_factories.OffererFactory()
    finance_factories.BankInformationFactory(offerer=offerer_to_delete)
    finance_factories.BankInformationFactory()

    # When
    delete_cascade_offerer_by_id(offerer_to_delete.id)

    # Then
    assert offerers_models.Offerer.query.count() == 0
    assert finance_models.BankInformation.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_remove_offers_of_offerer():
    # Given
    offerer_to_delete = offerers_factories.OffererFactory()
    venue = offerers_factories.VenueFactory(managingOfferer=offerer_to_delete)
    event_offer = offers_factories.EventOfferFactory(venue=venue)
    thing_offer = offers_factories.ThingOfferFactory(venue=venue)
    items_to_delete = [event_offer.id, thing_offer.id]

    # When
    recap_data = delete_cascade_offerer_by_id(offerer_to_delete.id)

    # Then
    assert offerers_models.Offerer.query.count() == 0
    assert offers_models.Offer.query.count() == 0
    assert sorted(recap_data["offer_ids_to_unindex"]) == sorted(items_to_delete)


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_remove_pricing_point_links():
    venue = offerers_factories.VenueFactory(pricing_point="self")
    offerers_factories.VenueFactory(pricing_point=venue, managingOfferer=venue.managingOfferer)
    offerer = venue.managingOfferer

    delete_cascade_offerer_by_id(offerer.id)

    assert offerers_models.Offerer.query.count() == 0
    assert offerers_models.Venue.query.count() == 0
    assert offerers_models.VenuePricingPointLink.query.count() == 0


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_remove_reimbursement_point_links():
    venue = offerers_factories.VenueFactory(reimbursement_point="self")
    offerer = venue.managingOfferer

    delete_cascade_offerer_by_id(offerer.id)

    assert offerers_models.Offerer.query.count() == 0
    assert offerers_models.Venue.query.count() == 0
    assert offerers_models.VenueReimbursementPointLink.query.count() == 0


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_remove_bank_informations_of_managed_venue():
    # Given
    venue = offerers_factories.VenueFactory(reimbursement_point="self")
    finance_factories.BankInformationFactory(venue=venue)
    offerer_to_delete = venue.managingOfferer
    finance_factories.BankInformationFactory()
    assert finance_models.BankInformation.query.count() == 2

    # When
    delete_cascade_offerer_by_id(offerer_to_delete.id)

    # Then
    assert offerers_models.Offerer.query.count() == 0
    assert offerers_models.Venue.query.count() == 0
    assert finance_models.BankInformation.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_remove_mediations_of_managed_offers():
    # Given
    offerer_to_delete = offerers_factories.OffererFactory()
    offers_factories.MediationFactory(offer__venue__managingOfferer=offerer_to_delete)
    offers_factories.MediationFactory()

    # When
    delete_cascade_offerer_by_id(offerer_to_delete.id)

    # Then
    assert offerers_models.Offerer.query.count() == 1
    assert offerers_models.Venue.query.count() == 1
    assert offers_models.Offer.query.count() == 1
    assert offers_models.Mediation.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_remove_favorites_of_managed_offers():
    # Given
    offerer_to_delete = offerers_factories.OffererFactory()
    users_factories.FavoriteFactory(offer__venue__managingOfferer=offerer_to_delete)
    users_factories.FavoriteFactory()

    # When
    delete_cascade_offerer_by_id(offerer_to_delete.id)

    # Then
    assert offerers_models.Offerer.query.count() == 1
    assert offerers_models.Venue.query.count() == 1
    assert offers_models.Offer.query.count() == 1
    assert users_models.Favorite.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_remove_criterion_attachment_of_managed_offers():
    # Given
    offerer_to_delete = offerers_factories.OffererFactory()
    offers_factories.OfferFactory(
        venue__managingOfferer=offerer_to_delete,
        criteria=[criteria_factories.CriterionFactory()],
    )
    offers_factories.OfferFactory(criteria=[criteria_factories.CriterionFactory()])
    # When
    delete_cascade_offerer_by_id(offerer_to_delete.id)

    # Then
    assert offerers_models.Offerer.query.count() == 1
    assert offerers_models.Venue.query.count() == 1
    assert offers_models.Offer.query.count() == 1
    assert criteria_models.OfferCriterion.query.count() == 1
    assert criteria_models.Criterion.query.count() == 2


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_remove_venue_synchronization_to_provider():
    # Given
    offerer_to_delete = offerers_factories.OffererFactory()
    providers_factories.VenueProviderFactory(venue__managingOfferer=offerer_to_delete)
    providers_factories.VenueProviderFactory()

    # When
    delete_cascade_offerer_by_id(offerer_to_delete.id)

    # Then
    assert offerers_models.Offerer.query.count() == 1
    assert offerers_models.Venue.query.count() == 1
    assert providers_models.VenueProvider.query.count() == 1
    assert providers_models.Provider.query.count() > 0


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_offerer_should_remove_venue_synchronization_to_allocine_provider():
    # Given
    offerer_to_delete = offerers_factories.OffererFactory()
    venue_to_delete = offerers_factories.VenueFactory(managingOfferer=offerer_to_delete)
    other_venue = offerers_factories.VenueFactory()
    providers_factories.AllocineVenueProviderPriceRuleFactory(allocineVenueProvider__venue=venue_to_delete)
    providers_factories.AllocineVenueProviderPriceRuleFactory(allocineVenueProvider__venue=other_venue)
    providers_factories.AllocinePivotFactory(venue=venue_to_delete)
    providers_factories.AllocinePivotFactory(venue=other_venue, theaterId="ABCDEFGHIJKLMNOPQR==", internalId="PABCDE")

    # When
    delete_cascade_offerer_by_id(offerer_to_delete.id)

    # Then
    assert offerers_models.Offerer.query.count() == 1
    assert offerers_models.Venue.query.count() == 1
    assert providers_models.VenueProvider.query.count() == 1
    assert providers_models.AllocineVenueProvider.query.count() == 1
    assert providers_models.AllocineVenueProviderPriceRule.query.count() == 1
    assert providers_models.AllocinePivot.query.count() == 1
    assert providers_models.Provider.query.count() > 0
