from typing import Any
from unittest import mock

import pytest

from pcapi.core.educational.factories import CancelledCollectiveBookingFactory, EducationalDomainFactory
from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
from pcapi.core.educational.factories import CollectiveStockFactory
from pcapi.core.educational.factories import ConfirmedCollectiveBookingFactory
from pcapi.core.educational.factories import PendingCollectiveBookingFactory
from pcapi.core.educational.factories import ReimbursedCollectiveBookingFactory
import pcapi.core.educational.models as educational_models
from pcapi.core.offerers import factories as offerer_factories
from pcapi.core.testing import assert_num_queries


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    @mock.patch("pcapi.core.search.unindex_collective_offer_ids")
    @mock.patch("pcapi.core.search.unindex_collective_offer_template_ids")
    def test_deactivate_cultural_partner(self, mock_1, mock_2, client) -> None:
        domain = EducationalDomainFactory()
        offerer = offerer_factories.OffererFactory()
        reimbursed_booking = ReimbursedCollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=offerer,
            collectiveStock__collectiveOffer__domains=[domain],
        )
        cancelled_booking = CancelledCollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=offerer,
            collectiveStock__collectiveOffer__domains=[domain],
        )
        pending_booking = PendingCollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=offerer,
            collectiveStock__collectiveOffer__domains=[domain],
        )
        confirmed_booking = ConfirmedCollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=offerer,
            collectiveStock__collectiveOffer__domains=[domain],
        )
        collective_offer = CollectiveStockFactory(
            collectiveOffer__venue__managingOfferer=offerer, collectiveOffer__domains=[domain]
        ).collectiveOffer
        collective_offer_template = CollectiveOfferTemplateFactory(venue__managingOfferer=offerer, domains=[domain])

        siren = offerer.siren

        num_queries = 1  # fetch offerer
        num_queries += 1  # fetch all venues
        num_queries += 1  # commit update on offerer and venues
        num_queries += 1  # get active bookings
        num_queries += 1  # lock stocks
        num_queries += 1  # commit all bookings cancellation
        num_queries += 1  # release lock
        num_queries += 2  # get collective offers and template offers
        num_queries += 2  # update collective offers and template offers "isActive"
        num_queries += 2  # commit collective offers and template updates
        num_queries += 2  # unindex collective offers and template

        with assert_num_queries(num_queries):
            response = client.with_eac_token().post(f"/adage/v1/cultural_partners/{siren}/deactivate")

        assert response.status_code == 200

        reimbursed_booking = educational_models.CollectiveBooking.query.get(reimbursed_booking.id)
        cancelled_booking = educational_models.CollectiveBooking.query.get(cancelled_booking.id)
        pending_booking = (
            educational_models.CollectiveBooking.query.join(
                educational_models.CollectiveStock, educational_models.CollectiveBooking.collectiveStock
            )
            .join(educational_models.CollectiveOffer, educational_models.CollectiveStock.collectiveOffer)
            .filter(educational_models.CollectiveBooking.id == pending_booking.id)
            .one()
        )
        confirmed_booking = (
            educational_models.CollectiveBooking.query.join(
                educational_models.CollectiveStock, educational_models.CollectiveBooking.collectiveStock
            )
            .join(educational_models.CollectiveOffer, educational_models.CollectiveStock.collectiveOffer)
            .filter(educational_models.CollectiveBooking.id == confirmed_booking.id)
            .one()
        )
        collective_offer = educational_models.CollectiveOffer.query.get(collective_offer.id)
        collective_offer_template = educational_models.CollectiveOfferTemplate.query.get(collective_offer_template.id)

        # assert status did not change
        assert reimbursed_booking.status == educational_models.CollectiveBookingStatus.REIMBURSED
        assert cancelled_booking.status == educational_models.CollectiveBookingStatus.CANCELLED

        # assert bookings have been cancelled and offers have been deactivated
        assert pending_booking.status == educational_models.CollectiveBookingStatus.CANCELLED
        assert (
            pending_booking.cancellationReason == educational_models.CollectiveBookingCancellationReasons.DEACTIVATION
        )
        assert pending_booking.collectiveStock.collectiveOffer.isActive == False

        assert confirmed_booking.status == educational_models.CollectiveBookingStatus.CANCELLED
        assert (
            confirmed_booking.cancellationReason == educational_models.CollectiveBookingCancellationReasons.DEACTIVATION
        )
        assert confirmed_booking.collectiveStock.collectiveOffer.isActive == False

        assert collective_offer.isActive == False
        assert collective_offer_template.isActive == False


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    def test_offerer_not_found(self, client: Any, db_session: Any) -> None:
        response = client.with_eac_token().post("/adage/v1/cultural_partners/UNKNOWN/deactivate")

        assert response.status_code == 404
        assert response.json == {"code": "OFFERER_NOT_FOUND"}
