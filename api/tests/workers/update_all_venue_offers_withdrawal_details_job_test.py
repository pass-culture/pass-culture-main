from unittest import mock

import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.workers.update_all_venue_offers_withdrawal_details_job import update_all_venue_offers_withdrawal_details_job



def test_update_all_venue_offers_withdrawal_details_job():
    venue = offerers_factories.VenueFactory()
    offer1 = offers_factories.OfferFactory(venue=venue)
    offer2 = offers_factories.OfferFactory(venue=venue)
    offer3 = offers_factories.OfferFactory(venue=venue)
    offer1_stock = offers_factories.StockFactory(offer=offer1)
    bookings_factories.BookingFactory(stock=offer1_stock)
    withdrawal_details = "Ceci est un exemple de modalités de retrait d'un bien"

    with mock.patch("pcapi.core.mails.transactional.send_booking_withdrawal_updated") as mailer_mock:
        update_all_venue_offers_withdrawal_details_job(venue, withdrawal_details)

    assert offer1.withdrawalDetails == withdrawal_details
    assert offer2.withdrawalDetails == withdrawal_details
    assert offer3.withdrawalDetails == withdrawal_details
    assert not mailer_mock.called



def test_update_all_venue_offers_withdrawal_with_email_notif():
    venue = offerers_factories.VenueFactory()
    offer1 = offers_factories.OfferFactory(venue=venue)
    offer2 = offers_factories.OfferFactory(venue=venue)
    offer3 = offers_factories.OfferFactory(venue=venue)
    offer1_stock = offers_factories.StockFactory(offer=offer1)
    offer2_stock = offers_factories.StockFactory(offer=offer2)
    bookings_factories.BookingFactory(stock=offer1_stock)
    bookings_factories.BookingFactory(stock=offer1_stock)
    bookings_factories.BookingFactory(stock=offer2_stock)
    withdrawal_details = "Ceci est un exemple de modalités de retrait d'un bien"

    with mock.patch("pcapi.core.mails.transactional.send_booking_withdrawal_updated") as mailer_mock:
        update_all_venue_offers_withdrawal_details_job(venue, withdrawal_details, send_email_notification=True)

    assert offer1.withdrawalDetails == withdrawal_details
    assert offer2.withdrawalDetails == withdrawal_details
    assert offer3.withdrawalDetails == withdrawal_details
    assert mailer_mock.call_count == 3
