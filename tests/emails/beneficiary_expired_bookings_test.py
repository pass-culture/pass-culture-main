from datetime import datetime
from datetime import timedelta

import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.offers.factories import ProductFactory
import pcapi.core.users.factories as users_factories
from pcapi.emails.beneficiary_expired_bookings import build_expired_bookings_recap_email_data_for_beneficiary
from pcapi.models import offer_type


@pytest.mark.usefixtures("db_session")
def test_should_send_email_to_offerer_when_expired_bookings_cancelled():
    now = datetime.utcnow()
    amnesiac_user = users_factories.UserFactory(email="dory@example.com", firstName="Dory")
    long_ago = now - timedelta(days=31)
    dvd = ProductFactory(type=str(offer_type.ThingType.AUDIOVISUEL))
    expired_today_dvd_booking = BookingFactory(
        stock__offer__product=dvd,
        stock__offer__name="Memento",
        stock__offer__venue__name="Mnémosyne",
        dateCreated=long_ago,
        isCancelled=True,
        status=BookingStatus.CANCELLED,
        cancellationReason=BookingCancellationReasons.EXPIRED,
        user=amnesiac_user,
    )

    cd = ProductFactory(type=str(offer_type.ThingType.MUSIQUE))
    expired_today_cd_booking = BookingFactory(
        stock__offer__product=cd,
        stock__offer__name="Random Access Memories",
        stock__offer__venue__name="Virgin Megastore",
        dateCreated=long_ago,
        isCancelled=True,
        status=BookingStatus.CANCELLED,
        cancellationReason=BookingCancellationReasons.EXPIRED,
        user=amnesiac_user,
    )

    email_data = build_expired_bookings_recap_email_data_for_beneficiary(
        amnesiac_user,
        [expired_today_dvd_booking, expired_today_cd_booking],
    )

    assert email_data == {
        "Mj-TemplateID": 1951103,
        "Mj-TemplateLanguage": True,
        "Vars": {
            "user_firstName": "Dory",
            "bookings": [
                {"offer_name": "Memento", "venue_name": "Mnémosyne"},
                {"offer_name": "Random Access Memories", "venue_name": "Virgin Megastore"},
            ],
        },
    }
