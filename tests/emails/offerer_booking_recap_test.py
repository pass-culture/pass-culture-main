from datetime import datetime
from datetime import timezone

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.factories import ActivationCodeFactory
from pcapi.core.testing import override_features
from pcapi.emails.offerer_booking_recap import retrieve_data_for_offerer_booking_recap_email
from pcapi.models.feature import FeatureToggle
from pcapi.utils.human_ids import humanize


def make_booking(**kwargs):
    attributes = dict(
        dateCreated=datetime(2019, 10, 3, 13, 24, 6, tzinfo=timezone.utc),
        token="ABC123",
        user__firstName="John",
        user__lastName="Doe",
        user__email="john@example.com",
        stock__beginningDatetime=datetime(2019, 11, 6, 14, 59, 5, tzinfo=timezone.utc),
        stock__price=10,
        stock__offer__name="Super événement",
        stock__offer__product__name="Super événement",
        stock__offer__product__subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id,
        stock__offer__venue__name="Lieu de l'offreur",
        stock__offer__venue__address="25 avenue du lieu",
        stock__offer__venue__postalCode="75010",
        stock__offer__venue__city="Paris",
        stock__offer__venue__managingOfferer__name="Théâtre du coin",
    )
    attributes.update(kwargs)
    return bookings_factories.BookingFactory(**attributes)


def get_expected_base_email_data(booking, mailjet_template_id, **overrides):
    offer_id = humanize(booking.stock.offer.id)
    email_data = {
        "MJ-TemplateID": mailjet_template_id,
        "MJ-TemplateLanguage": True,
        "Headers": {
            "Reply-To": "john@example.com",
        },
        "Vars": {
            "nom_offre": "Super événement",
            "nom_lieu": "Lieu de l'offreur",
            "prix": "10.00 €",
            "date": "06-Nov-2019",
            "heure": "15h59",
            "quantity": 1,
            "user_firstName": "John",
            "user_lastName": "Doe",
            "user_email": "john@example.com",
            "user_phoneNumber": "",
            "is_event": 1,
            "can_expire"
            if FeatureToggle.ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS.is_active()
            else "can_expire_after_30_days": 0,
            "expiration_delay": 30,
            "is_booking_autovalidated": 0,
            "contremarque": "ABC123",
            "ISBN": "",
            "lien_offre_pcpro": f"http://localhost:3001/offres/{offer_id}/edition",
            "offer_type": "EventType.SPECTACLE_VIVANT",
            "departement": "75",
            "must_use_token_for_payment": 1,
        },
    }
    email_data["Vars"].update(overrides)
    return email_data


