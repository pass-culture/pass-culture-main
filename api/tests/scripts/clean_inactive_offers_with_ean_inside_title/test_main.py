import contextlib

import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferStatus
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.scripts.clean_inactive_offers_with_ean_inside_title.main import reject_inactive_offers_with_ean_inside_title


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


def build_offer(subcategory_id, name=None, ean=None, with_booking=True, **extra_kwargs):
    if ean is None:
        ean = EAN

    if name is None:
        name = (f"My {subcategory_id} offer :: {ean}",)

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


class OfferWithEanInsideTitleTest:
    @pytest.mark.parametrize("subcategory_id", TARGET_SUBCATEGORIES)
    def test_inactive_offer_is_rejected(self, subcategory_id):
        offer = build_offer(subcategory_id, ean=EAN, stock__offer__isActive=False)
        build_product(ean=OTHER_EAN)

        with assert_rejected(offer):
            reject_inactive_offers_with_ean_inside_title()

    @pytest.mark.parametrize("subcategory_id", TARGET_SUBCATEGORIES)
    def test_inactive_offer_without_booking_is_rejected(self, subcategory_id):
        offer = build_offer(subcategory_id, ean=EAN, stock__offer__isActive=False)
        build_product(ean=OTHER_EAN)

        with assert_rejected(offer):
            reject_inactive_offers_with_ean_inside_title()

    @pytest.mark.parametrize("subcategory_id", TARGET_SUBCATEGORIES)
    def test_active_offer_is_ignored(self, subcategory_id):
        offer = build_offer(subcategory_id, ean=EAN)

        with assert_no_changes(offer):
            reject_inactive_offers_with_ean_inside_title()

    @pytest.mark.parametrize("subcategory_id", TARGET_SUBCATEGORIES)
    def test_rejected_offer_is_ignored(self, subcategory_id):
        offer = build_offer(subcategory_id, ean=EAN, stock__offer__validation=OfferValidationStatus.REJECTED)
        build_product(ean=OTHER_EAN)

        with assert_no_changes(offer):
            reject_inactive_offers_with_ean_inside_title()


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
    def test_offers_to_reject_and_offers_to_ignore(self, min_id, max_id, batch_size):
        to_reject_offers = [
            # inactive offer -> must be rejected
            build_offer(TARGET_SUBCATEGORIES[0], ean=EAN, stock__offer__isActive=False),
            # another inactive other -> must be rejected
            build_offer(TARGET_SUBCATEGORIES[1], ean=OTHER_EAN, stock__offer__isActive=False),
        ]

        to_ignore_offers = [
            # already rejected -> must be ignored
            build_offer(TARGET_SUBCATEGORIES[0], ean=EAN, stock__offer__validation=OfferValidationStatus.REJECTED),
            # active offer -> must be ignored
            build_offer(subcategories.ABO_PRATIQUE_ART.id, ean=EAN, stock__offer__isActive=True),
        ]

        if max_id == "max":
            max_id = offers_models.Offer.query.order_by(offers_models.Offer.id.desc()).first().id + 1

        if min_id == "min":
            min_id = offers_models.Offer.query.first().id - 1

        with assert_rejected(*to_reject_offers):
            with assert_no_changes(*to_ignore_offers):
                reject_inactive_offers_with_ean_inside_title(min_id=min_id, max_id=max_id, batch_size=batch_size)


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
def assert_rejected(*offers):
    old_names = {offer.id: offer.name for offer in offers}
    old_extra_data = {offer.id: offer.extraData for offer in offers}

    yield

    bookings_count = 0

    for offer in offers:
        db.session.refresh(offer)

        assert offer.status == OfferStatus.REJECTED
        assert offer.name == old_names[offer.id]
        assert offer.extraData == old_extra_data[offer.id]

        bookings = [booking for stock in offer.stocks for booking in stock.bookings]
        bookings_count += len(bookings)
        for booking in bookings:
            assert booking.status == BookingStatus.CANCELLED

    assert len(mails_testing.outbox) == bookings_count

    found_templates = {row["template"]["id_prod"] for row in mails_testing.outbox}
    expected_templates = {
        TransactionalEmail.BOOKING_CANCELLATION_BY_PRO_TO_BENEFICIARY.value.id_prod,
    }

    assert found_templates <= expected_templates
