from datetime import datetime
from datetime import timedelta

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories
import pcapi.core.educational.factories as educational_factories
from pcapi.core.educational.models import EducationalBookingStatus
from pcapi.core.offerers.factories import ApiKeyFactory
import pcapi.core.offers.factories as offers_factories
import pcapi.core.payments.factories as payments_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    def test_when_user_has_rights_and_regular_offer(self, client):
        # Given
        past = datetime.now() - timedelta(days=2)
        booking = bookings_factories.IndividualBookingFactory(
            individualBooking__user__email="beneficiary@example.com",
            stock__beginningDatetime=past,
            stock__offer=offers_factories.EventOfferFactory(
                extraData={
                    "theater": {
                        "allocine_movie_id": 165,
                        "allocine_room_id": 987,
                    },
                },
                subcategoryId=subcategories.CARTE_CINE_MULTISEANCES.id,
                product__name="An offer you cannot refuse",
                venue__name="Le Petit Rintintin",
            ),
        )
        user_offerer = offers_factories.UserOffererFactory(offerer=booking.offerer)
        pro_user = user_offerer.user

        # When
        client = client.with_basic_auth(pro_user.email)
        response = client.get(f"/v2/bookings/token/{booking.token}")

        # Then
        assert response.headers["Content-type"] == "application/json"
        assert response.status_code == 200
        assert response.json == {
            "bookingId": humanize(booking.id),
            "dateOfBirth": "",
            "datetime": format_into_utc_date(booking.stock.beginningDatetime),
            "ean13": None,
            "email": "beneficiary@example.com",
            "formula": "ABO",
            "isUsed": False,
            "offerId": booking.stock.offerId,
            "offerName": "An offer you cannot refuse",
            "offerType": "EVENEMENT",
            "phoneNumber": "",
            "price": 10.0,
            "publicOfferId": humanize(booking.stock.offerId),
            "quantity": 1,
            "theater": {
                "allocine_movie_id": 165,
                "allocine_room_id": 987,
            },
            "userName": "Jeanne Doux",
            "venueAddress": "1 boulevard Poissonnière",
            "venueDepartmentCode": "75",
            "venueName": "Le Petit Rintintin",
        }

    def test_when_user_has_rights_and_booking_is_educational_validated_by_principal(self, client):
        # Given
        redactor = educational_factories.EducationalRedactorFactory(
            civility="M.",
            firstName="Jean",
            lastName="Doudou",
            email="jean.doux@example.com",
        )
        validated_eac_booking = bookings_factories.EducationalBookingFactory(
            dateCreated=datetime.utcnow() - timedelta(days=5),
            educationalBooking__educationalRedactor=redactor,
            educationalBooking__status=EducationalBookingStatus.USED_BY_INSTITUTE,
        )
        pro_user = users_factories.ProFactory()
        offers_factories.UserOffererFactory(user=pro_user, offerer=validated_eac_booking.offerer)

        # When
        client = client.with_basic_auth(pro_user.email)
        response = client.get(f"/v2/bookings/token/{validated_eac_booking.token}")

        # Then
        assert response.headers["Content-type"] == "application/json"
        assert response.status_code == 200
        assert response.json == {
            "bookingId": humanize(validated_eac_booking.id),
            "dateOfBirth": "",
            "datetime": format_into_utc_date(validated_eac_booking.stock.beginningDatetime),
            "ean13": None,
            "email": redactor.email,
            "formula": "PLACE",
            "isUsed": False,
            "offerId": validated_eac_booking.stock.offer.id,
            "offerName": validated_eac_booking.stock.offer.name,
            "offerType": "EVENEMENT",
            "phoneNumber": "",
            "price": float(validated_eac_booking.stock.price),
            "publicOfferId": humanize(validated_eac_booking.stock.offer.id),
            "quantity": validated_eac_booking.quantity,
            "theater": {},
            "userName": f"{redactor.firstName} {redactor.lastName}",
            "venueAddress": validated_eac_booking.venue.address,
            "venueDepartmentCode": validated_eac_booking.venue.departementCode,
            "venueName": validated_eac_booking.venue.name,
        }

    def test_when_api_key_is_provided_and_rights_and_regular_offer(self, client):
        # Given
        booking = bookings_factories.IndividualBookingFactory()
        ApiKeyFactory(offerer=booking.offerer, prefix="test_prefix")

        # When
        url = f"/v2/bookings/token/{booking.token}"
        response = client.get(url, headers={"Authorization": "Bearer test_prefix_clearSecret"})

        # Then
        assert response.status_code == 200

    def test_when_user_has_rights_and_regular_offer_and_token_in_lower_case(self, client):
        # Given
        booking = bookings_factories.IndividualBookingFactory(
            stock__beginningDatetime=datetime.now() - timedelta(days=2),
        )
        user_offerer = offers_factories.UserOffererFactory(offerer=booking.offerer)
        pro_user = user_offerer.user

        # When
        client = client.with_basic_auth(pro_user.email)
        response = client.get(f"/v2/bookings/token/{booking.token.lower()}")

        # Then
        assert response.status_code == 200


class Returns401Test:
    def test_when_user_no_auth_nor_api_key(self, client):
        response = client.get("/v2/bookings/token/TOKEN")
        assert response.status_code == 401

    def test_when_wrong_api_key(self, client):
        url = "/v2/bookings/token/FAKETOKEN"
        response = client.get(url, headers={"Authorization": "Bearer WrongApiKey1234567"})
        assert response.status_code == 401


