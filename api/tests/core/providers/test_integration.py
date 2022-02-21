import pytest

import pcapi.core.bookings.api as bookings_api
import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.bookings.models as bookings_models
from pcapi.core.categories import subcategories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.providers import api
from pcapi.core.providers import models


pytestmark = pytest.mark.usefixtures("db_session")


def test_negative_remaining_quantity_then_cancel_booking():
    # We have a pending booking...
    provider = offerers_factories.APIProviderFactory()
    stock = offers_factories.StockFactory(
        rawProviderQuantity=1,
        quantity=1,
        lastProvider=provider,
        idAtProviders="reference@siret",
        offer__idAtProvider="reference",
        offer__product__idAtProviders="reference",
        offer__product__subcategoryId=subcategories.LIVRE_PAPIER.id,
        offer__venue__siret="siret",
    )
    booking = bookings_factories.IndividualBookingFactory(stock=stock)

    # ... but the library informs us that, actually, they sold the
    # last item.
    details = [
        models.StockDetail(
            products_provider_reference="reference",
            offers_provider_reference="reference",
            venue_reference=f"reference@{booking.venue.id}",
            stocks_provider_reference=f"reference@{booking.venue.siret}",
            available_quantity=0,
            price=10,
        ),
    ]
    api.synchronize_stocks(details, booking.venue, provider.id)
    assert stock.rawProviderQuantity == 0
    assert stock.quantity == 0
    assert stock.dnBookedQuantity == 1

    # The beneficiary or the library should be able to cancel the
    # booking.
    bookings_api.cancel_booking_by_offerer(booking)
    assert booking.status == bookings_models.BookingStatus.CANCELLED


def test_negative_remaining_quantity_then_validate_booking():
    # We have a pending booking...
    provider = offerers_factories.APIProviderFactory()
    stock = offers_factories.StockFactory(
        rawProviderQuantity=1,
        quantity=1,
        lastProvider=provider,
        idAtProviders="reference@siret",
        offer__idAtProvider="reference",
        offer__product__idAtProviders="reference",
        offer__product__subcategoryId=subcategories.LIVRE_PAPIER.id,
        offer__venue__siret="siret",
    )
    booking = bookings_factories.BookingFactory(stock=stock)

    # ... but the library informs us that, actually, they sold the
    # last copy of the book.
    details = [
        models.StockDetail(
            products_provider_reference="reference",
            offers_provider_reference="reference",
            venue_reference=f"reference@{booking.venue.id}",
            stocks_provider_reference=f"reference@{booking.venue.siret}",
            available_quantity=0,
            price=10,
        ),
    ]
    api.synchronize_stocks(details, booking.venue, provider.id)
    assert stock.rawProviderQuantity == 0
    assert stock.quantity == 0
    assert stock.dnBookedQuantity == 1

    # ... but in turns out that, in fact, the library had an extra,
    # unaccounted copy hidden somewhere. The beneficiary has been able
    # to retrieve their booking and we should be able to mark it as
    # used.
    bookings_api.mark_as_used(booking)
    assert booking.status == bookings_models.BookingStatus.USED
