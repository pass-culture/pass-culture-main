from datetime import datetime
from datetime import timedelta

import pytest

from pcapi.core.bookings.factories import CancelledBookingFactory
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.categories import subcategories
from pcapi.core.offers.factories import ProductFactory
import pcapi.core.users.factories as users_factories
from pcapi.emails.beneficiary_expired_bookings import build_expired_bookings_recap_email_data_for_beneficiary


@pytest.mark.usefixtures("db_session")
def test_should_send_email_to_beneficiary_when_expired_bookings_cancelled():
    now = datetime.utcnow()
    amnesiac_user = users_factories.UserFactory(email="dory@example.com", firstName="Dory")
    long_ago = now - timedelta(days=31)
    dvd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id)
    expired_today_dvd_booking = CancelledBookingFactory(
        stock__offer__product=dvd,
        stock__offer__name="Memento",
        stock__offer__venue__name="Mnémosyne",
        dateCreated=long_ago,
        cancellationReason=BookingCancellationReasons.EXPIRED,
        user=amnesiac_user,
    )

    cd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id)
    expired_today_cd_booking = CancelledBookingFactory(
        stock__offer__product=cd,
        stock__offer__name="Random Access Memories",
        stock__offer__venue__name="Virgin Megastore",
        dateCreated=long_ago,
        cancellationReason=BookingCancellationReasons.EXPIRED,
        user=amnesiac_user,
    )

    email_data = build_expired_bookings_recap_email_data_for_beneficiary(
        amnesiac_user, [expired_today_dvd_booking, expired_today_cd_booking], 30
    )

    assert email_data == {
        "Mj-TemplateID": 3095107,
        "Mj-TemplateLanguage": True,
        "Vars": {
            "user_firstName": "Dory",
            "bookings": [
                {"offer_name": "Memento", "venue_name": "Mnémosyne"},
                {"offer_name": "Random Access Memories", "venue_name": "Virgin Megastore"},
            ],
            "withdrawal_period": 30,
        },
    }
