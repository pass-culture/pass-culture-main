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
from pcapi.scripts.clean_offer_titles_with_eans.main import run


pytestmark = pytest.mark.usefixtures("db_session")


EAN = "1234567890987"
EXTRA_DATA = {"ean": EAN, "author": "someone"}

TARGET_SUBCATEGORIES = [
    subcategories.LIVRE_PAPIER.id,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id,
]


def build_offer(subcategory_id, name=None, ean=None):
    if ean is None:
        ean = EAN

    if name is None:
        name = (f"My {subcategory_id} offer :: {ean}",)

    return bookings_factories.BookingFactory(
        stock__offer__name=name,
        stock__offer__extraData={},
        stock__offer__subcategoryId=subcategory_id,
    ).stock.offer


def build_offers(eans, subcategories):
    return [build_offer(subcategory_id, ean=eans[idx]) for idx, subcategory_id in enumerate(subcategories)]


def build_random_offer(ean=None, name=None):
    if ean is None:
        ean = EAN

    if name is None:
        name = f"My movie {ean}"

    return bookings_factories.BookingFactory(
        stock__offer__name=name,
        stock__offer__extraData={},
        stock__offer__subcategoryId=subcategories.CARTE_CINE_MULTISEANCES.id,
    ).stock.offer


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
    def test_compatible_offer_is_updated_from_product(self, subcategory_id):
        offer = build_offer(subcategory_id)
        product = build_product()

        with assert_offers_updated_from_products((offer, product)):
            run()

    @pytest.mark.parametrize("subcategory_id", TARGET_SUBCATEGORIES)
    def test_targeted_offer_without_ean_inside_title_is_ignored(self, subcategory_id):
        offer = build_offer(subcategory_id, name="simple name")

        with assert_no_changes(offer):
            run()

    def test_not_targeted_offer_subcategory_is_ignored(self):
        offer = build_random_offer()

        with assert_no_changes(offer):
            run()

    @pytest.mark.parametrize("subcategory_id", TARGET_SUBCATEGORIES)
    def test_incompatible_offer_with_ean_inside_title_is_rejected(self, subcategory_id):
        offer = build_offer(subcategory_id)
        build_product(incompatible=True)

        with assert_rejected(offer):
            run()

    @pytest.mark.parametrize("subcategory_id", TARGET_SUBCATEGORIES)
    def test_offer_with_unknown_ean_inside_title_is_rejected(self, subcategory_id):
        offer = build_offer(subcategory_id)
        build_product(ean="0000000000000")

        with assert_rejected(offer):
            run()

    def test_offers_to_update_and_ignore_and_reject(self):
        known_eans = ["0000000000001", "0000000000002", "0000000000003"]
        unknown_eans = ["1111111111111", "1111111111112", "1111111111113"]
        gcu_incompatible_eans = ["2222222222221", "2222222222222", "2222222222223"]

        offers_to_update = build_offers(known_eans, TARGET_SUBCATEGORIES)
        valid_products = [build_product(ean=ean) for ean in known_eans]

        offers_to_reject = build_offers(unknown_eans, TARGET_SUBCATEGORIES)
        offers_to_reject += build_offers(gcu_incompatible_eans, TARGET_SUBCATEGORIES)
        [build_product(incompatible=True, ean=ean) for ean in gcu_incompatible_eans]

        offers_to_ignore = [
            build_random_offer(name="some offer to ignore"),
            build_random_offer(name="another offer to ignore"),
        ]

        with assert_offers_updated_from_products(*zip(offers_to_update, valid_products)):
            with assert_no_changes(*offers_to_ignore):
                with assert_rejected(*offers_to_reject):
                    run()


@contextlib.contextmanager
def assert_offers_updated_from_products(*offers_and_products):
    for row in offers_and_products:
        offer, product = row
        assert offer.name != product.name
        assert offer.extraData != product.extraData

    yield

    for row in offers_and_products:
        offer, product = row

        db.session.refresh(offer)
        db.session.refresh(product)

        assert offer.name == product.name
        assert offer.extraData == product.extraData


@contextlib.contextmanager
def assert_no_changes(*offers):
    old_names = {offer.id: offer.name for offer in offers}
    old_extra_data = {offer.id: offer.extraData for offer in offers}

    old_booking_status = {offer.id: None for offer in offers}
    for offer in offers:
        for stock in offer.stocks:
            old_booking_status[offer.id] = [(b.id, b.status) for b in stock.bookings]

    yield

    for offer in offers:
        db.session.refresh(offer)

    new_names = {offer.id: offer.name for offer in offers}
    new_extra_data = {offer.id: offer.extraData for offer in offers}

    new_booking_status = {offer.id: None for offer in offers}
    for offer in offers:
        for stock in offer.stocks:
            new_booking_status[offer.id] = [(b.id, b.status) for b in stock.bookings]

    assert old_names == new_names
    assert old_extra_data == new_extra_data
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

    assert len(mails_testing.outbox) == len(offers) + bookings_count

    found_templates = {row["template"]["id_prod"] for row in mails_testing.outbox}
    expected_templates = {
        TransactionalEmail.OFFER_VALIDATED_TO_REJECTED_TO_PRO.value.id_prod,
        TransactionalEmail.OFFER_REJECTION_TO_PRO.value.id_prod,
        TransactionalEmail.OFFER_PENDING_TO_REJECTED_TO_PRO.value.id_prod,
        TransactionalEmail.BOOKING_CANCELLATION_BY_PRO_TO_BENEFICIARY.value.id_prod,
    }

    assert found_templates <= expected_templates
