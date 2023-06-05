import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.bookings.models as bookings_models
import pcapi.core.criteria.factories as criteria_factories
import pcapi.core.criteria.models as criteria_models
import pcapi.core.educational.factories as educational_factories
import pcapi.core.educational.models as educational_models
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
from pcapi.scripts.offerer.delete_cascade_venue_by_id import delete_cascade_venue_by_id


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_venue_should_abort_when_venue_has_any_bookings():
    # Given
    booking = bookings_factories.BookingFactory()
    venue_to_delete = booking.venue

    # When
    with pytest.raises(offerers_exceptions.CannotDeleteVenueWithBookingsException) as exception:
        delete_cascade_venue_by_id(venue_to_delete.id)

    # Then
    assert exception.value.errors["cannotDeleteVenueWithBookingsException"] == [
        "Lieu non supprimable car il contient des réservations"
    ]
    assert offerers_models.Venue.query.count() == 1
    assert offers_models.Stock.query.count() == 1
    assert bookings_models.Booking.query.count() == 1


def test_delete_cascade_venue_should_abort_when_venue_has_any_collective_bookings(db_session):
    # Given
    booking = educational_factories.CollectiveBookingFactory()
    venue_to_delete = booking.venue

    # When
    with pytest.raises(offerers_exceptions.CannotDeleteVenueWithBookingsException) as exception:
        delete_cascade_venue_by_id(venue_to_delete.id)

    # Then
    assert exception.value.errors["cannotDeleteVenueWithBookingsException"] == [
        "Lieu non supprimable car il contient des réservations"
    ]
    assert offerers_models.Venue.query.count() == 1
    assert educational_models.CollectiveStock.query.count() == 1
    assert educational_models.CollectiveBooking.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_venue_should_abort_when_pricing_point_for_another_venue():
    # Given
    venue_to_delete = offerers_factories.VenueFactory(pricing_point="self")
    offerers_factories.VenueFactory(pricing_point=venue_to_delete, managingOfferer=venue_to_delete.managingOfferer)

    # When
    with pytest.raises(offerers_exceptions.CannotDeleteVenueUsedAsPricingPointException) as exception:
        delete_cascade_venue_by_id(venue_to_delete.id)

    # Then
    assert exception.value.errors["cannotDeleteVenueUsedAsPricingPointException"] == [
        "Lieu non supprimable car il est utilisé comme point de valorisation d'un autre lieu"
    ]
    assert offerers_models.Offerer.query.count() == 1
    assert offerers_models.Venue.query.count() == 2
    assert offerers_models.VenuePricingPointLink.query.count() == 2


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_venue_should_abort_when_reimbursement_point_for_another_venue():
    # Given
    venue_to_delete = offerers_factories.VenueFactory(reimbursement_point="self")
    offerers_factories.VenueFactory(
        reimbursement_point=venue_to_delete, managingOfferer=venue_to_delete.managingOfferer
    )

    # When
    with pytest.raises(offerers_exceptions.CannotDeleteVenueUsedAsReimbursementPointException) as exception:
        delete_cascade_venue_by_id(venue_to_delete.id)

    # Then
    assert exception.value.errors["cannotDeleteVenueUsedAsReimbursementPointException"] == [
        "Lieu non supprimable car il est utilisé comme point de remboursement d'un autre lieu"
    ]
    assert offerers_models.Offerer.query.count() == 1
    assert offerers_models.Venue.query.count() == 2
    assert offerers_models.VenueReimbursementPointLink.query.count() == 2


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_venue_should_remove_offers_stocks_and_activation_codes():
    # Given
    venue_to_delete = offerers_factories.VenueFactory()
    offer_1 = offers_factories.OfferFactory(venue=venue_to_delete)
    offer_2 = offers_factories.OfferFactory(venue=venue_to_delete)
    stock = offers_factories.StockFactory(offer__venue=venue_to_delete)
    event_stock = offers_factories.EventStockFactory(offer__venue=venue_to_delete)
    items_to_delete = [offer_1.id, offer_2.id, stock.offerId, event_stock.offerId]

    other_venue = offerers_factories.VenueFactory(managingOfferer=venue_to_delete.managingOfferer)
    price_category_label = offers_factories.PriceCategoryLabelFactory(label="otherLabel", venue=other_venue)
    offers_factories.ActivationCodeFactory(stock=stock)
    stock_with_another_venue = offers_factories.EventStockFactory(
        offer__venue=other_venue,
        priceCategory__priceCategoryLabel=price_category_label,
    )
    offers_factories.ActivationCodeFactory(stock=stock_with_another_venue)
    # When
    recap_data = delete_cascade_venue_by_id(venue_to_delete.id)

    # Then
    assert offerers_models.Venue.query.count() == 1
    assert offers_models.Offer.query.count() == 1
    assert offers_models.Stock.query.count() == 1
    assert offers_models.ActivationCode.query.count() == 1
    assert offers_models.PriceCategory.query.count() == 1
    assert offers_models.PriceCategoryLabel.query.count() == 1
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
    assert offerers_models.Venue.query.count() == 1
    assert educational_models.CollectiveOffer.query.count() == 1
    assert educational_models.CollectiveOfferTemplate.query.count() == 0
    assert educational_models.CollectiveStock.query.count() == 1
    assert sorted(recap_data["collective_offer_ids_to_unindex"]) == sorted(collective_offers_to_delete)
    assert recap_data["collective_offer_template_ids_to_unindex"] == [offer_2_id]


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_venue_should_remove_bank_informations_of_venue():
    # Given
    venue_to_delete = offerers_factories.VenueFactory()
    finance_factories.BankInformationFactory(venue=venue_to_delete)
    finance_factories.BankInformationFactory()

    # When
    delete_cascade_venue_by_id(venue_to_delete.id)

    # Then
    assert offerers_models.Venue.query.count() == 0
    assert offerers_models.Offerer.query.count() == 1
    assert finance_models.BankInformation.query.count() == 1


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_venue_should_remove_pricing_point_links():
    venue = offerers_factories.VenueFactory(pricing_point="self")

    delete_cascade_venue_by_id(venue.id)

    assert offerers_models.Venue.query.count() == 0
    assert offerers_models.VenuePricingPointLink.query.count() == 0


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_venue_should_remove_reimbursement_point_links():
    venue = offerers_factories.VenueFactory(reimbursement_point="self")

    delete_cascade_venue_by_id(venue.id)

    assert offerers_models.Venue.query.count() == 0
    assert offerers_models.VenueReimbursementPointLink.query.count() == 0


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
    assert offerers_models.Venue.query.count() == 1
    assert offers_models.Offer.query.count() == 1
    assert offers_models.Mediation.query.count() == 1


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
    assert offerers_models.Venue.query.count() == 1
    assert offers_models.Offer.query.count() == 1
    assert users_models.Favorite.query.count() == 1


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
    assert offerers_models.Venue.query.count() == 1
    assert offers_models.Offer.query.count() == 1
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
    assert offerers_models.Venue.query.count() == 1
    assert providers_models.VenueProvider.query.count() == 1
    assert providers_models.Provider.query.count() > 0


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_venue_should_remove_synchronization_to_allocine_provider():
    # Given
    venue = offerers_factories.VenueFactory()
    venue_to_delete = offerers_factories.VenueFactory()
    providers_factories.AllocineVenueProviderPriceRuleFactory(allocineVenueProvider__venue=venue_to_delete)
    providers_factories.AllocineVenueProviderPriceRuleFactory(allocineVenueProvider__venue=venue)
    providers_factories.AllocinePivotFactory(venue=venue_to_delete)
    providers_factories.AllocinePivotFactory(venue=venue, theaterId="ABCDEFGHIJKLMNOPQR==", internalId="PABCDE")

    # When
    delete_cascade_venue_by_id(venue_to_delete.id)

    # Then
    assert offerers_models.Venue.query.count() == 1
    assert providers_models.VenueProvider.query.count() == 1
    assert providers_models.AllocineVenueProvider.query.count() == 1
    assert providers_models.AllocineVenueProviderPriceRule.query.count() == 1
    assert providers_models.AllocinePivot.query.count() == 1
    assert providers_models.Provider.query.count() > 0


@pytest.mark.usefixtures("db_session")
def test_delete_cascade_venue_when_template_has_offer_on_other_venue():
    venue = offerers_factories.VenueFactory()
    venue2 = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
    template = educational_factories.CollectiveOfferTemplateFactory(venue=venue)
    offer = educational_factories.CollectiveOfferFactory(venue=venue2, template=template)
    delete_cascade_venue_by_id(venue.id)

    assert offerers_models.Venue.query.count() == 1
    assert educational_models.CollectiveOffer.query.count() == 1
    assert educational_models.CollectiveOfferTemplate.query.count() == 0
    assert offer.template is None
