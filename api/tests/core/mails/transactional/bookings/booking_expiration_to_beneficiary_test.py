from datetime import datetime
from datetime import timedelta

import pytest

from pcapi.core.bookings.factories import CancelledBookingFactory
from pcapi.core.bookings.factories import IndividualBookingFactory
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.categories import subcategories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.bookings.booking_expiration_to_beneficiary import (
    get_expired_bookings_to_beneficiary_data,
)
from pcapi.core.mails.transactional.bookings.booking_expiration_to_beneficiary import (
    send_expired_bookings_to_beneficiary_email,
)
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers.factories import ProductFactory
from pcapi.core.testing import override_features
import pcapi.core.users.factories as users_factories


@pytest.mark.usefixtures("db_session")
class SendExpiredBookingsEmailToBeneficiarySendinblueTest:
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_should_send_email_to_beneficiary_when_expired_book_booking_cancelled(self):
        amnesiac_user = users_factories.BeneficiaryGrant18Factory(email="dory@example.com")
        expired_today_book_booking = IndividualBookingFactory(
            user=amnesiac_user, stock__offer__subcategoryId=subcategories.LIVRE_PAPIER.id
        )
        send_expired_bookings_to_beneficiary_email(amnesiac_user, [expired_today_book_booking])

        assert len(mails_testing.outbox) == 1
        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.EXPIRED_BOOKING_TO_BENEFICIARY.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["params"]["WITHDRAWAL_PERIOD"] == 10

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_should_send_email_to_beneficiary_when_expired_others_bookings_cancelled(self):
        amnesiac_user = users_factories.BeneficiaryGrant18Factory(email="dory@example.com")
        expired_today_dvd_booking = IndividualBookingFactory(
            user=amnesiac_user, stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id
        )
        expired_today_cd_booking = IndividualBookingFactory(
            user=amnesiac_user, stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id
        )
        send_expired_bookings_to_beneficiary_email(amnesiac_user, [expired_today_cd_booking, expired_today_dvd_booking])

        assert len(mails_testing.outbox) == 1
        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.EXPIRED_BOOKING_TO_BENEFICIARY.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["params"]["WITHDRAWAL_PERIOD"] == 30

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_should_send_two_emails_to_beneficiary_when_expired_books_and_other_bookings_cancelled(self):
        amnesiac_user = users_factories.BeneficiaryGrant18Factory(email="dory@example.com")
        expired_today_book_booking = IndividualBookingFactory(
            user=amnesiac_user, stock__offer__subcategoryId=subcategories.LIVRE_PAPIER.id
        )
        expired_today_cd_booking = IndividualBookingFactory(
            user=amnesiac_user, stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id
        )
        send_expired_bookings_to_beneficiary_email(
            amnesiac_user, [expired_today_cd_booking, expired_today_book_booking]
        )

        assert len(mails_testing.outbox) == 2
        assert mails_testing.outbox[0].sent_data["params"]["WITHDRAWAL_PERIOD"] == 10
        assert mails_testing.outbox[1].sent_data["params"]["WITHDRAWAL_PERIOD"] == 30

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_should_get_correct_data_when_expired_bookings_cancelled(self):
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

        email_data = get_expired_bookings_to_beneficiary_data(
            amnesiac_user, [expired_today_dvd_booking, expired_today_cd_booking], 30
        )

        assert email_data.template == TransactionalEmail.EXPIRED_BOOKING_TO_BENEFICIARY.value
        assert email_data.params == {
            "FIRSTNAME": "Dory",
            "BOOKINGS": [
                {"offer_name": "Memento", "venue_name": "Mnémosyne"},
                {"offer_name": "Random Access Memories", "venue_name": "Virgin Megastore"},
            ],
            "WITHDRAWAL_PERIOD": 30,
        }


@pytest.mark.usefixtures("db_session")
class SendExpiredBookingsEmailToBeneficiaryMailjetTest:
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=False)
    def test_should_send_email_to_beneficiary_when_expired_book_booking_cancelled(self, app):
        amnesiac_user = users_factories.BeneficiaryGrant18Factory(email="dory@example.com")
        expired_today_book_booking = IndividualBookingFactory(
            user=amnesiac_user, stock__offer__subcategoryId=subcategories.LIVRE_PAPIER.id
        )
        send_expired_bookings_to_beneficiary_email(amnesiac_user, [expired_today_book_booking])

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 3095107
        assert mails_testing.outbox[0].sent_data["Vars"]["withdrawal_period"] == 10

    def test_should_send_email_to_beneficiary_when_expired_others_bookings_cancelled(self, app):
        amnesiac_user = users_factories.BeneficiaryGrant18Factory(email="dory@example.com")
        expired_today_dvd_booking = IndividualBookingFactory(
            user=amnesiac_user, stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id
        )
        expired_today_cd_booking = IndividualBookingFactory(
            user=amnesiac_user, stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id
        )
        send_expired_bookings_to_beneficiary_email(amnesiac_user, [expired_today_cd_booking, expired_today_dvd_booking])

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 3095107
        assert mails_testing.outbox[0].sent_data["Vars"]["withdrawal_period"] == 30

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=False)
    def test_should_send_two_emails_to_beneficiary_when_expired_books_and_other_bookings_cancelled(self, app):
        amnesiac_user = users_factories.BeneficiaryGrant18Factory(email="dory@example.com")
        expired_today_book_booking = IndividualBookingFactory(
            user=amnesiac_user, stock__offer__subcategoryId=subcategories.LIVRE_PAPIER.id
        )
        expired_today_cd_booking = IndividualBookingFactory(
            user=amnesiac_user, stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id
        )
        send_expired_bookings_to_beneficiary_email(
            amnesiac_user, [expired_today_cd_booking, expired_today_book_booking]
        )

        assert len(mails_testing.outbox) == 2
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 3095107
        assert mails_testing.outbox[0].sent_data["Vars"]["withdrawal_period"] == 10
        assert mails_testing.outbox[1].sent_data["Mj-TemplateID"] == 3095107
        assert mails_testing.outbox[1].sent_data["Vars"]["withdrawal_period"] == 30

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=False)
    def test_should_send_mailjet_email_to_beneficiary_when_expired_bookings_cancelled(self):
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

        email_data = get_expired_bookings_to_beneficiary_data(
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
