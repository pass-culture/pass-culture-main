import re
import contextlib

import pytest

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.scripts.clean_offers_ean_title.movie_creative_material_music_instruments.main import run
from tests.scripts.clean_offers_ean_title import utils


pytestmark = pytest.mark.usefixtures("db_session")


EAN = "1234567890987"
EXTRA_DATA = {"ean": EAN, "author": "someone"}

TARGET_SUBCATEGORIES = [
    subcategories.SUPPORT_PHYSIQUE_FILM.id,
    subcategories.MATERIEL_ART_CREATIF.id,
    subcategories.ACHAT_INSTRUMENT.id,
]


def build_product(incompatible=False, ean=None):
    gcu = offers_models.GcuCompatibilityType.COMPATIBLE
    if incompatible:
        gcu = offers_models.GcuCompatibilityType.FRAUD_INCOMPATIBLE

    extra_data = EXTRA_DATA
    if ean is not None:
        extra_data["ean"] = ean

    return offers_factories.ProductFactory(
        name="real product name",
        extraData=EXTRA_DATA,
        gcuCompatibilityType=gcu,
    )


class RunTest:
    @pytest.mark.parametrize("subcategory_id", TARGET_SUBCATEGORIES)
    def test_offer_name_contains_ean_and_more_is_updated(self, subcategory_id):
        offer = utils.build_offer(subcategory_id)

        with assert_offers_updated(offer):
            run()

    @pytest.mark.parametrize("subcategory_id", TARGET_SUBCATEGORIES)
    def test_offer_name_is_an_ean_is_rejected(self, subcategory_id):
        offer = utils.build_offer(subcategory_id, name=utils.EAN)

        with utils.assert_rejected(offer):
            run()

    @pytest.mark.parametrize("name", [utils.EAN, "nope", ""])
    def test_offer_is_not_from_targeted_subcategories_is_ignored(self, name):
        offer = utils.build_random_offer(name=name)

        with utils.assert_no_changes(offer):
            run()

    def test_offers_to_update_ignore_and_reject(self):
        eans = ["0000000000001", "0000000000002", "0000000000003"]
        names_as_eans = ["1111111111111", "1111111111112", "1111111111113"]

        offers_to_update = utils.build_offers(TARGET_SUBCATEGORIES, eans=eans)
        offers_to_reject = utils.build_offers(TARGET_SUBCATEGORIES, names=names_as_eans)
        offers_to_ignore = [
            utils.build_random_offer(name="some offer to ignore"),
            utils.build_random_offer(name="another offer to ignore"),
        ]

        with assert_offers_updated(*offers_to_update):
            with utils.assert_no_changes(*offers_to_ignore):
                with utils.assert_rejected(*offers_to_reject):
                    run()


@contextlib.contextmanager
def assert_offers_updated(*offers):
    valid = re.compile(r"^.*([0-9]{13}).*$")

    eans = {offer.id: None for offer in offers}
    for offer in offers:
        match = valid.match(offer.name)
        assert match is not None

        eans[offer.id] = match.group(1)

    yield

    for offer in offers:
        db.session.refresh(offer)

        assert valid.match(offer.name) is None
        assert offer.extraData["ean"] == eans[offer.id]
