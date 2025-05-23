import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.models import db
from pcapi.scripts.move_offer.move_batch_offer import _move_collective_offers
from pcapi.scripts.move_offer.move_batch_offer import _move_individual_offers
from pcapi.scripts.move_offer.move_batch_offer import _move_price_category_label


pytestmark = pytest.mark.usefixtures("db_session")


def test_move_price_category_label_respect_unicity_constraint():
    origin_venue = offerers_factories.VenueFactory()
    destination_venue = offerers_factories.VenueFactory()

    price_category_label_A_origin = offers_factories.PriceCategoryLabelFactory(label="labelA", venue=origin_venue)
    price_category_label_B_origin = offers_factories.PriceCategoryLabelFactory(label="labelB", venue=origin_venue)
    price_category_label_B_destination = offers_factories.PriceCategoryLabelFactory(
        label="labelB", venue=destination_venue
    )

    price_category_A = offers_factories.PriceCategoryFactory(priceCategoryLabel=price_category_label_A_origin)
    price_category_B = offers_factories.PriceCategoryFactory(priceCategoryLabel=price_category_label_B_origin)

    _move_price_category_label(origin_venue, destination_venue)
    db.session.commit()

    db.session.refresh(price_category_label_A_origin)
    db.session.refresh(price_category_label_B_origin)
    db.session.refresh(price_category_label_B_destination)
    assert price_category_label_A_origin.venue == destination_venue
    assert price_category_label_B_origin.venue == origin_venue
    assert price_category_label_B_destination.venue == destination_venue

    db.session.refresh(price_category_A)
    db.session.refresh(price_category_B)
    assert price_category_A.priceCategoryLabel == price_category_label_A_origin
    assert price_category_B.priceCategoryLabel == price_category_label_B_destination


@pytest.mark.features(VENUE_REGULARIZATION=True)
def test_move_batch_offer():
    origin_venue = offerers_factories.VenueFactory(siret=None, comment="coucou")

    collective_offer = educational_factories.CollectiveOfferFactory(venue=origin_venue)
    collective_offer2 = educational_factories.CollectiveOfferFactory(venue=origin_venue)
    collective_offer3 = educational_factories.CollectiveOfferFactory(venue=origin_venue)

    offer = offers_factories.OfferFactory(venue=origin_venue)
    offer2 = offers_factories.OfferFactory(venue=origin_venue)
    offer3 = offers_factories.OfferFactory(venue=origin_venue)

    destination_venue = offerers_factories.VenueFactory(managingOfferer=origin_venue.managingOfferer)

    _move_individual_offers(origin_venue=origin_venue, destination_venue=destination_venue)
    _move_collective_offers(origin_venue=origin_venue, destination_venue=destination_venue)

    db.session.refresh(collective_offer)
    db.session.refresh(collective_offer2)
    db.session.refresh(collective_offer3)
    assert collective_offer.venue == destination_venue
    assert collective_offer2.venue == destination_venue
    assert collective_offer3.venue == destination_venue

    db.session.refresh(offer)
    db.session.refresh(offer2)
    db.session.refresh(offer3)
    assert offer.venue == destination_venue
    assert offer2.venue == destination_venue
    assert offer3.venue == destination_venue
