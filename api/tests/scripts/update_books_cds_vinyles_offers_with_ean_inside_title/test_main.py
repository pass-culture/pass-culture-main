import contextlib
from datetime import timedelta

import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.categories import subcategories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.scripts.update_books_cds_vinyles_offers_with_ean_inside_title.main import update_offers_with_ean_inside_title


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


def build_regular_offer(subcategory_id, name=None, ean=None, with_booking=True, **extra_kwargs):
    if ean is None:
        ean = EAN

    if name is None:
        name = f"My {subcategory_id} regular test offer"

    if with_booking:
        kwargs = {
            "stock__offer__name": name,
            "stock__offer__extraData": {"ean": ean},
            "stock__offer__ean": ean,
            "stock__offer__isActive": True,
            "stock__offer__subcategoryId": subcategory_id,
            **extra_kwargs,
        }
        return bookings_factories.BookingFactory(**kwargs).stock.offer

    kwargs = {
        "name": name,
        "extraData": {"ean": ean},
        "ean": ean,
        "isActive": True,
        "subcategoryId": subcategory_id,
        **extra_kwargs,
    }
    return offers_factories.OfferFactory(**kwargs)


def build_offer(subcategory_id, name=None, ean=None, with_booking=True, **extra_kwargs):
    if ean is None:
        ean = EAN

    if name is None:
        name = f"My {subcategory_id} offer :: {ean}"

    if with_booking:
        return bookings_factories.BookingFactory(
            stock__offer__name=name,
            stock__offer__extraData={},
            stock__offer__subcategoryId=subcategory_id,
            **extra_kwargs,
        ).stock.offer
    return offers_factories.OfferFactory(
        name=name,
        extraData={},
        subcategoryId=subcategory_id,
        **extra_kwargs,
    )


def build_rejected_offer(subcategory_id, name=None, ean=None, with_booking=True, **extra_kwargs):
    extra_kwargs.update({"stock__offer__validation": OfferValidationStatus.REJECTED})
    return build_offer(subcategory_id, name=name, ean=ean, with_booking=with_booking, **extra_kwargs)


def build_inactive_offer(subcategory_id, name=None, ean=None, with_booking=True, **extra_kwargs):
    extra_kwargs.update({"stock__offer__isActive": False})
    return build_offer(subcategory_id, name=name, ean=ean, with_booking=with_booking, **extra_kwargs)


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


class LegitOfferWithEanInsideTitleTest:
    """Offers with a EAN inside title that matches a known and valid product"""

    @pytest.mark.parametrize("subcategory_id", TARGET_SUBCATEGORIES)
    def test_active_offer_is_updated(self, subcategory_id):
        offer = build_offer(subcategory_id, ean=EAN)
        product = build_product(ean=EAN)

        with assert_updated_from_product((offer, product)):
            update_offers_with_ean_inside_title()

    @pytest.mark.parametrize("subcategory_id", TARGET_SUBCATEGORIES)
    def test_inactive_offer_is_ignored(self, subcategory_id):
        offer = build_inactive_offer(subcategory_id, ean=EAN)
        build_product(ean=EAN)

        with assert_no_changes(offer):
            update_offers_with_ean_inside_title()

    @pytest.mark.parametrize("subcategory_id", TARGET_SUBCATEGORIES)
    def test_rejected_offer_is_ignored(self, subcategory_id):
        offer = build_rejected_offer(subcategory_id, ean=EAN)
        build_product(ean=EAN)

        with assert_no_changes(offer):
            update_offers_with_ean_inside_title()


class NoEAnInsideTitleTest:
    @pytest.mark.parametrize("subcategory_id", TARGET_SUBCATEGORIES)
    @pytest.mark.parametrize("offer_factory", [build_offer, build_inactive_offer, build_rejected_offer])
    def test_active_offer_is_ignored(self, subcategory_id, offer_factory):
        offer = offer_factory(subcategory_id, name="no ean here")
        build_product(ean=EAN)

        with assert_no_changes(offer):
            update_offers_with_ean_inside_title()


class LegitOfferWithAnotherOneFromSameVenueTest:
    """Offers with a EAN inside title that matches a known and valid product
    AND from a venue that also have at least another one with same EAN
    """

    @pytest.mark.parametrize("subcategory_id", TARGET_SUBCATEGORIES)
    def test_active_offer_is_updated(self, subcategory_id):
        offer = build_offer(subcategory_id, ean=EAN)
        preexisting_offer = build_regular_offer(
            subcategory_id,
            ean=EAN,
            stock__offer__dateCreated=offer.dateCreated - timedelta(days=1),
            stock__offer__venue=offer.venue,
        )
        product = build_product(ean=EAN)

        with assert_updated_from_product((offer, product)):
            with assert_deactivated(preexisting_offer):
                update_offers_with_ean_inside_title()

    @pytest.mark.parametrize("subcategory_id", TARGET_SUBCATEGORIES)
    def test_active_offer_with_existing_deactivated_one_is_updated(self, subcategory_id):
        offer = build_offer(subcategory_id, ean=EAN)
        preexisting_offer = build_regular_offer(
            subcategory_id,
            ean=EAN,
            stock__offer__validation=OfferValidationStatus.REJECTED,
            stock__offer__dateCreated=offer.dateCreated - timedelta(days=1),
            stock__offer__venue=offer.venue,
        )
        product = build_product(ean=EAN)

        with assert_updated_from_product((offer, product)):
            with assert_no_changes(preexisting_offer):
                update_offers_with_ean_inside_title()

    @pytest.mark.parametrize("subcategory_id", TARGET_SUBCATEGORIES)
    def test_active_offer_with_existing_inactive_one_is_updated(self, subcategory_id):
        offer = build_offer(subcategory_id, ean=EAN)
        preexisting_offer = build_regular_offer(
            subcategory_id,
            ean=EAN,
            stock__offer__isActive=False,
            stock__offer__dateCreated=offer.dateCreated - timedelta(days=1),
            stock__offer__venue=offer.venue,
        )
        product = build_product(ean=EAN)

        with assert_updated_from_product((offer, product)):
            with assert_no_changes(preexisting_offer):
                update_offers_with_ean_inside_title()


