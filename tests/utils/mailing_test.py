from datetime import datetime
from datetime import timezone
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from pcapi.core.categories import subcategories
from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_stock_from_offer
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize
from pcapi.utils.mailing import build_pc_pro_offer_link
from pcapi.utils.mailing import extract_users_information_from_bookings
from pcapi.utils.mailing import format_booking_date_for_email
from pcapi.utils.mailing import format_booking_hours_for_email
from pcapi.utils.mailing import make_validation_email_object

from tests.files.api_entreprise import MOCKED_SIREN_ENTREPRISES_API_RETURN


def get_mocked_response_status_200(entity):
    response = MagicMock(status_code=200, text="")
    response.json = MagicMock(return_value=MOCKED_SIREN_ENTREPRISES_API_RETURN)
    return response


def get_by_siren_stub(offerer):
    return {
        "unite_legale": {
            "siren": "395251440",
            "etablissement_siege": {
                "siren": "395251440",
                "siret": "39525144000016",
                "etablissement_siege": "true",
            },
            "activite_principale": "59.14Z",
        },
        "other_etablissements_sirets": ["39525144000032", "39525144000065"],
    }


class GetUsersInformationFromStockBookingsTest:
    def test_returns_correct_users_information_from_bookings_stock(self):
        # Given
        user_1 = users_factories.BeneficiaryGrant18Factory.build(
            departementCode="93",
            email="test@example.com",
            firstName="Jean",
            lastName="Dupont",
            publicName="Test",
        )
        user_2 = users_factories.BeneficiaryGrant18Factory.build(
            departementCode="93",
            email="mail@example.com",
            firstName="Jaja",
            lastName="Dudu",
            publicName="Test",
        )
        user_3 = users_factories.BeneficiaryGrant18Factory.build(
            departementCode="93",
            email="mail@example.com",
            firstName="Toto",
            lastName="Titi",
            publicName="Test",
        )
        offerer = create_offerer()
        venue = create_venue(
            offerer=offerer, name="Test offerer", booking_email="reservations@test.fr", is_virtual=True, siret=None
        )
        thing_offer = create_offer_with_thing_product(venue, thing_subcategory_id=subcategories.LIVRE_NUMERIQUE.id)
        beginning_datetime = datetime(2019, 11, 6, 14, 00, 0, tzinfo=timezone.utc)
        stock = create_stock_from_offer(thing_offer, price=0, quantity=10, beginning_datetime=beginning_datetime)
        booking_1 = create_booking(user=user_1, stock=stock, venue=venue, token="HELLO0")
        booking_2 = create_booking(user=user_2, stock=stock, venue=venue, token="HELLO1")
        booking_3 = create_booking(user=user_3, stock=stock, venue=venue, token="HELLO2")

        stock.bookings = [booking_1, booking_2, booking_3]

        # When
        users_informations = extract_users_information_from_bookings(stock.bookings)

        # Then
        assert users_informations == [
            {"firstName": "Jean", "lastName": "Dupont", "email": "test@example.com", "contremarque": "HELLO0"},
            {"firstName": "Jaja", "lastName": "Dudu", "email": "mail@example.com", "contremarque": "HELLO1"},
            {"firstName": "Toto", "lastName": "Titi", "email": "mail@example.com", "contremarque": "HELLO2"},
        ]


class BuildPcProOfferLinkTest:
    @patch("pcapi.settings.PRO_URL", "http://pcpro.com")
    @pytest.mark.usefixtures("db_session")
    def test_should_return_pc_pro_offer_link(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        repository.save(offer)
        offer_id = humanize(offer.id)

        # When
        pc_pro_url = build_pc_pro_offer_link(offer)

        # Then
        assert pc_pro_url == f"http://pcpro.com/offres/{offer_id}/edition"


class FormatDateAndHourForEmailTest:
    def test_should_return_formatted_event_beginningDatetime_when_offer_is_an_event(self):
        # Given
        user = users_factories.UserFactory.build()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock_from_offer(offer, beginning_datetime=datetime(2019, 10, 9, 10, 20, 00))
        booking = create_booking(user=user, stock=stock)

        # When
        formatted_date = format_booking_date_for_email(booking)

        # Then
        assert formatted_date == "09-Oct-2019"

    def test_should_return_empty_string_when_offer_is_not_an_event(self):
        # Given
        user = users_factories.UserFactory.build()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_from_offer(offer, beginning_datetime=None)
        booking = create_booking(user=user, stock=stock)

        # When
        formatted_date = format_booking_date_for_email(booking)

        # Then
        assert formatted_date == ""


class FormatBookingHoursForEmailTest:
    def test_should_return_hours_and_minutes_from_beginningDatetime_when_contains_hours(self):
        # Given
        user = users_factories.UserFactory.build()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock_from_offer(offer, beginning_datetime=datetime(2019, 10, 9, 10, 20, 00))
        booking = create_booking(user=user, stock=stock)

        # When
        formatted_date = format_booking_hours_for_email(booking)

        # Then
        assert formatted_date == "12h20"

    def test_should_return_only_hours_from_event_beginningDatetime_when_oclock(self):
        # Given
        user = users_factories.UserFactory.build()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock_from_offer(offer, beginning_datetime=datetime(2019, 10, 9, 13, 00, 00))
        booking = create_booking(user=user, stock=stock)

        # When
        formatted_date = format_booking_hours_for_email(booking)

        # Then
        assert formatted_date == "15h"

    def test_should_return_empty_string_when_offer_is_not_an_event(self):
        # Given
        user = users_factories.UserFactory.build()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_from_offer(offer)
        booking = create_booking(user=user, stock=stock)

        # When
        formatted_date = format_booking_hours_for_email(booking)

        # Then
        assert formatted_date == ""


class MakeValidationEmailObjectTest:
    def test_should_return_subject_with_correct_departement_code(self):
        # Given
        user = users_factories.UserFactory.build(departementCode="93")
        offerer = create_offerer(postal_code="95490")
        user_offerer = create_user_offerer(user=user, offerer=offerer)

        # When
        email_object = make_validation_email_object(
            user_offerer=user_offerer, offerer=offerer, get_by_siren=get_by_siren_stub
        )

        # Then
        assert email_object.get("Subject") == "95 - inscription / rattachement PRO à valider : Test Offerer"
