from datetime import datetime
from unittest.mock import patch

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize
from pcapi.utils.mailing import build_pc_pro_offer_link
from pcapi.utils.mailing import extract_users_information_from_bookings
from pcapi.utils.mailing import format_booking_date_for_email
from pcapi.utils.mailing import format_booking_hours_for_email
from pcapi.utils.mailing import make_validation_email_object


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


@pytest.mark.usefixtures("db_session")
def test_extract_users_information_from_bookings():
    # Given
    user1 = users_factories.BeneficiaryGrant18Factory(
        email="1@example.com",
        firstName="Jean",
        lastName="Dupont",
    )
    user2 = users_factories.BeneficiaryGrant18Factory(
        email="2@example.com",
        firstName="Jaja",
        lastName="Dudu",
    )
    user3 = users_factories.BeneficiaryGrant18Factory(
        email="3@example.com",
        firstName="Toto",
        lastName="Titi",
    )
    stock = offers_factories.StockFactory()
    bookings_factories.IndividualBookingFactory(
        individualBooking__user=user1,
        stock=stock,
        token="HELLO1",
    )
    bookings_factories.IndividualBookingFactory(
        individualBooking__user=user2,
        stock=stock,
        token="HELLO2",
    )
    bookings_factories.IndividualBookingFactory(
        individualBooking__user=user3,
        stock=stock,
        token="HELLO3",
    )

    # When
    users_informations = extract_users_information_from_bookings(stock.bookings)

    # Then
    assert users_informations == [
        {"firstName": "Jean", "lastName": "Dupont", "email": "1@example.com", "contremarque": "HELLO1"},
        {"firstName": "Jaja", "lastName": "Dudu", "email": "2@example.com", "contremarque": "HELLO2"},
        {"firstName": "Toto", "lastName": "Titi", "email": "3@example.com", "contremarque": "HELLO3"},
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
        assert pc_pro_url == f"http://pcpro.com/offre/{offer_id}/individuel/edition"


@pytest.mark.usefixtures("db_session")
class FormatDateAndHourForEmailTest:
    def test_should_return_formatted_event_beginningDatetime_when_offer_is_an_event(self):
        booking = bookings_factories.BookingFactory(
            stock__beginningDatetime=datetime(2019, 10, 9, 10, 20),
            stock__offer__subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id,
        )
        assert format_booking_date_for_email(booking) == "09-Oct-2019"

    def test_should_return_empty_string_when_offer_is_not_an_event(self):
        booking = bookings_factories.BookingFactory(
            stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )
        assert format_booking_date_for_email(booking) == ""


@pytest.mark.usefixtures("db_session")
class FormatBookingHoursForEmailTest:
    def test_should_return_hours_and_minutes_from_beginningDatetime_when_contains_hours(self):
        booking = bookings_factories.BookingFactory(
            stock__beginningDatetime=datetime(2019, 10, 9, 10, 20),
            stock__offer__subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id,
        )
        assert format_booking_hours_for_email(booking) == "12h20"

    def test_should_return_only_hours_from_event_beginningDatetime_when_oclock(self):
        booking = bookings_factories.BookingFactory(
            stock__beginningDatetime=datetime(2019, 10, 9, 13),
            stock__offer__subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id,
        )
        assert format_booking_hours_for_email(booking) == "15h"

    def test_should_return_empty_string_when_offer_is_not_an_event(self):
        booking = bookings_factories.BookingFactory(
            stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )
        assert format_booking_hours_for_email(booking) == ""


class MakeValidationEmailObjectTest:
    def test_should_return_subject_with_correct_departement_code(self):
        # Given
        user = users_factories.UserFactory.build()
        offerer = create_offerer(postal_code="95490")
        user_offerer = create_user_offerer(user=user, offerer=offerer)

        # When
        email_object = make_validation_email_object(
            user_offerer=user_offerer, offerer=offerer, get_by_siren=get_by_siren_stub
        )

        # Then
        assert email_object.get("Subject") == "95 - inscription / rattachement PRO à valider : Test Offerer"
