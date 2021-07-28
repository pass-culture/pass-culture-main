from datetime import datetime
from unittest.mock import patch

from pcapi.core.users import factories as users_factories
from pcapi.emails.offerer_bookings_recap_after_deleting_stock import (
    retrieve_offerer_bookings_recap_email_data_after_offerer_cancellation,
)
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_product_with_thing_type
from pcapi.model_creators.specific_creators import create_stock_from_offer


class RetrieveOffererBookingsRecapEmailDataAfterOffererCancellationTest:
    @patch(
        "pcapi.emails.offerer_bookings_recap_after_deleting_stock.build_pc_pro_offer_link",
        return_value="http://pc_pro.com/offer_link",
    )
    def test_should_return_mailjet_data_with_correct_information_when_offer_is_an_event(self, build_pc_pro_offer_link):
        # Given
        beneficiary = users_factories.BeneficiaryFactory.build(
            publicName="John Doe", firstName="John", lastName="Doe", email="john@example.com"
        )
        offerer = create_offerer()
        venue = create_venue(offerer, name="Venue name")
        offer = create_offer_with_event_product(venue, event_name="My Event")
        stock = create_stock_from_offer(offer, price=12.52, beginning_datetime=datetime(2019, 10, 9, 10, 20, 00))
        booking = create_booking(beneficiary, stock=stock, venue=venue, quantity=2, token="12345")
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
        beneficiary = users_factories.BeneficiaryFactory.build(
            publicName="John Doe", firstName="John", lastName="Doe", email="john@example.com"
        )
        offerer = create_offerer()
        venue = create_venue(offerer, name="La petite librairie", public_name="La grande librairie")
        thing_product = create_product_with_thing_type(thing_name="Le récit de voyage")
        offer = create_offer_with_thing_product(venue=venue, product=thing_product)
        stock = create_stock_from_offer(offer, price=0)
        booking = create_booking(user=beneficiary, stock=stock, token="12346", quantity=6)

        other_beneficiary = users_factories.BeneficiaryFactory.build(
            publicName="James Bond", firstName="James", lastName="Bond", email="bond@example.com"
        )
        booking2 = create_booking(user=other_beneficiary, stock=stock, token="12345")
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
