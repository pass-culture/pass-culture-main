from datetime import datetime

from pcapi.core.users import factories as users_factories
from pcapi.emails.user_notification_after_stock_update import (
    retrieve_data_to_warn_user_after_stock_update_affecting_booking,
)
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product


class RetrieveDataToWarnUserAfterStockUpdateAffectingBookingTest:
    def test_should_send_email_when_stock_date_have_been_changed(self):
        # Given
        beginning_datetime = datetime(2019, 7, 20, 12, 0, 0)
        new_beginning_datetime = datetime(2019, 8, 20, 12, 0, 0)

        beneficiary = users_factories.BeneficiaryFactory.build()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue, event_name="Offer name")
        stock = create_stock(beginning_datetime=beginning_datetime, offer=offer, price=20)
        booking = create_booking(user=beneficiary, stock=stock)

        stock.beginningDatetime = new_beginning_datetime

        # When
        booking_info_for_mailjet = retrieve_data_to_warn_user_after_stock_update_affecting_booking(booking)

        # Then
        assert booking_info_for_mailjet == {
            "MJ-TemplateID": 1332139,
            "MJ-TemplateLanguage": True,
            "Vars": {
                "offer_name": booking.stock.offer.name,
                "user_first_name": beneficiary.firstName,
                "venue_name": booking.stock.offer.venue.name,
                "event_date": "mardi 20 août 2019",
                "event_hour": "14h",
            },
        }
