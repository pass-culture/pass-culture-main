import typing
from unittest import mock

import pytest

from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
from pcapi.core.educational.factories import PlaylistFactory
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.providers.factories import ProviderFactory
from pcapi.core.providers.factories import VenueProviderFactory
from pcapi.core.providers.models import VenueProvider
from pcapi.core.users.factories import UserFactory
from pcapi.models import db
from pcapi.scripts.soft_delete_venues_without_offers.main import main


pytestmark = pytest.mark.usefixtures("db_session")


def mock_csv(venue_list: list[int]) -> typing.Iterator[int]:
    for venue_id in venue_list:
        yield {"Venue ID": str(venue_id)}


@mock.patch("pcapi.scripts.soft_delete_venues_without_offers.main._read_csv_file")
def test_soft_delete_basic(mock_read_csv_file):
    UserFactory(id=5752883)
    venue = VenueFactory(isPermanent=False, isOpenToPublic=False)
    VenueFactory(isPermanent=True, isOpenToPublic=False, managingOfferer=venue.managingOfferer)

    mock_read_csv_file.return_value = mock_csv([venue.id])
    main()
    db.session.commit()
    db.session.query(offerers_models.Venue).execution_options(
        include_deleted=True
    ).all()  # reloading soft deleted venues into session

    assert venue.isSoftDeleted is True
    actions_list = db.session.query(history_models.ActionHistory).all()
    assert len(actions_list) == 1
    assert actions_list[0].actionType == history_models.ActionType.VENUE_SOFT_DELETED
    assert actions_list[0].venue == venue


@mock.patch("pcapi.scripts.soft_delete_venues_without_offers.main._read_csv_file")
def test_soft_delete_multiple_venue_on_offerer(mock_read_csv_file):
    UserFactory(id=5752883)
    venue1 = VenueFactory(isPermanent=False, isOpenToPublic=False)
    venue2 = VenueFactory(isPermanent=False, isOpenToPublic=False, managingOfferer=venue1.managingOfferer)

    mock_read_csv_file.return_value = mock_csv([venue1.id, venue2.id])

    main()
    db.session.commit()
    db.session.query(offerers_models.Venue).execution_options(
        include_deleted=True
    ).all()  # reloading soft deleted venues into session

    assert venue1.isSoftDeleted is True
    assert venue2.isSoftDeleted is False  # it should not be deleted as it is the only venue remaining on this offerer
    actions_list = db.session.query(history_models.ActionHistory).all()
    assert len(actions_list) == 1
    assert actions_list[0].actionType == history_models.ActionType.VENUE_SOFT_DELETED
    assert actions_list[0].venue == venue1


@mock.patch("pcapi.scripts.soft_delete_venues_without_offers.main._read_csv_file")
def test_do_not_soft_delete_venue_with_offer(mock_read_csv_file):
    UserFactory(id=5752883)
    venue_with_offers = VenueFactory(isPermanent=False, isOpenToPublic=False)
    venue_with_collective_offers = VenueFactory(isPermanent=False, isOpenToPublic=False)
    venue_with_collective_playlist = VenueFactory(isPermanent=False, isOpenToPublic=False)
    venue_with_collective_offer_templates = VenueFactory(isPermanent=False, isOpenToPublic=False)
    venue_without_offers = VenueFactory(
        isPermanent=False, isOpenToPublic=False, managingOfferer=venue_with_offers.managingOfferer
    )
    OfferFactory.create_batch(5, venue=venue_with_offers)
    CollectiveOfferFactory.create_batch(5, venue=venue_with_collective_offers)
    CollectiveOfferTemplateFactory.create_batch(5, venue=venue_with_collective_offer_templates)
    PlaylistFactory.create_batch(5, venue=venue_with_collective_playlist)

    mock_read_csv_file.return_value = mock_csv(
        [
            venue_with_offers.id,
            venue_without_offers.id,
            venue_with_collective_offers.id,
            venue_with_collective_offer_templates.id,
            venue_with_collective_playlist.id,
        ]
    )

    main()
    db.session.commit()
    db.session.query(offerers_models.Venue).execution_options(
        include_deleted=True
    ).all()  # reloading soft deleted venues into session

    assert venue_without_offers.isSoftDeleted is True
    assert venue_with_offers.isSoftDeleted is False  # it should not be deleted as it has offers
    assert venue_with_collective_offers.isSoftDeleted is False  # it should not be deleted as it has collective offers
    assert venue_with_collective_offer_templates.isSoftDeleted is False  # it should not be deleted as it has templates
    assert venue_with_collective_playlist.isSoftDeleted is False  # it should not be deleted as it has playlist

    actions_list = db.session.query(history_models.ActionHistory).all()
    assert len(actions_list) == 1
    assert actions_list[0].actionType == history_models.ActionType.VENUE_SOFT_DELETED
    assert actions_list[0].venue == venue_without_offers


@mock.patch("pcapi.scripts.soft_delete_venues_without_offers.main._read_csv_file")
def test_do_not_soft_delete_venues_open_to_public_or_permanent(mock_read_csv_file):
    UserFactory(id=5752883)
    venue1 = VenueFactory(isPermanent=False, isOpenToPublic=True)  # this should not happen
    venue2 = VenueFactory(isPermanent=True, isOpenToPublic=True, managingOfferer=venue1.managingOfferer)
    venue3 = VenueFactory(isPermanent=True, isOpenToPublic=False, managingOfferer=venue1.managingOfferer)
    venue4 = VenueFactory(isPermanent=False, isOpenToPublic=False, managingOfferer=venue1.managingOfferer)

    mock_read_csv_file.return_value = mock_csv([venue1.id, venue2.id, venue3.id, venue4.id])

    main()
    db.session.commit()
    db.session.query(offerers_models.Venue).execution_options(
        include_deleted=True
    ).all()  # reloading soft deleted venues into session

    assert venue1.isSoftDeleted is False  # it should not be deleted as it is opened to public
    assert venue2.isSoftDeleted is False  # it should not be deleted as it is permanent and open to public
    assert venue3.isSoftDeleted is False  # it should not be deleted as it is permanent
    assert venue4.isSoftDeleted is True  # last venue without offers on this offerer, should be deleted

    actions_list = db.session.query(history_models.ActionHistory).all()
    assert len(actions_list) == 1
    assert actions_list[0].actionType == history_models.ActionType.VENUE_SOFT_DELETED
    assert actions_list[0].venue == venue4


@mock.patch("pcapi.scripts.soft_delete_venues_without_offers.main._read_csv_file")
def test_soft_delete_venue_with_provider(mock_read_csv_file):
    venue = VenueFactory(isPermanent=False, isOpenToPublic=False)
    UserFactory(id=5752883)
    VenueFactory(isPermanent=True, isOpenToPublic=False, managingOfferer=venue.managingOfferer)
    provider = ProviderFactory()
    VenueProviderFactory(provider=provider, venue=venue)
    assert db.session.query(VenueProvider).count() == 1

    mock_read_csv_file.return_value = mock_csv([venue.id])
    main()
    db.session.commit()
    db.session.query(offerers_models.Venue).execution_options(
        include_deleted=True
    ).all()  # reloading soft deleted venues into session

    assert venue.isSoftDeleted is True
    assert db.session.query(VenueProvider).count() == 0

    actions_list = db.session.query(history_models.ActionHistory).all()
    assert len(actions_list) == 2
    assert actions_list[0].actionType == history_models.ActionType.LINK_VENUE_PROVIDER_DELETED
    assert actions_list[0].venue == venue
    assert actions_list[0].extraData["provider_id"] == provider.id