# TODO(yacine) this test class will be removed after removing FF ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS
class OffererBookingRecapLegacyBooksBookingRulesTest:
    MAILJET_TEMPLATE_ID = 2843165

    @override_features(ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=False)
    @pytest.mark.usefixtures("db_session")
    def test_with_event(self):
        booking = make_booking()

        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        expected = get_expected_base_email_data(booking, self.MAILJET_TEMPLATE_ID)
        assert email_data == expected

    @override_features(ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=False)
    @pytest.mark.usefixtures("db_session")
    def test_with_book(self):
        booking = make_booking(
            stock__offer__name="Le récit de voyage",
            stock__offer__product__extraData={"isbn": "123456789"},
            stock__offer__product__name="Le récit de voyage",
            stock__offer__product__subcategoryId=subcategories.LIVRE_PAPIER.id,
        )

        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        expected = get_expected_base_email_data(
            booking,
            self.MAILJET_TEMPLATE_ID,
            date="",
            departement="75",
            heure="",
            is_event=0,
            nom_offre="Le récit de voyage",
            offer_type="book",
            can_expire_after_30_days=1,
        )
        assert email_data == expected

    @override_features(AUTO_ACTIVATE_DIGITAL_BOOKINGS=True, ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=False)
    @pytest.mark.usefixtures("db_session")
    def test_non_digital_bookings_can_expire_after_30_days(self):
        booking = make_booking(
            stock__offer__name="Le récit de voyage",
            stock__offer__product__extraData={"isbn": "123456789"},
            stock__offer__product__name="Le récit de voyage",
            stock__offer__product__subcategoryId=subcategories.LIVRE_PAPIER.id,
            stock__offer__venue__address=None,
            stock__offer__venue__city=None,
            stock__offer__venue__departementCode=None,
            stock__offer__venue__isVirtual=True,
            stock__offer__venue__postalCode=None,
            stock__offer__venue__siret=None,
        )

        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        expected = get_expected_base_email_data(
            booking,
            self.MAILJET_TEMPLATE_ID,
            date="",
            departement="numérique",
            heure="",
            is_event=0,
            nom_offre="Le récit de voyage",
            offer_type="book",
            can_expire_after_30_days=1,
        )
        assert email_data == expected

    @override_features(ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=False)
    @pytest.mark.usefixtures("db_session")
    def test_with_book_with_missing_isbn(self):
        booking = make_booking(
            stock__offer__name="Le récit de voyage",
            stock__offer__product__extraData={},  # no ISBN
            stock__offer__product__name="Le récit de voyage",
            stock__offer__product__subcategoryId=subcategories.LIVRE_PAPIER.id,
            stock__offer__venue__address=None,
            stock__offer__venue__city=None,
            stock__offer__venue__departementCode=None,
            stock__offer__venue__isVirtual=True,
            stock__offer__venue__postalCode=None,
            stock__offer__venue__siret=None,
        )

        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        expected = get_expected_base_email_data(
            booking,
            self.MAILJET_TEMPLATE_ID,
            date="",
            departement="numérique",
            heure="",
            is_event=0,
            nom_offre="Le récit de voyage",
            offer_type="book",
            ISBN="",
            can_expire_after_30_days=1,
        )
        assert email_data == expected

    @override_features(ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=False)
    @pytest.mark.usefixtures("db_session")
    def test_a_digital_booking_expires_after_30_days(self):
        # Given
        booking = make_booking(
            quantity=10,
            stock__price=0,
            stock__offer__product__subcategoryId=subcategories.VOD.id,
            stock__offer__product__url="http://example.com",
            stock__offer__name="Super offre numérique",
        )

        # When
        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        # Then
        expected = get_expected_base_email_data(
            booking,
            self.MAILJET_TEMPLATE_ID,
            date="",
            heure="",
            is_event=0,
            prix="Gratuit",
            nom_offre="Super offre numérique",
            offer_type="ThingType.AUDIOVISUEL",
            quantity=10,
            can_expire_after_30_days=1,
            must_use_token_for_payment=0,
        )
        assert email_data == expected

    @override_features(ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=False)
    @pytest.mark.usefixtures("db_session")
    def test_when_use_token_for_payment(self):
        # Given
        booking = make_booking(
            stock__price=10,
        )

        # When
        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        # Then
        expected = get_expected_base_email_data(booking, self.MAILJET_TEMPLATE_ID, must_use_token_for_payment=1)
        assert email_data == expected

    @override_features(ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=False)
    @pytest.mark.usefixtures("db_session")
    def test_no_need_when_price_is_free(self):
        # Given
        booking = make_booking(
            stock__price=0,
        )

        # When
        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        # Then
        expected = get_expected_base_email_data(
            booking, self.MAILJET_TEMPLATE_ID, prix="Gratuit", must_use_token_for_payment=0
        )
        assert email_data == expected

    @override_features(ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=False)
    @pytest.mark.usefixtures("db_session")
    def test_no_need_when_using_activation_code(self):
        # Given
        booking = make_booking()
        ActivationCodeFactory(stock=booking.stock, booking=booking, code="code_toto")

        # When
        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        # Then
        expected = get_expected_base_email_data(booking, self.MAILJET_TEMPLATE_ID, must_use_token_for_payment=0)
        assert email_data == expected

    @override_features(AUTO_ACTIVATE_DIGITAL_BOOKINGS=True, ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=False)
    @pytest.mark.usefixtures("db_session")
    def test_no_need_when_booking_is_autovalidated(self):
        # Given
        offer = offers_factories.OfferFactory(
            venue__name="Lieu de l'offreur",
            venue__managingOfferer__name="Théâtre du coin",
            product=offers_factories.DigitalProductFactory(name="Super événement", url="http://example.com"),
        )
        digital_stock = offers_factories.StockWithActivationCodesFactory()
        first_activation_code = digital_stock.activationCodes[0]
        booking = bookings_factories.UsedBookingFactory(
            user__email="john@example.com",
            user__firstName="John",
            user__lastName="Doe",
            stock__offer=offer,
            activationCode=first_activation_code,
            dateCreated=datetime(2018, 1, 1),
        )

        # When
        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        # Then
        expected = get_expected_base_email_data(
            booking,
            self.MAILJET_TEMPLATE_ID,
            date="",
            heure="",
            is_event=0,
            is_booking_autovalidated=1,
            must_use_token_for_payment=0,
            offer_type="ThingType.AUDIOVISUEL",
            contremarque=booking.token,
        )
        assert email_data == expected

    @override_features(AUTO_ACTIVATE_DIGITAL_BOOKINGS=True, ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=False)
    @pytest.mark.usefixtures("db_session")
    def test_a_digital_booking_with_activation_code_is_automatically_used(self):
        # Given
        offer = offers_factories.OfferFactory(
            venue__name="Lieu de l'offreur",
            venue__managingOfferer__name="Théâtre du coin",
            product=offers_factories.DigitalProductFactory(name="Super offre numérique", url="http://example.com"),
        )
        digital_stock = offers_factories.StockWithActivationCodesFactory()
        first_activation_code = digital_stock.activationCodes[0]
        booking = bookings_factories.UsedBookingFactory(
            user__email="john@example.com",
            user__firstName="John",
            user__lastName="Doe",
            stock__offer=offer,
            activationCode=first_activation_code,
            dateCreated=datetime(2018, 1, 1),
        )

        # When
        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        # Then
        expected = get_expected_base_email_data(
            booking,
            self.MAILJET_TEMPLATE_ID,
            date="",
            heure="",
            prix="10.00 €",
            is_event=0,
            nom_offre="Super offre numérique",
            offer_type="ThingType.AUDIOVISUEL",
            quantity=1,
            can_expire_after_30_days=0,
            is_booking_autovalidated=1,
            must_use_token_for_payment=0,
            contremarque=booking.token,
        )
        assert email_data == expected

    @override_features(ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=False)
    @pytest.mark.usefixtures("db_session")
    def test_should_not_truncate_price(self):
        booking = make_booking(stock__price=5.86)

        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        expected = get_expected_base_email_data(booking, self.MAILJET_TEMPLATE_ID, prix="5.86 €")
        assert email_data == expected

    @override_features(ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=False)
    @pytest.mark.usefixtures("db_session")
    def test_should_use_venue_public_name_when_available(self):
        booking = make_booking(
            stock__offer__venue__name="Legal name",
            stock__offer__venue__publicName="Public name",
        )

        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        expected = get_expected_base_email_data(booking, self.MAILJET_TEMPLATE_ID, nom_lieu="Public name")
        assert email_data == expected

    @override_features(ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=False)
    @pytest.mark.usefixtures("db_session")
    def test_should_add_user_phone_number_to_vars(self):
        # given
        booking = make_booking(user__phoneNumber="0123456789")

        # when
        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        # then
        template_vars = email_data["Vars"]
        assert template_vars["user_phoneNumber"] == "0123456789"

    @override_features(ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=False)
    @pytest.mark.usefixtures("db_session")
    def test_should_add_reply_to_header_with_beneficiary_email(self):
        # given
        booking = make_booking(user__email="beneficiary@example.com")

        # when
        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        # then
        template_headers = email_data["Headers"]
        assert template_headers["Reply-To"] == "beneficiary@example.com"


