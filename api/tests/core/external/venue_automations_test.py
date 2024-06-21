from datetime import datetime
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
import pytest
from sib_api_v3_sdk import RequestContactImport

from pcapi import settings
import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.external.automations import venue as venue_automations
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
from pcapi.models.offer_mixin import OfferValidationStatus


@pytest.mark.usefixtures("db_session")
class VenueAutomationsTest:
    def test_get_inactive_venues_emails(self):
        date_92_days_ago = datetime.utcnow() - relativedelta(days=92)
        date_70_days_ago = datetime.utcnow() - relativedelta(days=70)

        offerer_validated_92_days_ago = offerers_factories.OffererFactory(dateValidated=date_92_days_ago)

        venue_no_booking = offerers_factories.VenueFactory(
            managingOfferer=offerer_validated_92_days_ago, bookingEmail="no_booking@example.com"
        )
        offers_factories.ThingStockFactory(
            offer=offers_factories.ThingOfferFactory(venue=venue_no_booking, validation=OfferValidationStatus.APPROVED)
        )

        # excluded because parent offerer has been validated less than 90 days ago:
        offerer_validated_70_days_ago = offerers_factories.OffererFactory(dateValidated=date_70_days_ago)
        venue_validated_70_days_ago = offerers_factories.VenueFactory(
            managingOfferer=offerer_validated_70_days_ago, bookingEmail="validated_70_days_ago@example.com"
        )
        offers_factories.ThingOfferFactory(venue=venue_validated_70_days_ago, validation=OfferValidationStatus.APPROVED)

        # excluded because of venue type:
        venue_festival = offerers_factories.VenueFactory(
            managingOfferer=offerer_validated_92_days_ago,
            venueTypeCode=offerers_models.VenueTypeCode.FESTIVAL,
            bookingEmail="venue_type_festival@example.com",
        )
        offers_factories.EventOfferFactory(venue=venue_festival, validation=OfferValidationStatus.APPROVED)

        venue_digital = offerers_factories.VirtualVenueFactory(
            managingOfferer=offerer_validated_92_days_ago,
            venueTypeCode=offerers_models.VenueTypeCode.DIGITAL,
            bookingEmail="venue_type_digital@example.com",
        )
        offers_factories.EventOfferFactory(venue=venue_digital, validation=OfferValidationStatus.APPROVED)

        # excluded because venue does not have approved offer:
        venue_no_approved_offer = offerers_factories.VenueFactory(
            managingOfferer=offerer_validated_92_days_ago, bookingEmail="no_approved_offer@example.com"
        )
        offers_factories.ThingOfferFactory(venue=venue_no_approved_offer, validation=OfferValidationStatus.DRAFT)

        # excluded because venue does not have offer at all:
        offerers_factories.VenueFactory(
            managingOfferer=offerer_validated_92_days_ago, bookingEmail="no_offer@example.com"
        )

        # matching because booking has more than 3 months:
        venue_old_booking = offerers_factories.VenueFactory(
            managingOfferer=offerer_validated_92_days_ago, bookingEmail="old_booking@example.com"
        )
        bookings_factories.BookingFactory(
            dateCreated=date_92_days_ago,
            stock=offers_factories.ThingStockFactory(
                offer=offers_factories.ThingOfferFactory(
                    venue=venue_old_booking, validation=OfferValidationStatus.APPROVED
                )
            ),
        )

        # excluded because offer has been booked less than 3 months ago
        venue_has_booking = offerers_factories.VenueFactory(
            managingOfferer=offerer_validated_92_days_ago, bookingEmail="has_booking@example.com"
        )
        bookings_factories.BookingFactory(
            stock=offers_factories.ThingStockFactory(
                offer=offers_factories.ThingOfferFactory(
                    venue=venue_has_booking, validation=OfferValidationStatus.APPROVED
                )
            ),
            dateCreated=date_70_days_ago,
        )

        results = venue_automations.get_inactive_venues_emails()

        assert set(results) == {venue_no_booking.bookingEmail, venue_old_booking.bookingEmail}

    @patch("pcapi.core.external.sendinblue.sib_api_v3_sdk.api.contacts_api.ContactsApi.import_contacts")
    def test_pro_inactive_venues_automation(self, mock_import_contacts):
        offerer = offerers_factories.OffererFactory(dateValidated=datetime.utcnow() - relativedelta(days=100))
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offers_factories.EventOfferFactory(venue=venue, validation=OfferValidationStatus.APPROVED)

        result = venue_automations.pro_inactive_venues_automation()

        mock_import_contacts.assert_called_once_with(
            RequestContactImport(
                file_url=None,
                file_body=f"EMAIL\n{venue.bookingEmail}",
                list_ids=[settings.SENDINBLUE_PRO_INACTIVE_90_DAYS_ID],
                notify_url=f"{settings.API_URL}/webhooks/sendinblue/importcontacts/{settings.SENDINBLUE_PRO_INACTIVE_90_DAYS_ID}/1",
                new_list=None,
                email_blacklist=False,
                sms_blacklist=False,
                update_existing_contacts=True,
                empty_contacts_attributes=False,
            )
        )

        assert result is True
