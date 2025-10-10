from typing import Iterable

from pcapi.core.offerers import models as offerers_models
from pcapi.core.geography import models as geography_models
from pcapi.core.offers.models import Offer
from pcapi.models import db


def get_all_venue_addresses(venue_id: int) -> Iterable[geography_models.Address]:
    address_ids_query = (
        db.session.query(offerers_models.OffererAddress.id)
        .join(Offer).filter(Offer.venueId == venue_id)
        .distinct(offerers_models.OffererAddress.addressId)
        .with_entities(offerers_models.OffererAddress.addressId)
        .all()
    )

    unique_address_ids = {row[0] for row in address_ids_query}
    return (
        db.session.query(geography_models.Address)
        .filter(geography_models.Address.id.in_(unique_address_ids))
    )
