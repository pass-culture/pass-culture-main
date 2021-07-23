from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories
from pcapi.core.offers.factories import OffererFactory
from pcapi.core.offers.factories import ProductFactory
from pcapi.emails.offerer_expired_bookings import build_expired_bookings_recap_email_data_for_offerer


@pytest.mark.usefixtures("db_session")
@patch(
    "pcapi.emails.offerer_expired_bookings.build_pc_pro_offer_link",
    return_value="http://pc_pro.com/offer_link",
)
def test_should_send_email_to_offerer_when_expired_bookings_cancelled(self, app):
    now = datetime.utcnow()
    offerer = OffererFactory()
    long_ago = now - timedelta(days=31)
    dvd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id)
    expired_today_dvd_booking = BookingFactory(
        user__publicName="Dory",
        user__email="dory@example.com",
        stock__offer__product=dvd,
        stock__offer__name="Memento",
        stock__offer__venue__name="Mnémosyne",
        stock__offer__venue__managingOfferer=offerer,
        dateCreated=long_ago,
        isCancelled=True,
        status=BookingStatus.CANCELLED,
        cancellationReason=BookingCancellationReasons.EXPIRED,
    )

    cd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id)
    expired_today_cd_booking = BookingFactory(
        user__publicName="Dorian",
        user__email="dorian@example.com",
        stock__offer__product=cd,
        stock__offer__name="Random Access Memories",
        stock__offer__venue__name="Virgin Megastore",
        stock__offer__venue__managingOfferer=offerer,
        dateCreated=long_ago,
        isCancelled=True,
        status=BookingStatus.CANCELLED,
        cancellationReason=BookingCancellationReasons.EXPIRED,
    )

    email_data = build_expired_bookings_recap_email_data_for_offerer(
        offerer,
        [expired_today_dvd_booking, expired_today_cd_booking],
    )

    assert email_data == {
        "Mj-TemplateID": 1952508,
        "Mj-TemplateLanguage": True,
        "Vars": {
            "bookings": [
                {
                    "offer_name": "Memento",
                    "venue_name": "Mnémosyne",
                    "price": "10.00",
                    "user_name": "Dory",
                    "user_email": "dory@example.com",
                    "pcpro_offer_link": "http://pc_pro.com/offer_link",
                },
                {
                    "offer_name": "Random Access Memories",
                    "venue_name": "Virgin Megastore",
                    "price": "10.00",
                    "user_name": "Dorian",
                    "user_email": "dorian@example.com",
                    "pcpro_offer_link": "http://pc_pro.com/offer_link",
                },
            ],
            "department": "75",
        },
    }
