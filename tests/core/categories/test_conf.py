import pytest

from pcapi.core.categories import subcategories
from pcapi.core.categories.conf import get_subcategory_from_type
import pcapi.core.offers.factories as offers_factories
from pcapi.models import ThingType
from pcapi.models import db


@pytest.mark.parametrize(
    "offer_type, virtual_venue, expected_subcategoryId",
    [
        (ThingType.INSTRUMENT, False, subcategories.ACHAT_INSTRUMENT.id),
        (ThingType.PRESSE_ABO, True, subcategories.ABO_PRESSE_EN_LIGNE.id),
        (ThingType.AUDIOVISUEL, True, subcategories.VOD.id),
        (ThingType.AUDIOVISUEL, False, subcategories.SUPPORT_PHYSIQUE_FILM.id),
    ],
)
def test_get_subcategory_from_type(offer_type, virtual_venue, expected_subcategoryId, db_session):
    venue = offers_factories.VirtualVenueFactory() if virtual_venue else offers_factories.VenueFactory()
    # type is a required column that is defined in the post_create hook according to subcategoryId
    # so we cannot create an Offer with a null subcategoryId
    offer = offers_factories.OfferFactory.build(subcategoryId=subcategories.LIVRE_PAPIER.id, venue=venue)
    offer.type = str(offer_type)
    offer.subcategoryId = None
    db.session.add(offer)
    db.session.commit()

    assert (
        get_subcategory_from_type(offer_type=offer.type, is_virtual_venue=offer.venue.isVirtual)
        == expected_subcategoryId
    )
