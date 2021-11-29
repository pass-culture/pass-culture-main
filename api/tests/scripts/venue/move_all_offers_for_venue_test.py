from unittest import mock

import pytest

from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.models import db
from pcapi.repository import repository
from pcapi.scripts.venue.move_all_offers_for_venue import move_all_offers_from_venue_to_other_venue


@pytest.mark.usefixtures("db_session")
class MoveAllOffersFromVenueToOtherVenueTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def should_change_venue_id_to_destination_id_for_offers_linked_to_origin_venue(self, mock_async_index_offer_ids):
        # Given
        offerer = create_offerer()
        origin_venue = create_venue(offerer)
        offers = [create_offer_with_thing_product(origin_venue), create_offer_with_thing_product(origin_venue)]
        destination_venue = create_venue(offerer, siret=offerer.siren + "56789")
        repository.save(*offers, destination_venue)

        # When
        move_all_offers_from_venue_to_other_venue(origin_venue.id, destination_venue.id)

        # Then
        db.session.refresh(destination_venue)
        assert set(destination_venue.offers) == set(offers)
        mock_async_index_offer_ids.assert_called_with({offer.id for offer in offers})
