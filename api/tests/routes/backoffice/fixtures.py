# pylint: disable=redefined-outer-name
import datetime

import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import factories as educational_factories
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import factories as providers_factories


__all__ = (
    "offerer",
    "venue_with_accepted_bank_info",
    "venue_with_draft_bank_info",
    "venue_with_rejected_bank_info",
    "venue_with_no_bank_info",
    "venue_with_accepted_self_reimbursement_point",
    "venue_with_accepted_reimbursement_point",
    "venue_with_expired_reimbursement_point",
    "venue_with_educational_status",
    "venue_with_no_contact",
    "venue_with_nor_contact_or_booking_email",
    "random_venue",
    "venue_provider_with_last_sync",
    "offerer_bank_info_with_application_id",
    "offerer_bank_info_with_no_application_id",
    "offerer_active_individual_offers",
    "offerer_inactive_individual_offers",
    "offerer_active_collective_offers",
    "offerer_inactive_collective_offers",
    "offerer_stocks",
    "individual_offerer_bookings",
    "collective_offerer_booking",
    "collective_venue_booking",
    "offerer_tags",
    "offerers_to_be_validated",
)


@pytest.fixture
def offerer():
    offerer = offerers_factories.OffererFactory(postalCode="46150")
    return offerer


@pytest.fixture
def venue_with_accepted_bank_info(offerer):
    venue = offerers_factories.VenueFactory(managingOfferer=offerer)
    finance_factories.BankInformationFactory(
        venue=venue,
        status=finance_models.BankInformationStatus.ACCEPTED,
    )
    return venue


@pytest.fixture
def venue_with_draft_bank_info(offerer):
    venue = offerers_factories.VenueFactory(managingOfferer=offerer)
    finance_factories.BankInformationFactory(
        venue=venue,
        status=finance_models.BankInformationStatus.DRAFT,
        applicationId=77,
    )
    return venue


@pytest.fixture
def venue_with_rejected_bank_info(offerer):
    venue = offerers_factories.VenueFactory(managingOfferer=offerer)
    finance_factories.BankInformationFactory(
        venue=venue,
        status=finance_models.BankInformationStatus.REJECTED,
    )
    return venue


@pytest.fixture
def venue_with_no_bank_info(offerer):
    venue = offerers_factories.VenueFactory(managingOfferer=offerer)
    return venue


@pytest.fixture
def venue_with_accepted_self_reimbursement_point(venue_with_accepted_bank_info):
    offerers_factories.VenueReimbursementPointLinkFactory(
        venue=venue_with_accepted_bank_info,
        reimbursementPoint=venue_with_accepted_bank_info,
    )
    return venue_with_accepted_bank_info


@pytest.fixture
def venue_with_accepted_reimbursement_point(
    venue_with_accepted_bank_info,
    venue_with_no_bank_info,
):
    offerers_factories.VenueReimbursementPointLinkFactory(
        venue=venue_with_no_bank_info,
        reimbursementPoint=venue_with_accepted_bank_info,
    )
    return venue_with_no_bank_info


@pytest.fixture
def venue_with_expired_reimbursement_point(
    offerer,
    venue_with_accepted_bank_info,
):
    venue = offerers_factories.VenueFactory(managingOfferer=offerer)
    offerers_factories.VenueReimbursementPointLinkFactory(
        venue=venue,
        reimbursementPoint=venue_with_accepted_bank_info,
        timespan=[
            datetime.datetime.utcnow() - datetime.timedelta(days=365),
            datetime.datetime.utcnow() - datetime.timedelta(days=1),
        ],
    )
    return venue


@pytest.fixture
def venue_with_educational_status(offerer):
    educational_status = offerers_factories.VenueEducationalStatusFactory()
    venue = offerers_factories.VenueFactory(
        managingOfferer=offerer,
        venueEducationalStatusId=educational_status.id,
    )
    return venue


@pytest.fixture
def venue_with_no_contact():
    venue = offerers_factories.VenueFactory(contact=None)
    return venue


@pytest.fixture
def venue_with_nor_contact_or_booking_email():
    venue = offerers_factories.VenueFactory(contact=None, bookingEmail=None)
    return venue


@pytest.fixture
def venue_provider_with_last_sync(venue_with_accepted_bank_info):
    venue_provider = providers_factories.VenueProviderFactory(
        venue=venue_with_accepted_bank_info,
        lastSyncDate=datetime.datetime.utcnow(),
    )
    return venue_provider


@pytest.fixture
def random_venue():
    venue = offerers_factories.VenueFactory(postalCode="46150")
    finance_factories.BankInformationFactory(venue=venue)
    return venue


@pytest.fixture
def offerer_bank_info_with_application_id(offerer):
    bank_info = finance_factories.BankInformationFactory(offerer=offerer, applicationId="42")
    return bank_info


@pytest.fixture
def offerer_bank_info_with_no_application_id(offerer):
    bank_info = finance_factories.BankInformationFactory(offerer=offerer, applicationId=None)
    return bank_info


@pytest.fixture
def offerer_active_individual_offers(offerer, venue_with_accepted_bank_info):
    offers = [
        offers_factories.OfferFactory(
            venue=venue_with_accepted_bank_info,
            isActive=True,
            validation=offers_models.OfferValidationStatus.APPROVED.value,
        )
        for _ in range(3)
    ] + [
        offers_factories.OfferFactory(
            venue=venue_with_accepted_bank_info,
            isActive=True,
            validation=offers_models.OfferValidationStatus.REJECTED.value,
        )
        for _ in range(1)
    ]
    return offers