class LegitOfferWithAnotherOneFromSameVenueWithoutSameEANTest:
    """Offers with a EAN inside title that matches a known and valid product
    AND from a venue that has at least one other offer BUT NONE with the same
    EAN.
    """

    @pytest.mark.parametrize("subcategory_id", TARGET_SUBCATEGORIES)
    def test_active_offer_is_updated(self, subcategory_id):
        offer = build_offer(subcategory_id, ean=EAN)
        product = build_product(ean=EAN)

        preexisting_offer = build_regular_offer(
            subcategory_id,
            ean=OTHER_EAN,
            stock__offer__dateCreated=offer.dateCreated - timedelta(days=1),
            stock__offer__venue=offer.venue,
        )
        build_product(ean=OTHER_EAN)

        with assert_updated_from_product((offer, product)):
            with assert_no_changes(preexisting_offer):
                update_offers_with_ean_inside_title()


class RunTest:
    @pytest.mark.parametrize(
        "min_id, max_id, batch_size",
        [
            (None, None, None),
            (1, None, None),
            (1, "max", None),
            (1, "max", 100),
            ("min", "max", 1),
        ],
    )
    def test_offers_to_ignore_and_to_update(self, min_id, max_id, batch_size):
        products = [
            build_product(ean=EAN),
            build_product(ean=OTHER_EAN),
            build_product(ean=INCOMPATIBLE_EAN, incompatible=True),
        ]

        to_update_offers = [
            # name has a known and legit EAN -> must be updated
            build_offer(TARGET_SUBCATEGORIES[0], name=EAN),
            build_offer(TARGET_SUBCATEGORIES[1], name=OTHER_EAN),
        ]

        to_ignore_offers = [
            # no EAN inside title -> must be ignored
            build_offer(TARGET_SUBCATEGORIES[0], name="ok"),
            # has EAN inside title but is not known -> must be ignored
            build_offer(TARGET_SUBCATEGORIES[1], name="0000000000099"),
            # has EAN inside title but is not compatible -> must be ignored
            build_offer(TARGET_SUBCATEGORIES[2], name=INCOMPATIBLE_EAN),
            # is rejected -> must be ignored
            build_rejected_offer(TARGET_SUBCATEGORIES[0], name=EAN),
            # is inactive -> must be ignored
            build_inactive_offer(TARGET_SUBCATEGORIES[1], name=OTHER_EAN),
        ]

        if max_id == "max":
            max_id = offers_models.Offer.query.order_by(offers_models.Offer.id.desc()).first().id + 1

        if min_id == "min":
            min_id = offers_models.Offer.query.first().id - 1

        with assert_updated_from_product(*zip(to_update_offers, products)):
            with assert_no_changes(*to_ignore_offers):
                update_offers_with_ean_inside_title(min_id=min_id, max_id=max_id, batch_size=batch_size)


@contextlib.contextmanager
def assert_no_changes(*offers):
    old_names = {offer.id: offer.name for offer in offers}
    old_extra_data = {offer.id: offer.extraData for offer in offers}
    old_status = {offer.id: offer.status for offer in offers}

    old_booking_status = {offer.id: None for offer in offers}
    for offer in offers:
        for stock in offer.stocks:
            old_booking_status[offer.id] = [(b.id, b.status) for b in stock.bookings]

    yield

    for offer in offers:
        db.session.refresh(offer)

    new_names = {offer.id: offer.name for offer in offers}
    new_extra_data = {offer.id: offer.extraData for offer in offers}
    new_status = {offer.id: offer.status for offer in offers}

    new_booking_status = {offer.id: None for offer in offers}
    for offer in offers:
        for stock in offer.stocks:
            new_booking_status[offer.id] = [(b.id, b.status) for b in stock.bookings]

    assert old_names == new_names
    assert old_extra_data == new_extra_data
    assert old_status == new_status
    assert old_booking_status == new_booking_status


@contextlib.contextmanager
def assert_deactivated(*offers):
    yield

    for offer in offers:
        db.session.refresh(offer)
        assert not offer.isActive


@contextlib.contextmanager
def assert_updated_from_product(*offers_and_products):
    yield

    for offer, product in offers_and_products:
        db.session.refresh(offer)
        db.session.refresh(product)

        assert offer.name == product.name
        assert offer.extraData == product.extraData
        assert offer.ean == product.ean
        assert offer.productId == product.id
