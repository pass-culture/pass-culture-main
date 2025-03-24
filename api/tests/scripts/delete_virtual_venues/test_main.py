from pcapi.core.educational import factories as educational_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.models import db
from pcapi.scripts.delete_empty_virtual_venues.main import delete_venues_without_offers


class DeleteVenuesWithoutOffersTest:

    def test_delete_venues_without_offers(self):
        should_be_deleted_virtual_venue = offerers_factories.VirtualVenueFactory()
        virtual_venue_2 = offerers_factories.VirtualVenueFactory()
        virtual_venue_3 = offerers_factories.VirtualVenueFactory()
        venue = offerers_factories.VenueFactory()
        offers_factories.OfferFactory(venue=virtual_venue_2)
        educational_factories.CollectiveOfferFactory(venue=virtual_venue_3)

        should_be_deleted_virtual_venue_id = should_be_deleted_virtual_venue.id

        delete_venues_without_offers()

        assert not offerers_models.Venue.query.filter(
            offerers_models.Venue.id == should_be_deleted_virtual_venue_id
        ).one_or_none()
        assert offerers_models.Venue.query.filter(offerers_models.Venue.id == virtual_venue_2.id).one_or_none()
        assert offerers_models.Venue.query.filter(offerers_models.Venue.id == virtual_venue_3.id).one_or_none()
        assert offerers_models.Venue.query.filter(offerers_models.Venue.id == venue.id).one_or_none()
