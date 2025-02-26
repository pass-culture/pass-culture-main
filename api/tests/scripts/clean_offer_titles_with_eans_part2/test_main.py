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
from pcapi.scripts.clean_offer_titles_with_eans_part2.main import handle_offers_with_ean_inside_title


pytestmark = pytest.mark.usefixtures("db_session")


EAN = "0000000000001"
OTHER_EAN = "0000000000002"
INCOMPATIBLE_EAN = "0000000000003"

EXTRA_DATA = {"ean": EAN, "author": "someone"}

TARGET_SUBCATEGORIES = [
    subcategories.SUPPORT_PHYSIQUE_FILM.id,
    subcategories.MATERIEL_ART_CREATIF.id,
    subcategories.ACHAT_INSTRUMENT.id,
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


class OfferWithEANAsTitleTest:
    @pytest.mark.parametrize("subcategory_id", TARGET_SUBCATEGORIES)
    def test_offer_from_targetted_category_is_rejected(self, subcategory_id):
        offer = build_offer(subcategory_id, name=EAN)

        with assert_rejected(offer):
            handle_offers_with_ean_inside_title()

    @pytest.mark.parametrize("subcategory_id", TARGET_SUBCATEGORIES)
    def test_offer_from_targetted_category_and_without_booking_is_rejected(self, subcategory_id):
        offer = build_offer(subcategory_id, name=EAN, with_booking=False)

        with assert_rejected(offer):
            handle_offers_with_ean_inside_title()

    @pytest.mark.parametrize("subcategory_id", TARGET_SUBCATEGORIES)
    def test_rejected_offer_from_targetted_category_is_ignored(self, subcategory_id):
        offer = build_offer(subcategory_id, name=EAN, stock__offer__validation=OfferValidationStatus.REJECTED)

        with assert_no_changes(offer):
            handle_offers_with_ean_inside_title()

    def test_offer_not_from_targetted_category_is_ignored(self):
        offer = build_offer(subcategories.ABO_PRATIQUE_ART.id, name=EAN)

        with assert_no_changes(offer):
            handle_offers_with_ean_inside_title()


class OfferEanInsideTitleTest:
    @pytest.mark.parametrize("subcategory_id", TARGET_SUBCATEGORIES)
    def test_offer_from_targetted_category_is_updated(self, subcategory_id):
        offer = build_offer(subcategory_id, name=f"A title with ean {EAN} inside")

        with assert_name_and_ean_updated(offer):
            handle_offers_with_ean_inside_title()

        assert offer.name == "A title with ean inside"

    @pytest.mark.parametrize(
        "name, expected_name",
        [
            (f"A title with ean {EAN} inside", "A title with ean inside"),
            (f"A title with ean #{EAN} inside", "A title with ean inside"),
            (f"ean at the end {EAN}", "ean at the end"),
            (f"ean at the end - {EAN}", "ean at the end"),
            (f"ean at the end -{EAN}", "ean at the end"),
        ],
    )
    def test_offer_is_updated_no_matter_where_and_how_is_the_ean(self, name, expected_name):
        offer = build_offer(TARGET_SUBCATEGORIES[0], name=name)

        with assert_name_and_ean_updated(offer):
            handle_offers_with_ean_inside_title()

        assert offer.name == expected_name

    @pytest.mark.parametrize("subcategory_id", TARGET_SUBCATEGORIES)
    def test_rejected_offer_from_targetted_category_is_ignored(self, subcategory_id):
        offer = build_offer(
            subcategory_id,
            name=f"A title with ean {EAN} inside",
            stock__offer__validation=OfferValidationStatus.REJECTED,
        )

        with assert_no_changes(offer):
            handle_offers_with_ean_inside_title()

    def test_offer_not_from_targetted_category_is_ignored(self):
        offer = build_offer(subcategories.ABO_PRATIQUE_ART.id, name=f"A title with ean {EAN} inside")

        with assert_no_changes(offer):
            handle_offers_with_ean_inside_title()


class HandleOffersWithEanInsideTitleTest:
    def test_offers_to_reject_update_and_ignore(self):
        to_reject_offers = [
            # name is an EAN -> must be rejected
            build_offer(TARGET_SUBCATEGORIES[0], name=EAN),
            build_offer(TARGET_SUBCATEGORIES[1], name=OTHER_EAN),
        ]

        to_update_offers = [
            build_offer(TARGET_SUBCATEGORIES[0], name=f"title with {EAN}"),
            build_offer(TARGET_SUBCATEGORIES[1], name=f"another title with {EAN}"),
        ]

        to_ignore_offers = [
            # not a targetted category -> must be ignored (even is name is the EAN)
            build_offer(subcategories.ABO_PRATIQUE_ART.id, name=EAN),
            # already rejected -> must be ignored
            build_offer(TARGET_SUBCATEGORIES[0], name=EAN, stock__offer__validation=OfferValidationStatus.REJECTED),
        ]

        with assert_rejected(*to_reject_offers):
            with assert_no_changes(*to_ignore_offers):
                with assert_name_and_ean_updated(*to_update_offers):
                    handle_offers_with_ean_inside_title()


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
def assert_name_and_ean_updated(*offers):
    old_names = {offer.id: offer.name for offer in offers}
    old_eans = {offer.id: offer.ean for offer in offers}
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
    new_eans = {offer.id: offer.ean for offer in offers}
    new_extra_data = {offer.id: offer.extraData for offer in offers}
    new_status = {offer.id: offer.status for offer in offers}

    new_booking_status = {offer.id: None for offer in offers}
    for offer in offers:
        for stock in offer.stocks:
            new_booking_status[offer.id] = [(b.id, b.status) for b in stock.bookings]

    for offer_id, old_name in old_names.items():
        assert new_names[offer_id] != old_name

    for offer_id, old_ean in old_eans.items():
        assert new_eans[offer_id] != old_ean

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
