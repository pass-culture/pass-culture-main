from io import BytesIO
from pathlib import Path

import pytest

from pcapi import settings
from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.offerers import factories as offerers_factories
from pcapi.utils.human_ids import humanize

import tests


IMAGES_DIR = Path(tests.__path__[0]) / "files"
UPLOAD_FOLDER = settings.LOCAL_STORAGE_DIR / CollectiveOffer.FOLDER


@pytest.mark.usefixtures("db_session")
class DeleteImageFromFileTest:
    def test_delete_from_file(self, client):
        offer = CollectiveOfferFactory()

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
            f"/collective/offers/{humanize(offer.id)}/image", form=data
        )

        # when

        response = client.with_session_auth(email="user@example.com").delete(
            f"/collective/offers/{humanize(offer.id)}/image"
        )

        # then

        assert response.status_code == 204
        assert (UPLOAD_FOLDER / offer._get_image_storage_id()).exists() is False

    def test_forbidden_offer(self, client):
        # given
        offer = CollectiveOfferFactory()

        offer2 = CollectiveOfferFactory()

        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # when
        response = client.with_session_auth(email="user@example.com").delete(
            f"/collective/offers/{humanize(offer2.id)}/image"
        )

        # then
        assert response.status_code == 403

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
