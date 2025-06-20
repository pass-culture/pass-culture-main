from io import BytesIO
from pathlib import Path

import pytest

from pcapi import settings
from pcapi.core.educational import factories
from pcapi.core.educational import models
from pcapi.core.educational import testing as educational_testing
from pcapi.core.offerers import factories as offerers_factories

import tests


IMAGES_DIR = Path(tests.__path__[0]) / "files"
UPLOAD_FOLDER = settings.LOCAL_STORAGE_DIR / models.CollectiveOffer.FOLDER


@pytest.mark.usefixtures("db_session")
class DeleteImageFromFileTest:
    def test_delete_from_file(self, client):
        offer = factories.CollectiveOfferFactory()

        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # given
        thumb = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        data = {
            "credit": "John Do",
            "thumb": (BytesIO(thumb), "image.jpg"),
            "croppingRectX": 0.0,
            "croppingRectY": 0.0,
            "croppingRectHeight": 0.9,
            "croppingRectWidth": 0.6,
        }

        response = client.with_session_auth(email="user@example.com").post(
            f"/collective/offers/{offer.id}/image", form=data
        )

        # when

        response = client.with_session_auth(email="user@example.com").delete(f"/collective/offers/{offer.id}/image")

        # then

        assert response.status_code == 204
        assert (UPLOAD_FOLDER / offer._get_image_storage_id()).exists() is False

    @pytest.mark.parametrize("status", educational_testing.STATUSES_ALLOWING_EDIT_DETAILS)
    def test_delete_image_allowed_action(self, client, status):
        offer = factories.create_collective_offer_by_status(status)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        response = client.with_session_auth(email="user@example.com").delete(f"/collective/offers/{offer.id}/image")

        assert response.status_code == 204

    def test_forbidden_offer(self, client):
        # given
        offer = factories.CollectiveOfferFactory()

        offer2 = factories.CollectiveOfferFactory()

        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # when
        response = client.with_session_auth(email="user@example.com").delete(f"/collective/offers/{offer2.id}/image")

        # then
        assert response.status_code == 403

    @pytest.mark.parametrize("status", educational_testing.STATUSES_NOT_ALLOWING_EDIT_DETAILS)
    def test_delete_image_unallowed_action(self, client, status):
        offer = factories.create_collective_offer_by_status(status)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        response = client.with_session_auth(email="user@example.com").delete(f"/collective/offers/{offer.id}/image")

        assert response.status_code == 403
        assert response.json == {"global": ["Cette action n'est pas autorisée sur cette offre"]}

    def test_delete_image_ended(self, client):
        offer = factories.EndedCollectiveOfferConfirmedBookingFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        response = client.with_session_auth(email="user@example.com").delete(f"/collective/offers/{offer.id}/image")

        assert response.status_code == 403
        assert response.json == {"global": ["Cette action n'est pas autorisée sur cette offre"]}

    def test_not_authentified(self, client):
        # when
        response = client.delete("/collective/offers/0/image")

        # then
        assert response.status_code == 401

    def test_offer_not_found(self, client):
        # given
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
        )

        # when
        response = client.with_session_auth(email="user@example.com").delete("/collective/offers/0/image")

        # then
        assert response.status_code == 404
