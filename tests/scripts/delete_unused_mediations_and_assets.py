import os
import pathlib

import pytest

from pcapi.core.object_storage import store_public_object
from pcapi.core.object_storage.testing import TESTS_STORAGE_DIR
from pcapi.core.offers.factories import MediationFactory
from pcapi.core.offers.models import Mediation
from pcapi.scripts.delete_unused_mediations_and_assets import delete_obsolete_mediations
from pcapi.scripts.delete_unused_mediations_and_assets import delete_obsolete_thumbnails_in_object_storage
from pcapi.utils.human_ids import humanize

import tests


IMAGES_DIR = pathlib.Path(tests.__path__[0]) / "files"


class DeleteObsoleteMediations:
    @pytest.mark.usefixtures("db_session")
    def test_delete_obsolete_mediations(self):
        """delete inactive, delete thumbless, keep the rest"""
        # given
        mediation_1 = MediationFactory(credit="©PassCulture", isActive=True, thumbCount=1)
        mediation_2 = MediationFactory(isActive=True, thumbCount=1)
        MediationFactory(isActive=False)
        MediationFactory(isActive=True)

        # when
        delete_obsolete_mediations(dry_run=False)

        # then
        assert Mediation.query.all() == [mediation_1, mediation_2]


@pytest.mark.usefixtures("clear_tests_assets_bucket")
class DeleteObsoleteThumbnailsInObjectStorage:
    @pytest.mark.usefixtures("db_session")
    def test_delete_unnecessary_thumbs(self):
        """
        delete orphan assets ie for which no Mediation has the same ID
        delete all assets tied to MediationSQLEntities
        delete multiple thumbs of the same Mediation"""
        # given
        seagull_pic = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()

        # Two Mediations with one thumb each
        mediation_1 = MediationFactory(credit="©One", isActive=True, thumbCount=1)
        store_public_object(
            bucket="tests",
            object_id=mediation_1.get_thumb_storage_id(0),
            blob=seagull_pic,
            content_type="image/jpeg",
        )
        mediation_2 = MediationFactory(credit="©Two", isActive=True, thumbCount=1)
        store_public_object(
            bucket="tests",
            object_id=mediation_2.get_thumb_storage_id(0),
            blob=seagull_pic,
            content_type="image/jpeg",
        )

        # a thumb without Mediation
        store_public_object(
            bucket="tests",
            object_id="mediations/DUMMY",
            blob=seagull_pic,
            content_type="image/jpeg",
        )

        # a thumb without MediationSQLEntity
        store_public_object(
            bucket="tests",
            object_id="mediationsqlentities/DUMMY",
            blob=seagull_pic,
            content_type="image/jpeg",
        )

        # a Mediation without thumb
        MediationFactory(credit="An artist without assets", isActive=True, thumbCount=1)

        # a Mediation with two assets
        mediation_with_two_assets = MediationFactory(credit="Twins", isActive=True, thumbCount=2)
        store_public_object(
            bucket="tests",
            object_id=mediation_with_two_assets.get_thumb_storage_id(0) + "_1",
            blob=seagull_pic,
            content_type="image/jpeg",
        )
        store_public_object(
            bucket="tests",
            object_id=mediation_with_two_assets.get_thumb_storage_id(0) + "_2",
            blob=seagull_pic,
            content_type="image/jpeg",
        )

        # when
        delete_obsolete_thumbnails_in_object_storage(
            dry_run=False,
            folder_name="tests",
            marker="tests/mediations",
            end_marker="tests/mf",
        )

        # then
        # only two Mediations are left
        assert Mediation.query.all() == [mediation_1, mediation_2]
        # only its asset (and the local backend artifact) is left
        expected_assets = {
            humanize(mediation_1.id),
            humanize(mediation_1.id) + ".type",
            humanize(mediation_2.id),
            humanize(mediation_2.id) + ".type",
        }
        assert set(f.name for f in os.scandir(TESTS_STORAGE_DIR / "mediations")) == expected_assets
