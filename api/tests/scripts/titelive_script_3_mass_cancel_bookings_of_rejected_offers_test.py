from unittest import mock

import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.bookings.models as bookings_models
import pcapi.core.offers.factories as offers_factories
from pcapi.core.search.backends import algolia
from pcapi.scripts import titelive_script_3_mass_cancel_bookings_of_rejected_offers


pytestmark = pytest.mark.usefixtures("db_session")


@mock.patch("pcapi.tasks.amplitude_tasks.track_event.delay")
@mock.patch("pcapi.core.external.attributes.api.update_batch_user")
@mock.patch("pcapi.core.external.attributes.api.update_sendinblue_user")
@mock.patch("pcapi.tasks.sendinblue_tasks.update_sib_pro_attributes_task.delay")
def test_process_bookings_does_not_perform_external_actions(
    mocked_amplitude_track_event,
    mocked_update_batch_user,
    mocked_update_sendinblue_user,
    mocked_update_sib_pro_attributes_task,
    app,
):
    # No offer reindexation, no Amplitude event, no SendinBlue
    # updates, etc.
    booking = bookings_factories.BookingFactory(
        stock__offer__venue__bookingEmail="test@example.com",
    )

    titelive_script_3_mass_cancel_bookings_of_rejected_offers.process_booking(booking)

    assert booking.status == bookings_models.BookingStatus.CANCELLED
    assert app.redis_client.scard(algolia.REDIS_OFFER_IDS_NAME) == 0
    mocked_amplitude_track_event.assert_not_called()
    mocked_update_batch_user.assert_not_called()
    mocked_update_sendinblue_user.assert_not_called()
    mocked_update_sib_pro_attributes_task.assert_not_called()


def test_process_offers():
    stock1 = offers_factories.StockFactory()
    booking1_cancellable = bookings_factories.BookingFactory(stock=stock1)
    booking1_used = bookings_factories.UsedBookingFactory(stock=stock1)
    stock2 = offers_factories.StockFactory()
    booking2_cancellable = bookings_factories.BookingFactory(stock=stock2)
    stock3 = offers_factories.StockFactory()
    booking3_cancellable = bookings_factories.BookingFactory(stock=stock3)
    stock4 = offers_factories.StockFactory()

    lines = [
        f"{stock1.offerId}\n",
        f"{stock2.offerId}\n",
        # booking of stock3 should not be cancelled
        f"{stock4.offerId}\n",
    ]

    titelive_script_3_mass_cancel_bookings_of_rejected_offers.process_offers(lines, 1)

    assert booking1_cancellable.status == bookings_models.BookingStatus.CANCELLED  # updated
    assert booking1_used.status == bookings_models.BookingStatus.USED  # unchanged
    assert booking2_cancellable.status == bookings_models.BookingStatus.CANCELLED  # updated
    assert booking3_cancellable.status == bookings_models.BookingStatus.CONFIRMED  # unchanged
