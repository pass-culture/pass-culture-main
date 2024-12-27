from datetime import datetime

import pytest

from pcapi.core.educational import factories
from pcapi.core.educational import models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.models import db


STATUSES_NOT_ALLOWING_ARCHIVE = (
    models.CollectiveOfferDisplayedStatus.PENDING,
    models.CollectiveOfferDisplayedStatus.PREBOOKED,
    models.CollectiveOfferDisplayedStatus.BOOKED,
    models.CollectiveOfferDisplayedStatus.ENDED,
    models.CollectiveOfferDisplayedStatus.ARCHIVED,
)

STATUSES_ALLOWING_ARCHIVE = tuple(
    set(models.CollectiveOfferDisplayedStatus)
    - {*STATUSES_NOT_ALLOWING_ARCHIVE, models.CollectiveOfferDisplayedStatus.INACTIVE}
)


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    num_queries = 1  # authentication
    num_queries += 1  # load current_user
    num_queries += 1  # load Feature Flag
    num_queries += 1  # ensure there is no existing archived offer
    num_queries += 1  # retrieve all collective_order.ids to batch them in pool for update
    num_queries += 1  # update dateArchive on collective_offer

    num_queries_error = num_queries - 1  # "ensure there is no existing archived offer" is not run
    num_queries_error = num_queries_error - 1  # "update dateArchive on collective_offer" is not run
    num_queries_error = num_queries_error + 1  # rollback due to atomic

    @override_features(ENABLE_COLLECTIVE_NEW_STATUSES=False)
    def when_archiving_existing_offers(self, client):
        offer1 = factories.CollectiveOfferFactory()
        venue = offer1.venue
        offer2 = factories.CollectiveOfferFactory(venue=venue)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)
        client = client.with_session_auth("pro@example.com")

        data = {"ids": [offer1.id, offer2.id]}
        with assert_num_queries(self.num_queries):
            response = client.patch("/collective/offers/archive", json=data)
            assert response.status_code == 204

        db.session.refresh(offer1)
        assert offer1.isArchived
        assert not offer1.isActive
        db.session.refresh(offer2)
        assert offer2.isArchived
        assert not offer2.isActive

    def when_archiving_existing_offers_from_other_offerer(self, client):
        offer = factories.CollectiveOfferFactory()
        venue = offer.venue
        offerer = venue.managingOfferer

        other_offer = factories.CollectiveOfferFactory()
        other_venue = other_offer.venue
        other_offerer = other_venue.managingOfferer

        # Ensure that the offerer is different
        assert other_offerer.id != offerer.id

        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)
        client = client.with_session_auth("pro@example.com")

        data = {"ids": [offer.id, other_offer.id]}
        response = client.patch("/collective/offers/archive", json=data)

        assert response.status_code == 204
        db.session.refresh(offer)
        assert offer.isArchived
        assert not offer.isActive
        db.session.refresh(other_offer)
        assert not other_offer.isArchived
        assert other_offer.isActive

    @override_features(ENABLE_COLLECTIVE_NEW_STATUSES=False)
    def when_archiving_draft_offers(self, client):
        draft_offer = factories.create_collective_offer_by_status(models.CollectiveOfferDisplayedStatus.DRAFT)
        venue = draft_offer.venue
        other_offer = factories.CollectiveOfferFactory(venue=venue)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)
        client = client.with_session_auth("pro@example.com")

        data = {"ids": [draft_offer.id, other_offer.id]}
        with assert_num_queries(self.num_queries):
            response = client.patch("/collective/offers/archive", json=data)
            assert response.status_code == 204

        db.session.refresh(draft_offer)
        assert draft_offer.isArchived
        assert not draft_offer.isActive
        db.session.refresh(other_offer)
        assert other_offer.isArchived
        assert not other_offer.isActive

    @override_features(ENABLE_COLLECTIVE_NEW_STATUSES=False)
    def test_archive_rejected_offer(self, client):
        offer = factories.create_collective_offer_by_status(models.CollectiveOfferDisplayedStatus.REJECTED)
        venue = offer.venue
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)
        client = client.with_session_auth("pro@example.com")

        data = {"ids": [offer.id]}
        with assert_num_queries(self.num_queries):
            response = client.patch("/collective/offers/archive", json=data)
            assert response.status_code == 204

        db.session.refresh(offer)
        assert offer.isArchived
        assert not offer.isActive

    @override_features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
    @pytest.mark.parametrize("status", STATUSES_ALLOWING_ARCHIVE)
    def test_archive_offer_allowed_action(self, client, status):
        offer = factories.create_collective_offer_by_status(status)
        venue = offer.venue
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)
        client = client.with_session_auth("pro@example.com")

        data = {"ids": [offer.id]}
        # same queries except "ensure there is no existing archived offer"
        num_queries = self.num_queries - 1
        with assert_num_queries(num_queries):
            response = client.patch("/collective/offers/archive", json=data)
            assert response.status_code == 204

        db.session.refresh(offer)
        assert offer.isArchived
        assert not offer.isActive

    @override_features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
    @pytest.mark.parametrize("status", STATUSES_NOT_ALLOWING_ARCHIVE)
    def test_archive_offer_unallowed_action(self, client, status):
        offer = factories.create_collective_offer_by_status(status)
        venue = offer.venue
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)
        client = client.with_session_auth("pro@example.com")

        offer_was_active = offer.isActive
        offer_was_archived = offer.isArchived
        data = {"ids": [offer.id]}
        with assert_num_queries(self.num_queries_error):
            response = client.patch("/collective/offers/archive", json=data)
            assert response.status_code == 403
            assert response.json == {"global": ["Cette action n'est pas autorisée sur cette offre"]}

        db.session.refresh(offer)
        assert offer.isArchived == offer_was_archived
        assert offer.isActive == offer_was_active

    @override_features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
    def test_archive_offer_ended(self, client):
        offer = factories.EndedCollectiveOfferFactory(booking_is_confirmed=True)
        venue = offer.venue
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)
        client = client.with_session_auth("pro@example.com")

        data = {"ids": [offer.id]}
        with assert_num_queries(self.num_queries_error):
            response = client.patch("/collective/offers/archive", json=data)
            assert response.status_code == 403
            assert response.json == {"global": ["Cette action n'est pas autorisée sur cette offre"]}

        db.session.refresh(offer)
        assert offer.isArchived == False
        assert offer.isActive == True

    @override_features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
    def test_archive_offer_unallowed_action_on_one_offer(self, client):
        allowed_offer = factories.DraftCollectiveOfferFactory()
        venue = allowed_offer.venue
        unallowed_offer = factories.PrebookedCollectiveOfferFactory(venue=venue)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)
        client = client.with_session_auth("pro@example.com")

        data = {"ids": [allowed_offer.id, unallowed_offer.id]}
        with assert_num_queries(self.num_queries_error):
            response = client.patch("/collective/offers/archive", json=data)
            assert response.status_code == 403
            assert response.json == {"global": ["Cette action n'est pas autorisée sur cette offre"]}

        db.session.refresh(allowed_offer)
        db.session.refresh(unallowed_offer)
        assert not allowed_offer.isArchived
        assert not unallowed_offer.isArchived


@pytest.mark.usefixtures("db_session")
class Returns422Test:
    @override_features(ENABLE_COLLECTIVE_NEW_STATUSES=False)
    def when_archiving_already_archived(self, client):
        offer_already_archived = factories.CollectiveOfferFactory(isActive=False, dateArchived=datetime.utcnow())
        venue = offer_already_archived.venue
        offer_not_archived = factories.CollectiveOfferFactory(venue=venue)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)
        client = client.with_session_auth("pro@example.com")

        data = {"ids": [offer_already_archived.id, offer_not_archived.id]}
        response = client.patch("/collective/offers/archive", json=data)

        assert response.status_code == 422
        assert response.json == {"global": ["One of the offers is already archived"]}

        assert models.CollectiveOffer.query.get(offer_already_archived.id).isArchived
        assert not models.CollectiveOffer.query.get(offer_not_archived.id).isArchived