class Returns403Test:
    def test_when_user_doesnt_have_rights_and_token_exists(self, client):
        # Given
        booking = bookings_factories.IndividualBookingFactory()
        another_pro_user = offers_factories.UserOffererFactory().user

        # When
        url = f"/v2/bookings/token/{booking.token}"
        response = client.with_basic_auth(another_pro_user.email).get(url)

        # Then
        assert response.status_code == 403
        assert response.json["user"] == [
            "Vous n’avez pas les droits suffisants pour valider cette contremarque car cette réservation n'a pas été faite sur une de vos offres, ou que votre rattachement à la structure est encore en cours de validation"
        ]

    def test_when_given_api_key_not_related_to_booking_offerer(self, client):
        # Given
        booking = bookings_factories.IndividualBookingFactory()
        ApiKeyFactory()  # another offerer's API key

        # When
        auth = "Bearer development_prefix_clearSecret"
        url = f"/v2/bookings/token/{booking.token}"
        response = client.get(url, headers={"Authorization": auth})

        # Then
        assert response.status_code == 403
        assert response.json["user"] == [
            "Vous n’avez pas les droits suffisants pour valider cette contremarque car cette réservation n'a pas été faite sur une de vos offres, ou que votre rattachement à la structure est encore en cours de validation"
        ]

    def test_when_booking_not_confirmed(self, client):
        # Given
        next_week = datetime.utcnow() + timedelta(weeks=1)
        booking = bookings_factories.IndividualBookingFactory(stock__beginningDatetime=next_week)
        pro_user = offers_factories.UserOffererFactory(offerer=booking.offerer).user

        # When
        url = f"/v2/bookings/token/{booking.token}"
        response = client.with_basic_auth(pro_user.email).get(url)

        # Then
        assert response.status_code == 403
        assert "Veuillez attendre" in response.json["booking"][0]

    def test_when_booking_is_cancelled(self, client):
        # Given
        booking = bookings_factories.CancelledBookingFactory()
        pro_user = offers_factories.UserOffererFactory(offerer=booking.offerer).user

        # When
        url = f"/v2/bookings/token/{booking.token}"
        response = client.with_basic_auth(pro_user.email).get(url)

        # Then
        assert response.status_code == 403
        assert response.json["booking"] == ["Cette réservation a été annulée"]

    def test_when_booking_is_refunded(self, client):
        # Given
        booking = payments_factories.PaymentFactory().booking
        pro_user = offers_factories.UserOffererFactory(offerer=booking.offerer).user

        # When
        url = f"/v2/bookings/token/{booking.token}"
        response = client.with_basic_auth(pro_user.email).get(url)

        # Then
        assert response.status_code == 403
        assert response.json["payment"] == ["Cette réservation a été remboursée"]

    def test_when_booking_is_educational_and_not_validated_by_principal_yet(self, client):
        # Given
        redactor = educational_factories.EducationalRedactorFactory(
            civility="M.",
            firstName="Jean",
            lastName="Doudou",
            email="jean.doux@example.com",
        )
        not_validated_eac_booking = bookings_factories.EducationalBookingFactory(
            dateCreated=datetime.utcnow() - timedelta(days=5),
            educationalBooking__educationalRedactor=redactor,
            educationalBooking__status=None,
        )
        pro_user = users_factories.ProFactory()
        offers_factories.UserOffererFactory(user=pro_user, offerer=not_validated_eac_booking.offerer)
        url = f"/v2/bookings/token/{not_validated_eac_booking.token}"

        # When
        response = client.with_basic_auth(pro_user.email).get(url)

        # Then
        assert response.status_code == 403
        assert (
            response.json["educationalBooking"]
            == "Cette réservation pour une offre éducationnelle n'est pas encore validée par le chef d'établissement"
        )

    def test_when_booking_is_educational_and_refused_by_principal(self, client):
        # Given
        redactor = educational_factories.EducationalRedactorFactory(
            civility="M.",
            firstName="Jean",
            lastName="Doudou",
            email="jean.doux@example.com",
        )
        refused_eac_booking = bookings_factories.EducationalBookingFactory(
            dateCreated=datetime.utcnow() - timedelta(days=5),
            educationalBooking__educationalRedactor=redactor,
            educationalBooking__status=EducationalBookingStatus.REFUSED,
        )
        pro_user = users_factories.ProFactory()
        offers_factories.UserOffererFactory(user=pro_user, offerer=refused_eac_booking.offerer)
        url = f"/v2/bookings/token/{refused_eac_booking.token}"

        # When
        response = client.with_basic_auth(pro_user.email).get(url)

        # Then
        assert response.status_code == 403
        assert (
            response.json["educationalBooking"]
            == "Cette réservation pour une offre éducationnelle a été refusée par le chef d'établissement"
        )


class Returns404Test:
    def test_missing_token(self, client):
        response = client.get("/v2/bookings/token/")
        assert response.status_code == 404

    def test_basic_auth_but_unknown_token(self, client):
        user = offers_factories.UserOffererFactory().user
        client = client.with_basic_auth(user.email)
        response = client.get("/v2/bookings/token/UNKNOWN")

        assert response.status_code == 404
        assert response.json["global"] == ["Cette contremarque n'a pas été trouvée"]

    def test_authenticated_with_api_key_but_token_not_found(self, client):
        ApiKeyFactory(prefix="test_prefix")
        response = client.get("/v2/bookings/token/12345", headers={"Authorization": "Bearer test_prefix_clearSecret"})

        assert response.status_code == 404
        assert response.json["global"] == ["Cette contremarque n'a pas été trouvée"]


class Returns410Test:
    def test_when_booking_is_already_validated(self, client):
        booking = bookings_factories.UsedBookingFactory()
        user = offers_factories.UserOffererFactory(offerer=booking.offerer).user

        client = client.with_basic_auth(user.email)
        response = client.get(f"/v2/bookings/token/{booking.token}")

        assert response.status_code == 410
        assert response.json["booking"] == ["Cette réservation a déjà été validée"]
