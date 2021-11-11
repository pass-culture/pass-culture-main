from datetime import date
from datetime import timedelta
from unittest import mock

import pytest

from pcapi.core.bookings.factories import EducationalBookingFactory
from pcapi.core.bookings.factories import IndividualBookingFactory
from pcapi.core.categories import subcategories
from pcapi.core.offers.factories import ProductFactory
from pcapi.repository import repository
from pcapi.scripts.booking.notify_soon_to_be_expired_bookings import (
    notify_users_of_soon_to_be_expired_individual_bookings,
)


@pytest.mark.usefixtures("db_session")
class NotifyUsersOfSoonToBeExpiredBookingsTest:
    @mock.patch(
        "pcapi.scripts.booking.notify_soon_to_be_expired_bookings.send_soon_to_be_expired_individual_bookings_recap_email_to_beneficiary"
    )
    def should_call_email_service_for_individual_bookings_which_will_expire_in_7_days(
        self, mocked_email_recap, app
    ) -> None:
        # Given
        now = date.today()
        booking_date_23_days_ago = now - timedelta(days=23)
        booking_date_22_days_ago = now - timedelta(days=22)

        dvd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id)
        expire_in_7_days_dvd_individual_booking = IndividualBookingFactory(
            stock__offer__product=dvd,
            dateCreated=booking_date_23_days_ago,
            isCancelled=False,
        )
        non_expired_cd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id)
        dont_expire_in_7_days_cd_individual_booking = IndividualBookingFactory(
            stock__offer__product=non_expired_cd,
            dateCreated=booking_date_22_days_ago,
            isCancelled=False,
        )
        repository.save(dont_expire_in_7_days_cd_individual_booking)

        # When
        notify_users_of_soon_to_be_expired_individual_bookings()

        # Then
        mocked_email_recap.assert_called_once_with(
            expire_in_7_days_dvd_individual_booking.individualBooking.user, [expire_in_7_days_dvd_individual_booking]
        )

    @mock.patch(
        "pcapi.scripts.booking.notify_soon_to_be_expired_bookings.send_soon_to_be_expired_individual_bookings_recap_email_to_beneficiary"
    )
    def should_not_call_email_service_for_educational_bookings_which_will_expire_in_7_days(
        self, mocked_email_recap, app
    ) -> None:
        """
        No email should be sent to educational booking users.
        As of september 2021, EAC offers are only of event type so not concerned
        with expiring bookings. But in case an EAC offer becomes compatible with thing type offers
        We want a test to cover this behavior
        """
        # Given
        now = date.today()
        booking_date_23_days_ago = now - timedelta(days=23)

        dvd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id)
        EducationalBookingFactory(
            stock__offer__product=dvd,
            dateCreated=booking_date_23_days_ago,
            isCancelled=False,
        )

        # When
        notify_users_of_soon_to_be_expired_individual_bookings()

        # Then
        assert not mocked_email_recap.called
