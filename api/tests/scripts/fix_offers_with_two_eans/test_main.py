import pytest

from pcapi.core.categories import subcategories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.scripts.fix_offers_with_two_eans.main import fix_offers_with_two_different_eans


pytestmark = pytest.mark.usefixtures("db_session")


EAN = "0000000000001"
OTHER_EAN = "0000000000002"
INCOMPATIBLE_EAN = "0000000000003"

EXTRA_DATA = {"ean": EAN, "author": "someone"}

TARGET_SUBCATEGORIES = [
    subcategories.LIVRE_PAPIER.id,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id,
]


def build_offer(subcategory_id, name=None, ean=None, **extra_kwargs):
    if ean is None:
        ean = EAN

    if name is None:
        name = f"My {subcategory_id} offer :: {ean}"

    return offers_factories.OfferFactory(
        name=name,
        extraData={},
        subcategoryId=subcategory_id,
        **extra_kwargs,
    )


def build_product(incompatible=False, ean=None):
    gcu = offers_models.GcuCompatibilityType.COMPATIBLE
    if incompatible:
        gcu = offers_models.GcuCompatibilityType.FRAUD_INCOMPATIBLE

    return offers_factories.ProductFactory(
        name="real product name",
        ean=ean,
        gcuCompatibilityType=gcu,
    )


class FixOffersWithTwoEansTest:
    @pytest.mark.parametrize("subcategory_id", TARGET_SUBCATEGORIES)
    def test_active_offer_is_updated(self, subcategory_id):
        real_ean = "0000000000001"
        another_ean = "0000000000002"

        offer = offers_factories.OfferFactory(
            extraData={"ean": real_ean},
            ean=another_ean,
            subcategoryId=subcategory_id,
        )

        build_product(ean=real_ean)

        fix_offers_with_two_different_eans()

        db.session.refresh(offer)
        assert offer.ean == real_ean
        assert offer.ean == offer.extraData["ean"]

    @pytest.mark.parametrize("subcategory_id", TARGET_SUBCATEGORIES)
    def test_inactive_offer_is_not_updated(self, subcategory_id):
        real_ean = "0000000000001"
        another_ean = "0000000000002"

        offer = offers_factories.OfferFactory(
            extraData={"ean": real_ean}, ean=another_ean, subcategoryId=subcategory_id, isActive=False
        )

        build_product(ean=real_ean)

        fix_offers_with_two_different_eans()

        db.session.refresh(offer)
        assert offer.ean == another_ean
        assert offer.ean != offer.extraData["ean"]

    def test_offer_from_random_category_is_not_updated(self):
        ean = "0000000000001"
        offer = offers_factories.EventOfferFactory()
        old_data = {"ean": offer.ean, "extraData": offer.extraData}

        build_product(ean=ean)

        fix_offers_with_two_different_eans()

        db.session.refresh(offer)
        new_data = {"ean": offer.ean, "extraData": offer.extraData}
        assert old_data == new_data

    def test_only_legit_offers_are_updated(self):
        to_update_offer1 = offers_factories.OfferFactory(
            ean="0000000000001",
            extraData={"ean": "0000000000002"},
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )

        to_update_offer2 = offers_factories.OfferFactory(
            ean="0000000000011",
            extraData={"ean": "0000000000022"},
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
        )

        build_product(ean="0000000000002")
        build_product(ean="0000000000022")

        # ignore offer: wrong subcategory
        ignored_offer = offers_factories.EventOfferFactory()
        old_data = {"ean": ignored_offer.ean, "extraData": ignored_offer.extraData}

        fix_offers_with_two_different_eans()

        db.session.refresh(to_update_offer1)
        db.session.refresh(to_update_offer2)
        db.session.refresh(ignored_offer)

        assert to_update_offer1.ean == "0000000000002"
        assert to_update_offer1.ean == to_update_offer1.extraData["ean"]

        assert to_update_offer2.ean == "0000000000022"
        assert to_update_offer2.ean == to_update_offer2.extraData["ean"]

        new_data = {"ean": ignored_offer.ean, "extraData": ignored_offer.extraData}
        assert old_data == new_data
