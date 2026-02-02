import csv
import datetime
import io
from operator import attrgetter

import pytest
import pytz

from pcapi.core import testing
from pcapi.core.educational import factories
from pcapi.core.educational import models
from pcapi.core.educational.utils import format_collective_offer_displayed_status
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.users.factories import ProFactory


pytestmark = pytest.mark.usefixtures("db_session")

EXPECTED_HEADER = [
    "Nom de l'offre",
    "Numéro de l'offre",
    "Statut de l'offre",
    "Type de localisation de l'offre",
    "Localisation de l'offre",
    "Structure",
    "Etablissement",
    "Code postal de l'établissement",
    "UAI de l'établissement",
    "Email de l'enseignant",
    "Prénom de l'enseignant",
    "Nom de l'enseignant",
    "Date de début de l'évènement",
    "Date de fin de l'évènement",
    "Prix",
    "Nombre de participants",
    "Date de préréservation de l'offre",
    "Date de réservation de l'offre",
    "Date de remboursement",
]


def _reader_from_response(response):
    csv_pseudo_file = io.StringIO(response.data.decode("utf-8-sig"))
    reader = csv.DictReader(csv_pseudo_file, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
    assert reader.fieldnames == EXPECTED_HEADER
    return list(reader)


def _format_date(date_time, tz):
    return date_time.replace(tzinfo=datetime.timezone.utc).astimezone(tz).isoformat()


class Returns200Test:
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # select collective_offer ids
    num_queries += 1  # select collective_offer
    num_queries_with_bookings = num_queries + 1  # selectinload collective_booking

    def test_one_offer(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = factories.ReimbursedCollectiveOfferFactory(
            venue=venue, locationType=models.CollectiveLocationType.ADDRESS, offererAddress=venue.offererAddress
        )

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.num_queries_with_bookings):
            response = client.get("/collective/offers/csv")
            assert response.status_code == 200

        venue = offer.venue
        stock = offer.collectiveStock
        [booking] = stock.collectiveBookings
        tz = pytz.timezone(offer.offererAddress.address.timezone)
        reader = _reader_from_response(response)
        assert len(reader) == 1
        assert reader[0] == {
            "Nom de l'offre": offer.name,
            "Numéro de l'offre": offer.id,
            "Type de localisation de l'offre": "À une adresse précise",
            "Localisation de l'offre": offer.offererAddress.address.fullAddress,
            "Statut de l'offre": format_collective_offer_displayed_status(offer.displayedStatus).lower(),
            "Etablissement": offer.institution.full_name,
            "Code postal de l'établissement": offer.institution.postalCode,
            "UAI de l'établissement": offer.institution.institutionId,
            "Email de l'enseignant": booking.educationalRedactor.email,
            "Prénom de l'enseignant": booking.educationalRedactor.firstName,
            "Nom de l'enseignant": booking.educationalRedactor.lastName,
            "Structure": venue.common_name,
            "Date de début de l'évènement": _format_date(stock.startDatetime, tz),
            "Date de fin de l'évènement": _format_date(stock.endDatetime, tz),
            "Prix": stock.price,
            "Nombre de participants": stock.numberOfTickets,
            "Date de préréservation de l'offre": _format_date(booking.dateCreated, tz),
            "Date de réservation de l'offre": _format_date(booking.confirmationDate, tz),
            "Date de remboursement": _format_date(booking.reimbursementDate, tz),
        }

    def test_one_offer_draft(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = factories.DraftCollectiveOfferFactory(
            name="Special name &@🤡%",
            venue=venue,
            locationType=models.CollectiveLocationType.TO_BE_DEFINED,
            locationComment="Chez toi",
        )
        offer.institution = None

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.num_queries):
            response = client.get("/collective/offers/csv")
            assert response.status_code == 200

        reader = _reader_from_response(response)
        assert len(reader) == 1
        assert reader[0] == {
            "Nom de l'offre": "Special name &@🤡%",
            "Numéro de l'offre": offer.id,
            "Statut de l'offre": format_collective_offer_displayed_status(offer.displayedStatus).lower(),
            "Type de localisation de l'offre": "À déterminer avec l'enseignant",
            "Localisation de l'offre": "Chez toi",
            "Structure": venue.common_name,
            "Etablissement": "",
            "Code postal de l'établissement": "",
            "UAI de l'établissement": "",
            "Email de l'enseignant": "",
            "Prénom de l'enseignant": "",
            "Nom de l'enseignant": "",
            "Date de début de l'évènement": "",
            "Date de fin de l'évènement": "",
            "Prix": "",
            "Nombre de participants": "",
            "Date de préréservation de l'offre": "",
            "Date de réservation de l'offre": "",
            "Date de remboursement": "",
        }

    def test_multiple_offers(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offers = factories.BookedCollectiveOfferFactory.create_batch(
            3, venue__managingOfferer=user_offerer.offerer, locationType=models.CollectiveLocationType.SCHOOL
        )
        offers = sorted(offers, key=attrgetter("dateCreated"), reverse=True)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.num_queries_with_bookings):
            response = client.get("/collective/offers/csv")
            assert response.status_code == 200

        reader = _reader_from_response(response)
        assert len(reader) == 3
        for offer, row in zip(offers, reader):
            venue = offer.venue
            stock = offer.collectiveStock
            [booking] = stock.collectiveBookings
            tz = pytz.timezone(venue.offererAddress.address.timezone)
            assert row == {
                "Nom de l'offre": offer.name,
                "Numéro de l'offre": offer.id,
                "Statut de l'offre": "réservée",
                "Type de localisation de l'offre": "En établissement scolaire",
                "Localisation de l'offre": "",
                "Structure": venue.common_name,
                "Etablissement": offer.institution.full_name,
                "Code postal de l'établissement": offer.institution.postalCode,
                "UAI de l'établissement": offer.institution.institutionId,
                "Email de l'enseignant": booking.educationalRedactor.email,
                "Prénom de l'enseignant": booking.educationalRedactor.firstName,
                "Nom de l'enseignant": booking.educationalRedactor.lastName,
                "Date de début de l'évènement": _format_date(stock.startDatetime, tz),
                "Date de fin de l'évènement": _format_date(stock.endDatetime, tz),
                "Prix": stock.price,
                "Nombre de participants": stock.numberOfTickets,
                "Date de préréservation de l'offre": _format_date(booking.dateCreated, tz),
                "Date de réservation de l'offre": _format_date(booking.confirmationDate, tz),
                "Date de remboursement": "",
            }

    def test_user_no_result(self, client):
        factories.PublishedCollectiveOfferFactory()
        user = ProFactory()

        client = client.with_session_auth(user.email)
        # no request to get collective offers as there are no ids
        with assert_num_queries(self.num_queries - 1):
            response = client.get("/collective/offers/csv")
            assert response.status_code == 200

        reader = _reader_from_response(response)
        assert len(reader) == 0

    def test_filter_status(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = factories.PublishedCollectiveOfferFactory(venue=venue)
        _offer_not_in_result = factories.PrebookedCollectiveOfferFactory(venue=venue)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.num_queries_with_bookings):
            response = client.get("/collective/offers/csv")
            assert response.status_code == 200

        reader = _reader_from_response(response)
        assert len(reader) == 2

        with assert_num_queries(self.num_queries_with_bookings):
            response = client.get("/collective/offers/csv?status=PUBLISHED")
            assert response.status_code == 200

        reader = _reader_from_response(response)
        assert len(reader) == 1
        assert reader[0]["Numéro de l'offre"] == offer.id
        assert reader[0]["Nom de l'offre"] == offer.name

    def test_filter_date_range(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = factories.PublishedCollectiveOfferFactory(venue=venue)
        offer.collectiveStock.startDatetime = datetime.datetime.fromisoformat("2020-01-05")
        offer_not_in_result = factories.PublishedCollectiveOfferFactory(venue=venue)
        offer_not_in_result.collectiveStock.startDatetime = datetime.datetime.fromisoformat("2020-02-05")

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.num_queries_with_bookings):
            response = client.get("/collective/offers/csv")
            assert response.status_code == 200

        reader = _reader_from_response(response)
        assert len(reader) == 2

        with assert_num_queries(self.num_queries_with_bookings):
            response = client.get("/collective/offers/csv?periodBeginningDate=2020-01-01&periodEndingDate=2020-02-01")
            assert response.status_code == 200

        reader = _reader_from_response(response)
        assert len(reader) == 1
        assert reader[0]["Numéro de l'offre"] == offer.id
        assert reader[0]["Nom de l'offre"] == offer.name

    def test_filter_offerer_id(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = factories.PublishedCollectiveOfferFactory(venue=venue)
        user_offerer_not_in_result = offerers_factories.UserOffererFactory(user=user_offerer.user)
        _offer_not_in_result = factories.PublishedCollectiveOfferFactory(
            venue__managingOfferer=user_offerer_not_in_result.offerer
        )

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.num_queries_with_bookings):
            response = client.get("/collective/offers/csv")
            assert response.status_code == 200

        reader = _reader_from_response(response)
        assert len(reader) == 2

        offerer_id = user_offerer.offerer.id
        with assert_num_queries(self.num_queries_with_bookings):
            response = client.get(f"/collective/offers/csv?offererId={offerer_id}")
            assert response.status_code == 200

        reader = _reader_from_response(response)
        assert len(reader) == 1
        assert reader[0]["Numéro de l'offre"] == offer.id
        assert reader[0]["Nom de l'offre"] == offer.name
