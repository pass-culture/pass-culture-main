import contextlib

from pcapi.core.bookings import factories as bookings_factories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.bookings.models import BookingStatus
from pcapi.models.offer_mixin import OfferStatus
from pcapi.models import db
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.categories.subcategories_v2 as subcats


EAN = "1234567890987"


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


def build_offers(subcategories, eans=None, names=None):
    if eans is None:
        eans = [None for _ in subcategories]

    if names is None:
        names = [None for _ in subcategories]

    return [
        build_offer(subcategory_id, ean=eans[idx], name=names[idx])
        for idx, subcategory_id in enumerate(subcategories)
    ]


def build_random_offer(ean=None, name=None):
    if ean is None:
        ean = EAN

    if name is None:
        name = f"My movie {ean}"

    return bookings_factories.BookingFactory(
        stock__offer__name=name,
        stock__offer__extraData={},
        stock__offer__subcategoryId=subcats.CARTE_CINE_MULTISEANCES.id,
    ).stock.offer


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

