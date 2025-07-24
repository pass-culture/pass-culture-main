import csv
import datetime
import io

import pytest
import pytz

from pcapi.core.educational import factories
from pcapi.core.educational import models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import assert_num_queries


pytestmark = pytest.mark.usefixtures("db_session")


def _reader_from_response(response):
    csv_pseudo_file = io.StringIO(response.data.decode("utf-8-sig"))
    reader = csv.DictReader(csv_pseudo_file, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
    return list(reader)


def _format_date(date_time, tz):
    return date_time.replace(tzinfo=datetime.timezone.utc).astimezone(tz).isoformat()


class Returns200Test:
    num_queries = 1  # select session
    num_queries += 1  # select user
    num_queries += 1  # select collective_offer
    num_queries += 1  # selectinload collective_booking

    def test_one_offer(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = factories.ReimbursedCollectiveOfferFactory(
            venue=venue, locationType=models.CollectiveLocationType.ADDRESS, offererAddress=venue.offererAddress
        )
        stock = offer.collectiveStock
        [booking] = stock.collectiveBookings
        tz = pytz.timezone(offer.offererAddress.address.timezone)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.num_queries):
            response = client.get("/collective/offers/csv")
            assert response.status_code == 200

        reader = _reader_from_response(response)
        assert len(reader) == 1
        assert reader[0] == {
            "Nom de l'offre": offer.name,
            "Numéro de l'offre": offer.id,
            "Statut de l'offre": "REIMBURSED",
            "Structure": venue.common_name,
            "Localisation de l'offre": offer.offererAddress.address.fullAddress,
            "Date de début de l'évènement": _format_date(stock.startDatetime, tz),
            "Date de fin de l'évènement": _format_date(stock.endDatetime, tz),
            "Prix": stock.price,
            "Nombre de participants": stock.numberOfTickets,
            "Etablissement": offer.institution.full_name,
            "Code postal de l'établissement": offer.institution.postalCode,
            "UAI de l'établissement": offer.institution.institutionId,
            "Contact de l'établissement": booking.educationalRedactor.email,
            "Date de réservation de l'offre": _format_date(booking.dateCreated, tz),
            "Date de remboursement": _format_date(booking.reimbursementDate, tz),
        }
