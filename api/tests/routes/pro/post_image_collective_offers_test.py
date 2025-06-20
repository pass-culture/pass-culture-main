from io import BytesIO
from pathlib import Path

import pytest

from pcapi import settings
from pcapi.core.educational import factories
from pcapi.core.educational import models
from pcapi.core.educational import testing as educational_testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.models import db

import tests


IMAGES_DIR = Path(tests.__path__[0]) / "files"
UPLOAD_FOLDER = settings.LOCAL_STORAGE_DIR / models.CollectiveOffer.FOLDER


def get_image_data():
    thumb = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
    return {
        "credit": "John Do",
        "thumb": (BytesIO(thumb), "image.jpg"),
        "croppingRectX": 0.0,
        "croppingRectY": 0.0,
        "croppingRectHeight": 0.9,
        "croppingRectWidth": 0.6,
    }


@pytest.mark.usefixtures("db_session")
class AttachCollectiveOfferImageTest:
    def test_attach_offer_image(self, client):
        offer = factories.CollectiveOfferFactory()
        assert offer.imageId is None
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        auth_client = client.with_session_auth(email="user@example.com")
        response = auth_client.post(f"/collective/offers/{offer.id}/image", form=get_image_data())

        assert response.status_code == 200
        db.session.refresh(offer)
        assert (UPLOAD_FOLDER / offer._get_image_storage_id()).exists() is True
        assert offer.imageId is not None
        assert offer.imageCredit is not None
        assert offer.imageHasOriginal is not None

    @pytest.mark.parametrize("status", educational_testing.STATUSES_ALLOWING_EDIT_DETAILS)
    def test_attach_image_allowed_action(self, client, status):
        offer = factories.create_collective_offer_by_status(status)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        auth_client = client.with_session_auth(email="user@example.com")
        response = auth_client.post(f"/collective/offers/{offer.id}/image", form=get_image_data())

        assert response.status_code == 200
        assert (UPLOAD_FOLDER / offer._get_image_storage_id()).exists() is True

    @pytest.mark.parametrize("status", educational_testing.STATUSES_NOT_ALLOWING_EDIT_DETAILS)
    def test_attach_image_unallowed_action(self, client, status):
        offer = factories.create_collective_offer_by_status(status)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        auth_client = client.with_session_auth(email="user@example.com")
        response = auth_client.post(f"/collective/offers/{offer.id}/image", form=get_image_data())

        assert response.status_code == 403
        assert response.json == {"global": ["Cette action n'est pas autorisée sur cette offre"]}
        assert (UPLOAD_FOLDER / offer._get_image_storage_id()).exists() is False

    def test_attach_image_ended(self, client):
        offer = factories.EndedCollectiveOfferConfirmedBookingFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        auth_client = client.with_session_auth(email="user@example.com")
        response = auth_client.post(f"/collective/offers/{offer.id}/image", form=get_image_data())

        assert response.status_code == 403
        assert response.json == {"global": ["Cette action n'est pas autorisée sur cette offre"]}
        assert (UPLOAD_FOLDER / offer._get_image_storage_id()).exists() is False
