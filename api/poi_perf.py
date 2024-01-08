import sqlalchemy as sa

from pcapi.core.geography.models import Address
from pcapi.core.geography.models import OffererPointOfInterest
from pcapi.core.geography.models import PointOfInterest
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.models import db
from pcapi.repository import transaction


with transaction():
    # Artificial data to create 300 Address and related POI
    venues = (
        Venue.query.filter(
            Venue.isVirtual == False, Venue.banId != None, Venue.address != "", Venue.managingOffererId == 13653
        )
        .options(
            sa.orm.load_only(
                Venue.id,
                Venue.name,
                Venue.address,
                Venue.postalCode,
                Venue.banId,
                Venue.city,
                Venue.longitude,
                Venue.latitude,
            )
        )
        .options(sa.orm.joinedload(Venue.managingOfferer).load_only(Offerer.id))
        .options(sa.orm.joinedload(Venue.offers).load_only(Offer.id))
        .limit(300)
        .all()
    )

    for venue in venues:
        # For each venue, create an `Address`, a related POI which is linked to the venue, and finally an `OffererPointOfInterest`
        address = Address(
            banId=venue.banId,
            street=venue.address,
            postalCode=venue.postalCode,
            city=venue.city,
            country="France",
            longitude=venue.longitude,
            latitude=venue.latitude,
        )
        poi = PointOfInterest(address=address)
        offerer_poi = OffererPointOfInterest(
            label=f"Mon {venue.name}", pointOfInterest=poi, offerer=venue.managingOfferer
        )
        venue.pointOfInterest = poi
        db.session.add(address)
        db.session.add(poi)
        db.session.add(offerer_poi)
        db.session.add(venue)
        # We need an ID to link offers to a PointOfInterest
        db.session.flush()
        # Link all the offers of the venue to it's POI
        db.session.bulk_update_mappings(
            Offer, [{"id": offer.id, "pointOfInterestId": poi.id} for offer in venue.offers]
        )
