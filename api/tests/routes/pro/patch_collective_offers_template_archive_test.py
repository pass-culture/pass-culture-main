from unittest.mock import patch

import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import testing as educational_testing
from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    def when_archiving_existing_offers_templates(self, client):
        # Given
        offer1 = CollectiveOfferTemplateFactory()
        venue = offer1.venue
        offer2 = CollectiveOfferTemplateFactory(venue=venue)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)
        client = client.with_session_auth("pro@example.com")

        # When
        data = {"ids": [offer1.id, offer2.id]}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            # 1. authentication + user
            # 2. retrieve all collective_offer_template
            # 3. update dateArchive on collective_offer
            with assert_num_queries(3):
                response = client.patch("/collective/offers-template/archive", json=data)
                assert response.status_code == 204

        # Then
        db.session.refresh(offer1)
        assert offer1.isArchived
        assert not offer1.isActive
        db.session.refresh(offer2)
        assert offer2.isArchived
        assert not offer2.isActive

    def when_archiving_existing_offers_from_other_offerer(self, client):
        # Given
        offer = CollectiveOfferTemplateFactory()
        venue = offer.venue
        offerer = venue.managingOfferer

        other_offer = CollectiveOfferTemplateFactory()
        other_venue = other_offer.venue
        other_offerer = other_venue.managingOfferer

        # Ensure that the offerer is different
        assert other_offerer.id != offerer.id

        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)
        client = client.with_session_auth("pro@example.com")

        # When
        data = {"ids": [offer.id, other_offer.id]}

        response = client.patch("/collective/offers-template/archive", json=data)

        # Then
        assert response.status_code == 204
        db.session.refresh(offer)
        assert offer.isArchived
        assert not offer.isActive
        db.session.refresh(other_offer)
        assert not other_offer.isArchived
        assert other_offer.isActive

    def when_archiving_draft_offers_templates(self, client):
        # Given
        draft_template_offer = CollectiveOfferTemplateFactory(validation=OfferValidationStatus.DRAFT)
        venue = draft_template_offer.venue
        other_template_offer = CollectiveOfferTemplateFactory(venue=venue)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)
        client = client.with_session_auth("pro@example.com")

        # When
        data = {"ids": [draft_template_offer.id, other_template_offer.id]}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            # 1. authentication + user
            # 2. retrieve all collective_offer_template.ids to batch them in pool for update
            # 3. update dateArchive on collective_offer
            with assert_num_queries(3):
                response = client.patch("/collective/offers-template/archive", json=data)
                assert response.status_code == 204

        # Then
        db.session.refresh(draft_template_offer)
        assert draft_template_offer.isArchived
        assert not draft_template_offer.isActive
        db.session.refresh(other_template_offer)
        assert other_template_offer.isArchived
        assert not other_template_offer.isActive

    def when_archiving_rejected_offers_templates(self, client):
        rejected_template_offer = CollectiveOfferTemplateFactory(validation=OfferValidationStatus.REJECTED)
        venue = rejected_template_offer.venue
        other_template_offer = CollectiveOfferTemplateFactory(venue=venue)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)
        client = client.with_session_auth("pro@example.com")

        data = {"ids": [rejected_template_offer.id, other_template_offer.id]}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            # 1. authentication + user
            # 2. retrieve all collective_offer_template.ids to batch them in pool for update
            # 3. update dateArchive on collective_offer
            # 4. update dateArchive on collective_offer
            with assert_num_queries(4):
                response = client.patch("/collective/offers-template/archive", json=data)
                assert response.status_code == 204

        db.session.refresh(rejected_template_offer)
        assert rejected_template_offer.isArchived
        assert not rejected_template_offer.isActive
        db.session.refresh(other_template_offer)
        assert other_template_offer.isArchived
        assert not other_template_offer.isActive

    @pytest.mark.parametrize("status", educational_testing.STATUSES_ALLOWING_ARCHIVE_OFFER_TEMPLATE)
    def test_when_archiving_allowed_offers_templates(self, client, status):
        pending_template_offer = educational_factories.create_collective_offer_template_by_status(status)
        venue = pending_template_offer.venue
        other_template_offer = CollectiveOfferTemplateFactory(venue=venue)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)
        client = client.with_session_auth("pro@example.com")

        data = {"ids": [pending_template_offer.id, other_template_offer.id]}

        response = client.patch("/collective/offers-template/archive", json=data)

        assert response.status_code == 204


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    @pytest.mark.parametrize("status", educational_testing.STATUSES_NOT_ALLOWING_ARCHIVE_OFFER_TEMPLATE)
    def test_when_archiving_not_allowed_offers_templates(self, client, status):
        pending_template_offer = educational_factories.create_collective_offer_template_by_status(status)
        venue = pending_template_offer.venue
        other_template_offer = CollectiveOfferTemplateFactory(venue=venue)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)
        client = client.with_session_auth("pro@example.com")

        data = {"ids": [pending_template_offer.id, other_template_offer.id]}

        response = client.patch("/collective/offers-template/archive", json=data)

        assert response.status_code == 403
        assert response.json["global"] == ["Cette action n'est pas autorisée sur cette offre"]
