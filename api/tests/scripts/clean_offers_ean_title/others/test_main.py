import re
import contextlib

import pytest

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.models import db
from pcapi.scripts.clean_offers_ean_title.others.main import run
from tests.scripts.clean_offers_ean_title import utils


pytestmark = pytest.mark.usefixtures("db_session")


EAN = "1234567890987"
EXTRA_DATA = {"ean": EAN, "author": "someone"}

TARGET_SUBCATEGORIES = [
    subcategories.SUPPORT_PHYSIQUE_FILM.id,
    subcategories.MATERIEL_ART_CREATIF.id,
    subcategories.ACHAT_INSTRUMENT.id,
    subcategories.LIVRE_PAPIER.id,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id,
]


class RunTest:
    def test_offer_name_with_ean_from_unauthorized_subcategory_is_rejected(self):
        offer = utils.build_random_offer()

        with utils.assert_rejected(offer):
            run()

    def test_offer_name_without_ean_from_unauthorized_subcategory_is_ignored(self):
        offer = utils.build_random_offer(name="no EAN here")

        with utils.assert_no_changes(offer):
            run()

    @pytest.mark.parametrize("subcategory_id", TARGET_SUBCATEGORIES)
    def test_offer_with_ean_from_targeted_subcategory_is_ignored(self, subcategory_id):
        offer = utils.build_offer(subcategory_id)

        with utils.assert_no_changes(offer):
            run()

    @pytest.mark.parametrize("subcategory_id", TARGET_SUBCATEGORIES)
    def test_offer_without_ean_from_targeted_subcategory_is_ignored(self, subcategory_id):
        offer = utils.build_offer(subcategory_id, name="my offer", ean="")

        with utils.assert_no_changes(offer):
            run()

    def test_offers_to_ignore_and_reject(self):
        offers_to_reject = [utils.build_random_offer(), utils.build_random_offer()]

        offers_to_ignore = [
            utils.build_offer(subcategory_id, name=f"my offer {idx}", ean="")
            for idx, subcategory_id in enumerate(TARGET_SUBCATEGORIES)
        ]
        offers_to_ignore += [
            utils.build_random_offer(name="no EAN"),
            utils.build_random_offer(name="nope")
        ]

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

