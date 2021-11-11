from datetime import datetime
from unittest.mock import patch

import pytest

from pcapi.core.bookings import factories as booking_factories
from pcapi.core.offers import factories as offer_factories
from pcapi.core.users import factories as users_factories
from pcapi.emails.offerer_bookings_recap_after_deleting_stock import (
    retrieve_offerer_bookings_recap_email_data_after_offerer_cancellation,
)


@pytest.mark.usefixtures("db_session")
class RetrieveOffererBookingsRecapEmailDataAfterOffererCancellationTest:
    @patch(
        "pcapi.emails.offerer_bookings_recap_after_deleting_stock.build_pc_pro_offer_link",
        return_value="http://pc_pro.com/offer_link",
    )
    def test_should_return_mailjet_data_with_correct_information_when_offer_is_an_event(self, build_pc_pro_offer_link):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            publicName="John Doe", firstName="John", lastName="Doe", email="john@example.com"
        )
        offer = offer_factories.EventOfferFactory(
            venue__name="Venue name",
            product__name="My Event",
        )
        booking = booking_factories.IndividualBookingFactory(
            user=beneficiary,
            individualBooking__user=beneficiary,
            stock__offer=offer,
            stock__beginningDatetime=datetime(2019, 10, 9, 10, 20, 00),
            stock__price=12.52,
            quantity=2,
            token="12345",
        )
        bookings = [booking]

        # When
        mailjet_data = retrieve_offerer_bookings_recap_email_data_after_offerer_cancellation(bookings)

        # Then
        assert mailjet_data == {
            "MJ-TemplateID": 1116333,
            "MJ-TemplateLanguage": True,
            "Vars": {
                "offer_name": "My Event",
                "lien_offre_pcpro": "http://pc_pro.com/offer_link",
                "venue_name": "Venue name",
                "price": "12.52",
                "is_event": 1,
                "event_date": "09-Oct-2019",
                "event_hour": "12h20",
                "quantity": 2,
                "reservations_number": 1,
                "users": [
                    {"countermark": "12345", "email": "john@example.com", "firstName": "John", "lastName": "Doe"}
                ],
            },
        }

    @patch(
        "pcapi.emails.offerer_bookings_recap_after_deleting_stock.build_pc_pro_offer_link",
        return_value="http://pc_pro.com/offer_link",
    )
    def test_should_return_mailjet_data_when_multiple_bookings_and_offer_is_a_thing(self, build_pc_pro_offer_link):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            publicName="John Doe", firstName="John", lastName="Doe", email="john@example.com"
        )
        offer = offer_factories.ThingOfferFactory(
            venue__name="La petite librairie",
            venue__publicName="La grande librairie",
            product__name="Le récit de voyage",
        )
        booking = booking_factories.IndividualBookingFactory(
            user=beneficiary,
            individualBooking__user=beneficiary,
            stock__offer=offer,
            stock__price=0,
            token="12346",
            quantity=6,
        )

        other_beneficiary = users_factories.BeneficiaryGrant18Factory(
            publicName="James Bond", firstName="James", lastName="Bond", email="bond@example.com"
        )
        booking2 = booking_factories.IndividualBookingFactory(
            user=other_beneficiary,
            individualBooking__user=other_beneficiary,
            stock__offer=offer,
            stock__price=0,
            token="12345",
            quantity=1,
        )
        bookings = [booking, booking2]

        # When
        mailjet_data = retrieve_offerer_bookings_recap_email_data_after_offerer_cancellation(bookings)

        # Then
        assert mailjet_data == {
            "MJ-TemplateID": 1116333,
            "MJ-TemplateLanguage": True,
            "Vars": {
                "offer_name": "Le récit de voyage",
                "lien_offre_pcpro": "http://pc_pro.com/offer_link",
                "venue_name": "La grande librairie",
                "price": "Gratuit",
                "is_event": 0,
                "event_date": "",
                "event_hour": "",
                "quantity": 7,
                "reservations_number": 2,
                "users": [
                    {"countermark": "12346", "email": "john@example.com", "firstName": "John", "lastName": "Doe"},
                    {"countermark": "12345", "email": "bond@example.com", "firstName": "James", "lastName": "Bond"},
                ],
            },
        }