class OffererBookingRecapNewBooksBookingRulesTest:
    MAILJET_TEMPLATE_ID = 3095147

    @override_features(ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=True)
    @pytest.mark.usefixtures("db_session")
    def test_with_event(self):
        booking = make_booking()

        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        expected = get_expected_base_email_data(booking, self.MAILJET_TEMPLATE_ID)
        assert email_data == expected

    @override_features(ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=True)
    @pytest.mark.usefixtures("db_session")
    def test_with_book(self):
        booking = make_booking(
            stock__offer__name="Le récit de voyage",
            stock__offer__product__extraData={"isbn": "123456789"},
            stock__offer__product__name="Le récit de voyage",
            stock__offer__product__subcategoryId=subcategories.LIVRE_PAPIER.id,
        )

        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        expected = get_expected_base_email_data(
            booking,
            self.MAILJET_TEMPLATE_ID,
            date="",
            departement="75",
            heure="",
            is_event=0,
            nom_offre="Le récit de voyage",
            offer_type="book",
            can_expire=1,
            expiration_delay=10,
        )
        assert email_data == expected

    @override_features(AUTO_ACTIVATE_DIGITAL_BOOKINGS=True, ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=True)
    @pytest.mark.usefixtures("db_session")
    def test_non_digital_bookings_can_expire_after_30_days(self):
        booking = make_booking(
            stock__offer__name="Le récit de voyage",
            stock__offer__product__extraData={"isbn": "123456789"},
            stock__offer__product__name="Le récit de voyage",
            stock__offer__product__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            stock__offer__venue__address=None,
            stock__offer__venue__city=None,
            stock__offer__venue__departementCode=None,
            stock__offer__venue__isVirtual=True,
            stock__offer__venue__postalCode=None,
            stock__offer__venue__siret=None,
        )

        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        expected = get_expected_base_email_data(
            booking,
            self.MAILJET_TEMPLATE_ID,
            date="",
            departement="numérique",
            heure="",
            is_event=0,
            nom_offre="Le récit de voyage",
            offer_type="ThingType.AUDIOVISUEL",
            can_expire=1,
        )
        assert email_data == expected

    @override_features(ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=True)
    @pytest.mark.usefixtures("db_session")
    def test_with_book_with_missing_isbn(self):
        booking = make_booking(
            stock__offer__name="Le récit de voyage",
            stock__offer__product__extraData={},  # no ISBN
            stock__offer__product__name="Le récit de voyage",
            stock__offer__product__subcategoryId=subcategories.LIVRE_PAPIER.id,
            stock__offer__venue__address=None,
            stock__offer__venue__city=None,
            stock__offer__venue__departementCode=None,
            stock__offer__venue__isVirtual=True,
            stock__offer__venue__postalCode=None,
            stock__offer__venue__siret=None,
        )

        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        expected = get_expected_base_email_data(
            booking,
            self.MAILJET_TEMPLATE_ID,
            date="",
            departement="numérique",
            heure="",
            is_event=0,
            nom_offre="Le récit de voyage",
            offer_type="book",
            ISBN="",
            can_expire=1,
            expiration_delay=10,
        )
        assert email_data == expected

    @override_features(ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=True)
    @pytest.mark.usefixtures("db_session")
    def test_a_digital_booking_expires_after_30_days(self):
        # Given
        booking = make_booking(
            quantity=10,
            stock__price=0,
            stock__offer__product__subcategoryId=subcategories.VOD.id,
            stock__offer__product__url="http://example.com",
            stock__offer__name="Super offre numérique",
        )

        # When
        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        # Then
        expected = get_expected_base_email_data(
            booking,
            self.MAILJET_TEMPLATE_ID,
            date="",
            heure="",
            is_event=0,
            prix="Gratuit",
            nom_offre="Super offre numérique",
            offer_type="ThingType.AUDIOVISUEL",
            quantity=10,
            can_expire=1,
            must_use_token_for_payment=0,
        )
        assert email_data == expected

    @override_features(ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=True)
    @pytest.mark.usefixtures("db_session")
    def test_when_use_token_for_payment(self):
        # Given
        booking = make_booking(
            stock__price=10,
        )

        # When
        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        # Then
        expected = get_expected_base_email_data(booking, self.MAILJET_TEMPLATE_ID, must_use_token_for_payment=1)
        assert email_data == expected

    @override_features(ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=True)
    @pytest.mark.usefixtures("db_session")
    def test_no_need_when_price_is_free(self):
        # Given
        booking = make_booking(
            stock__price=0,
        )

        # When
        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        # Then
        expected = get_expected_base_email_data(
            booking, self.MAILJET_TEMPLATE_ID, prix="Gratuit", must_use_token_for_payment=0
        )
        assert email_data == expected

    @override_features(ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=True)
    @pytest.mark.usefixtures("db_session")
    def test_no_need_when_using_activation_code(self):
        # Given
        booking = make_booking()
        ActivationCodeFactory(stock=booking.stock, booking=booking, code="code_toto")

        # When
        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        # Then
        expected = get_expected_base_email_data(booking, self.MAILJET_TEMPLATE_ID, must_use_token_for_payment=0)
        assert email_data == expected

    @override_features(AUTO_ACTIVATE_DIGITAL_BOOKINGS=True, ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=True)
    @pytest.mark.usefixtures("db_session")
    def test_no_need_when_booking_is_autovalidated(self):
        # Given
        offer = offers_factories.OfferFactory(
            venue__name="Lieu de l'offreur",
            venue__managingOfferer__name="Théâtre du coin",
            product=offers_factories.DigitalProductFactory(name="Super événement", url="http://example.com"),
        )
        digital_stock = offers_factories.StockWithActivationCodesFactory()
        first_activation_code = digital_stock.activationCodes[0]
        booking = bookings_factories.UsedBookingFactory(
            user__email="john@example.com",
            user__firstName="John",
            user__lastName="Doe",
            stock__offer=offer,
            activationCode=first_activation_code,
            dateCreated=datetime(2018, 1, 1),
        )

        # When
        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        # Then
        expected = get_expected_base_email_data(
            booking,
            self.MAILJET_TEMPLATE_ID,
            date="",
            heure="",
            is_event=0,
            is_booking_autovalidated=1,
            must_use_token_for_payment=0,
            offer_type="ThingType.AUDIOVISUEL",
            contremarque=booking.token,
        )
        assert email_data == expected

    @override_features(AUTO_ACTIVATE_DIGITAL_BOOKINGS=True, ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=True)
    @pytest.mark.usefixtures("db_session")
    def test_a_digital_booking_with_activation_code_is_automatically_used(self):
        # Given
        offer = offers_factories.OfferFactory(
            venue__name="Lieu de l'offreur",
            venue__managingOfferer__name="Théâtre du coin",
            product=offers_factories.DigitalProductFactory(name="Super offre numérique", url="http://example.com"),
        )
        digital_stock = offers_factories.StockWithActivationCodesFactory()
        first_activation_code = digital_stock.activationCodes[0]
        booking = bookings_factories.UsedBookingFactory(
            user__email="john@example.com",
            user__firstName="John",
            user__lastName="Doe",
            stock__offer=offer,
            activationCode=first_activation_code,
            dateCreated=datetime(2018, 1, 1),
        )

        # When
        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        # Then
        expected = get_expected_base_email_data(
            booking,
            self.MAILJET_TEMPLATE_ID,
            date="",
            heure="",
            prix="10.00 €",
            is_event=0,
            nom_offre="Super offre numérique",
            offer_type="ThingType.AUDIOVISUEL",
            quantity=1,
            can_expire=0,
            is_booking_autovalidated=1,
            must_use_token_for_payment=0,
            contremarque=booking.token,
        )
        assert email_data == expected

    @override_features(ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=True)
    @pytest.mark.usefixtures("db_session")
    def test_should_not_truncate_price(self):
        booking = make_booking(stock__price=5.86)

        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        expected = get_expected_base_email_data(booking, self.MAILJET_TEMPLATE_ID, prix="5.86 €")
        assert email_data == expected

    @override_features(ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=True)
    @pytest.mark.usefixtures("db_session")
    def test_should_use_venue_public_name_when_available(self):
        booking = make_booking(
            stock__offer__venue__name="Legal name",
            stock__offer__venue__publicName="Public name",
        )

        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        expected = get_expected_base_email_data(booking, self.MAILJET_TEMPLATE_ID, nom_lieu="Public name")
        assert email_data == expected

    @override_features(ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=True)
    @pytest.mark.usefixtures("db_session")
    def test_should_add_user_phone_number_to_vars(self):
        # given
        booking = make_booking(user__phoneNumber="0123456789")

        # when
        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        # then
        template_vars = email_data["Vars"]
        assert template_vars["user_phoneNumber"] == "0123456789"

    @override_features(ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS=True)
    @pytest.mark.usefixtures("db_session")
    def test_should_add_reply_to_header_with_beneficiary_email(self):
        # given
        booking = make_booking(user__email="beneficiary@example.com")

        # when
        email_data = retrieve_data_for_offerer_booking_recap_email(booking)

        # then
        template_headers = email_data["Headers"]
        assert template_headers["Reply-To"] == "beneficiary@example.com"
