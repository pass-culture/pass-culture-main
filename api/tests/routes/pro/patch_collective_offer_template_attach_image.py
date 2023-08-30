from io import BytesIO
from pathlib import Path

import pytest

from pcapi import settings
from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
from pcapi.core.educational.models import CollectiveOfferTemplate
from pcapi.core.offerers import factories as offerers_factories
from pcapi.utils.human_ids import humanize

import tests


IMAGES_DIR = Path(tests.__path__[0]) / "files"
UPLOAD_FOLDER = settings.LOCAL_STORAGE_DIR / CollectiveOfferTemplate.FOLDER



class AttachImageFromFileTest:
    def teardown_method(self):
        """clear images after each tests"""
        storage_folder = UPLOAD_FOLDER / CollectiveOfferTemplate.__name__.lower()
        for child in storage_folder.iterdir():
            if not child.is_file():
                continue
            child.unlink()

    def test_import_from_file(self, client):
        offer = CollectiveOfferTemplateFactory(
            mentalDisabilityCompliant=False,
            contactEmail="johndoe@yopmail.com",
            contactPhone="0600000000",
            subcategoryId="CINE_PLEIN_AIR",
            domains=[],
        )

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

        # when
        response = client.with_session_auth(email="user@example.com").patch(
            f"/collective/offers-template/{humanize(offer.id)}/image", form=data
        )

        # then
        assert response.status_code == 200
        assert response.json == {
            "imageUrl": offer.imageUrl,
        }
        assert (UPLOAD_FOLDER / offer._get_image_storage_id()).exists()
        assert offer.hasImage

    def test_too_small(self, client):
        offer = CollectiveOfferTemplateFactory(
            mentalDisabilityCompliant=False,
            contactEmail="johndoe@yopmail.com",
            contactPhone="0600000000",
            subcategoryId="CINE_PLEIN_AIR",
            domains=[],
        )

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
            "croppingRectHeight": 0.001,
            "croppingRectWidth": 0.001,
        }

        # when
        response = client.with_session_auth(email="user@example.com").patch(
            f"/collective/offers-template/{humanize(offer.id)}/image", form=data
        )

        # then
        assert response.status_code == 400

    def test_forbidden_offer(self, client):
        offer = CollectiveOfferTemplateFactory(
            mentalDisabilityCompliant=False,
            contactEmail="johndoe@yopmail.com",
            contactPhone="0600000000",
            subcategoryId="CINE_PLEIN_AIR",
            domains=[],
        )

        offer2 = CollectiveOfferTemplateFactory(
            mentalDisabilityCompliant=False,
            contactEmail="johndoe@yopmail.com",
            contactPhone="0600000000",
            subcategoryId="CINE_PLEIN_AIR",
            domains=[],
        )

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

        # when
        response = client.with_session_auth(email="user@example.com").patch(
            f"/collective/offers-template/{humanize(offer2.id)}/image", form=data
        )

        # then
        assert response.status_code == 403

    def test_not_authentified(self, client):
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

        # when
        response = client.patch("/collective/offers-template/0/image", form=data)

        # then
        assert response.status_code == 401

    def test_offer_not_found(self, client):
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
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

        # when
        response = client.with_session_auth(email="user@example.com").patch(
            "/collective/offers-template/0/image", form=data
        )

        # then
        assert response.status_code == 404