@pytest.fixture
def offerer_inactive_individual_offers(offerer, venue_with_accepted_bank_info):
    offers = [
        offers_factories.OfferFactory(
            venue=venue_with_accepted_bank_info,
            isActive=False,
            validation=offers_models.OfferValidationStatus.APPROVED.value,
        )
        for _ in range(4)
    ] + [
        offers_factories.OfferFactory(
            venue=venue_with_accepted_bank_info,
            isActive=False,
            validation=offers_models.OfferValidationStatus.REJECTED.value,
        )
        for _ in range(1)
    ]
    return offers


@pytest.fixture
def offerer_active_collective_offers(offerer, venue_with_accepted_bank_info):
    offers = [
        educational_factories.CollectiveOfferFactory(
            venue=venue_with_accepted_bank_info,
            isActive=True,
            validation=offers_models.OfferValidationStatus.APPROVED.value,
        )
        for _ in range(5)
    ] + [
        educational_factories.CollectiveOfferFactory(
            venue=venue_with_accepted_bank_info,
            isActive=True,
            validation=offers_models.OfferValidationStatus.REJECTED.value,
        )
        for _ in range(1)
    ]
    return offers


@pytest.fixture
def offerer_inactive_collective_offers(offerer, venue_with_accepted_bank_info):
    offers = [
        educational_factories.CollectiveOfferFactory(
            venue=venue_with_accepted_bank_info,
            isActive=False,
            validation=offers_models.OfferValidationStatus.APPROVED.value,
        )
        for _ in range(6)
    ] + [
        educational_factories.CollectiveOfferFactory(
            venue=venue_with_accepted_bank_info,
            isActive=False,
            validation=offers_models.OfferValidationStatus.REJECTED.value,
        )
        for _ in range(1)
    ]
    return offers


@pytest.fixture
def offerer_stocks(offerer_active_individual_offers):
    stocks = [offers_factories.StockFactory(offer=offer) for offer in offerer_active_individual_offers]
    return stocks


@pytest.fixture
def individual_offerer_bookings(offerer_stocks):
    used_simple = bookings_factories.BookingFactory(
        status=bookings_models.BookingStatus.USED,
        quantity=1,
        amount=10,
        stock=offerer_stocks[0],
    )
    confirmed_duo = bookings_factories.BookingFactory(
        status=bookings_models.BookingStatus.CONFIRMED,
        quantity=2,
        amount=10,
        stock=offerer_stocks[1],
    )
    cancelled = bookings_factories.BookingFactory(
        status=bookings_models.BookingStatus.CANCELLED,
        venue=venue_with_accepted_bank_info,
        stock=offerer_stocks[2],
    )
    return [used_simple, confirmed_duo, cancelled]


@pytest.fixture
def collective_offerer_booking(venue_with_educational_status):
    stock = educational_factories.CollectiveStockFactory(price=1664)
    used = educational_factories.UsedCollectiveBookingFactory(
        collectiveStock=stock,
        offerer=venue_with_educational_status.managingOfferer,
    )
    cancelled = educational_factories.CancelledCollectiveBookingFactory(
        collectiveStock=stock,
        offerer=venue_with_educational_status.managingOfferer,
    )
    return used, cancelled


@pytest.fixture
def collective_venue_booking(venue_with_accepted_bank_info):
    educational_status = offerers_factories.VenueEducationalStatusFactory()
    venue_with_accepted_bank_info.venueEducationalStatusId = educational_status.id
    stock = educational_factories.CollectiveStockFactory(price=42)
    used = educational_factories.UsedCollectiveBookingFactory(
        collectiveStock=stock,
        venue=venue_with_accepted_bank_info,
    )
    cancelled = educational_factories.CancelledCollectiveBookingFactory(
        collectiveStock=stock,
        venue=venue_with_accepted_bank_info,
    )
    return used, cancelled


@pytest.fixture
def offerer_tags():
    tags = tuple(
        offerers_factories.OffererTagFactory(label=label)
        for label in ("Top acteur", "Collectivité", "Établissement public")
    )
    return tags


@pytest.fixture
def offerers_to_be_validated(offerer_tags):
    top_tag, collec_tag, public_tag = offerer_tags

    no_tag = offerers_factories.NotValidatedOffererFactory(name="A")
    top = offerers_factories.NotValidatedOffererFactory(name="B")
    collec = offerers_factories.NotValidatedOffererFactory(name="C")
    public = offerers_factories.NotValidatedOffererFactory(name="D")
    top_collec = offerers_factories.NotValidatedOffererFactory(name="E")
    top_public = offerers_factories.NotValidatedOffererFactory(name="F")

    for offerer in (top, top_collec, top_public):
        offerers_factories.OffererTagMappingFactory(tagId=top_tag.id, offererId=offerer.id)
    for offerer in (collec, top_collec):
        offerers_factories.OffererTagMappingFactory(tagId=collec_tag.id, offererId=offerer.id)
    for offerer in (public, top_public):
        offerers_factories.OffererTagMappingFactory(tagId=public_tag.id, offererId=offerer.id)

    return (no_tag, top, collec, public, top_collec, top_public)
