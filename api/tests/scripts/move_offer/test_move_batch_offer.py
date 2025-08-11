from unittest import mock

import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.history import models as history_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.providers import factories as providers_factories
from pcapi.models import db
from pcapi.scripts.move_offer.move_batch_offer import _move_all_venue_offers
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
@mock.patch("pcapi.scripts.move_offer.move_batch_offer._extract_invalid_venues_to_csv")
def test_move_batch_offer(_extract_invalid_venues_to_csv_patch):
    _extract_invalid_venues_to_csv_patch.return_value = None
    origin_venue = offerers_factories.VenueFactory(siret=None, comment="coucou")

    collective_offer = educational_factories.CollectiveOfferFactory(venue=origin_venue)
    collective_offer2 = educational_factories.CollectiveOfferFactory(venue=origin_venue)
    collective_offer3 = educational_factories.CollectiveOfferFactory(venue=origin_venue)

    offer = offers_factories.OfferFactory(venue=origin_venue)
    offer2 = offers_factories.OfferFactory(venue=origin_venue)
    offer3 = offers_factories.OfferFactory(venue=origin_venue)

    destination_venue = offerers_factories.VenueFactory(managingOfferer=origin_venue.managingOfferer)

    origin_venue_id = origin_venue.id

    _move_all_venue_offers(dry_run=False, origin=origin_venue.id, destination=destination_venue.id)

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

    assert db.session.query(history_models.ActionHistory).count() == 3
    assert (
        db.session.query(history_models.ActionHistory)
        .filter(history_models.ActionHistory.venueId == origin_venue_id)[0]
        .actionType
        == history_models.ActionType.VENUE_REGULARIZATION
    )
    assert (
        db.session.query(history_models.ActionHistory)
        .filter(history_models.ActionHistory.venueId == origin_venue_id)[1]
        .actionType
        == history_models.ActionType.VENUE_SOFT_DELETED
    )
    assert (
        db.session.query(history_models.ActionHistory)
        .filter(history_models.ActionHistory.venueId == destination_venue.id)
        .one()
        .actionType
        == history_models.ActionType.VENUE_REGULARIZATION
    )


@pytest.mark.features(VENUE_REGULARIZATION=True)
@mock.patch("pcapi.scripts.move_offer.move_batch_offer._extract_invalid_venues_to_csv")
def test_move_batch_offer_destination_venue_already_permanent_no_action_history_created(
    _extract_invalid_venues_to_csv_patch,
):
    _extract_invalid_venues_to_csv_patch.return_value = None
    origin_venue = offerers_factories.VenueFactory(siret=None, comment="coucou")

    offer = offers_factories.OfferFactory(venue=origin_venue)

    destination_venue = offerers_factories.VenueFactory(managingOfferer=origin_venue.managingOfferer, isPermanent=True)

    origin_venue_id = origin_venue.id

    _move_all_venue_offers(dry_run=False, origin=origin_venue.id, destination=destination_venue.id)

    db.session.refresh(offer)
    assert offer.venue == destination_venue

    assert db.session.query(history_models.ActionHistory).count() == 2
    assert (
        db.session.query(history_models.ActionHistory)
        .filter(history_models.ActionHistory.venueId == origin_venue_id)[0]
        .actionType
        == history_models.ActionType.VENUE_REGULARIZATION
    )
    assert (
        db.session.query(history_models.ActionHistory)
        .filter(history_models.ActionHistory.venueId == origin_venue_id)[1]
        .actionType
        == history_models.ActionType.VENUE_SOFT_DELETED
    )


@pytest.mark.features(VENUE_REGULARIZATION=True)
@mock.patch("pcapi.scripts.move_offer.move_batch_offer._extract_invalid_venues_to_csv")
def test_move_batch_offer_with_provider(_extract_invalid_venues_to_csv_patch):
    _extract_invalid_venues_to_csv_patch.return_value = None

    origin_venue = offerers_factories.VenueFactory(siret=None, comment="coucou")
    active_provider = providers_factories.PublicApiProviderFactory.create(
        name="Provider name",
        isActive=True,
        hmacKey="S3cr3tK3y",
    )
    active_new_provider = providers_factories.PublicApiProviderFactory.create(
        name="New Provider name",
        isActive=True,
        hmacKey="S3cr3tK3y",
    )
    inactive_provider = providers_factories.PublicApiProviderFactory.create(
        name="Inactive Provider name",
        isActive=False,
        hmacKey="S3cr3tK3y",
    )

    offer = offers_factories.OfferFactory(venue=origin_venue)

    destination_venue = offerers_factories.VenueFactory(managingOfferer=origin_venue.managingOfferer)

    origin_venue_provider_already_on_destination = providers_factories.VenueProviderFactory.create(
        venue=origin_venue, provider=active_provider, isActive=True
    )
    origin_venue_provider_not_on_destination = providers_factories.VenueProviderFactory.create(
        venue=origin_venue, provider=active_new_provider, isActive=True
    )
    origin_venue_provider_inactive = providers_factories.VenueProviderFactory.create(
        venue=origin_venue, provider=inactive_provider, isActive=False
    )

    destination_venue_provider = providers_factories.VenueProviderFactory.create(
        venue=destination_venue, provider=active_provider, isActive=True
    )

    origin_venue_id = origin_venue.id

    # sanity check
    assert len(destination_venue.venueProviders) == 1

    _move_all_venue_offers(dry_run=False, origin=origin_venue.id, destination=destination_venue.id)

    db.session.refresh(destination_venue)
    assert len(destination_venue.venueProviders) == 2

    db.session.refresh(offer)
    assert offer.venue == destination_venue

    db.session.refresh(origin_venue_provider_already_on_destination)
    assert origin_venue_provider_already_on_destination.isActive is False
    db.session.refresh(origin_venue_provider_not_on_destination)
    assert origin_venue_provider_not_on_destination.isActive is False
    db.session.refresh(origin_venue_provider_inactive)
    assert origin_venue_provider_inactive.isActive is False

    db.session.refresh(destination_venue_provider)
    for provider in destination_venue.venueProviders:
        assert provider.isActive is True

    # 3 actions history VENUE_REGULARIZATION, 2 specific to providers
    assert db.session.query(history_models.ActionHistory).count() == 6
    assert (
        db.session.query(history_models.ActionHistory)
        .filter(
            history_models.ActionHistory.venueId == destination_venue.id,
            history_models.ActionHistory.actionType == history_models.ActionType.SYNC_VENUE_TO_PROVIDER,
        )
        .one()
    )
    assert (
        len(
            db.session.query(history_models.ActionHistory)
            .filter(
                history_models.ActionHistory.venueId == origin_venue_id,
                history_models.ActionHistory.actionType == history_models.ActionType.LINK_VENUE_PROVIDER_UPDATED,
            )
            .all()
        )
        == 2
    )
