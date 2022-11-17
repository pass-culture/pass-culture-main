import datetime

import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import factories as educational_factories
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers import factories as providers_factories
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users.backoffice import api as backoffice_api
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


ROLE_PERMISSIONS: dict[str, list[perm_models.Permissions]] = {
    "admin": [
        perm_models.Permissions.MANAGE_PERMISSIONS,
    ],
    "support-N1": [
        perm_models.Permissions.SEARCH_PUBLIC_ACCOUNT,
        perm_models.Permissions.READ_PUBLIC_ACCOUNT,
    ],
    "support-N2": [
        perm_models.Permissions.SEARCH_PUBLIC_ACCOUNT,
        perm_models.Permissions.READ_PUBLIC_ACCOUNT,
        perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT,
    ],
    "support-PRO": [
        perm_models.Permissions.SEARCH_PRO_ACCOUNT,
        perm_models.Permissions.READ_PRO_ENTITY,
        perm_models.Permissions.MANAGE_PRO_ENTITY,
    ],
    "fraude-conformite": [
        perm_models.Permissions.SEARCH_PUBLIC_ACCOUNT,
        perm_models.Permissions.READ_PUBLIC_ACCOUNT,
        perm_models.Permissions.SEARCH_PRO_ACCOUNT,
        perm_models.Permissions.READ_PRO_ENTITY,
        perm_models.Permissions.VALIDATE_OFFERER,
    ],
    "daf": [],
    "bizdev": [],
    "programmation": [],
    "product-management": [],
}


@pytest.fixture(scope="function", name="roles_with_permissions")
def roles_with_permissions_fixture() -> None:
    perms_in_db = {perm.name: perm for perm in perm_models.Permission.query.all()}

    for name, perms in ROLE_PERMISSIONS.items():
        role = perm_models.Role(name=name, permissions=[perms_in_db[perm.name] for perm in perms])
        db.session.add(role)

    db.session.commit()


@pytest.fixture(scope="function", name="legit_user")
def legit_user_fixture(roles_with_permissions: None) -> users_models.User:
    user = users_factories.UserFactory(isActive=True)

    user.backoffice_profile = perm_models.BackOfficeUserProfile(user=user)
    backoffice_api.upsert_roles(user, list(perm_models.Roles))

    db.session.commit()

    return user


@pytest.fixture(scope="function", name="authenticated_client")
def authenticated_client_fixture(client, legit_user):  # type: ignore
    return client.with_session_auth(legit_user.email)


@pytest.fixture(name="offerer")
def offerer_fixture():
    offerer = offerers_factories.OffererFactory(
        postalCode="46150", validationStatus=offerers_models.ValidationStatus.VALIDATED
    )
    return offerer


@pytest.fixture(name="venue_with_accepted_bank_info")
def venue_with_accepted_bank_info_fixture(offerer):
    venue = offerers_factories.VenueFactory(managingOfferer=offerer)
    finance_factories.BankInformationFactory(
        venue=venue,
        status=finance_models.BankInformationStatus.ACCEPTED,
    )
    return venue


@pytest.fixture(name="venue_with_draft_bank_info")
def venue_with_draft_bank_info_fixture(offerer):
    venue = offerers_factories.VenueFactory(managingOfferer=offerer)
    finance_factories.BankInformationFactory(
        venue=venue,
        status=finance_models.BankInformationStatus.DRAFT,
        applicationId=77,
    )
    return venue


@pytest.fixture(name="venue_with_rejected_bank_info")
def venue_with_rejected_bank_info_fixture(offerer):
    venue = offerers_factories.VenueFactory(managingOfferer=offerer)
    finance_factories.BankInformationFactory(
        venue=venue,
        status=finance_models.BankInformationStatus.REJECTED,
    )
    return venue


@pytest.fixture(name="venue_with_no_bank_info")
def venue_with_no_bank_info_fixture(offerer):
    venue = offerers_factories.VenueFactory(managingOfferer=offerer)
    return venue


@pytest.fixture(name="venue_with_accepted_self_reimbursement_point")
def venue_with_accepted_self_reimbursement_point_fixture(venue_with_accepted_bank_info):
    offerers_factories.VenueReimbursementPointLinkFactory(
        venue=venue_with_accepted_bank_info,
        reimbursementPoint=venue_with_accepted_bank_info,
    )
    return venue_with_accepted_bank_info


@pytest.fixture(name="venue_with_accepted_reimbursement_point")
def venue_with_accepted_reimbursement_point_fixture(
    venue_with_accepted_bank_info,
    venue_with_no_bank_info,
):
    offerers_factories.VenueReimbursementPointLinkFactory(
        venue=venue_with_no_bank_info,
        reimbursementPoint=venue_with_accepted_bank_info,
    )
    return venue_with_no_bank_info


@pytest.fixture(name="venue_with_expired_reimbursement_point")
def venue_with_expired_reimbursement_point_fixture(
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


@pytest.fixture(name="venue_with_educational_status")
def venue_with_educational_status_fixture(offerer):
    educational_status = offerers_factories.VenueEducationalStatusFactory()
    venue = offerers_factories.VenueFactory(
        managingOfferer=offerer,
        venueEducationalStatusId=educational_status.id,
    )
    return venue


@pytest.fixture(name="venue_with_no_contact")
def venue_with_no_contact_fixture():
    venue = offerers_factories.VenueFactory(contact=None)
    return venue


@pytest.fixture(name="venue_with_nor_contact_or_booking_email")
def venue_with_nor_contact_or_booking_email_fixture():
    venue = offerers_factories.VenueFactory(contact=None, bookingEmail=None)
    return venue


@pytest.fixture(name="venue_provider_with_last_sync")
def venue_provider_with_last_sync_fixture(venue_with_accepted_bank_info):
    venue_provider = providers_factories.VenueProviderFactory(
        venue=venue_with_accepted_bank_info,
        lastSyncDate=datetime.datetime.utcnow(),
    )
    return venue_provider


@pytest.fixture(name="random_venue")
def random_venue_fixture():
    venue = offerers_factories.VenueFactory(postalCode="46150")
    finance_factories.BankInformationFactory(venue=venue)
    return venue


@pytest.fixture(name="offerer_bank_info_with_application_id")
def offerer_bank_info_with_application_id_fixture(offerer):
    bank_info = finance_factories.BankInformationFactory(offerer=offerer, applicationId="42")
    return bank_info


@pytest.fixture(name="offerer_bank_info_with_no_application_id")
def offerer_bank_info_with_no_application_id_fixture(offerer):
    bank_info = finance_factories.BankInformationFactory(offerer=offerer, applicationId=None)
    return bank_info


@pytest.fixture(name="offerer_active_individual_offers")
def offerer_active_individual_offers_fixture(offerer, venue_with_accepted_bank_info):
    approved_offers = offers_factories.OfferFactory.create_batch(
        2,
        venue=venue_with_accepted_bank_info,
        isActive=True,
        validation=offers_models.OfferValidationStatus.APPROVED.value,
    )

    rejected_offer = offers_factories.OfferFactory(
        venue=venue_with_accepted_bank_info,
        isActive=True,
        validation=offers_models.OfferValidationStatus.REJECTED.value,
    )

    return approved_offers + [rejected_offer]


@pytest.fixture(name="offerer_inactive_individual_offers")
def offerer_inactive_individual_offers_fixture(offerer, venue_with_accepted_bank_info):
    approved_offers = offers_factories.OfferFactory.create_batch(
        3,
        venue=venue_with_accepted_bank_info,
        isActive=False,
        validation=offers_models.OfferValidationStatus.APPROVED.value,
    )

    rejected_offer = offers_factories.OfferFactory(
        venue=venue_with_accepted_bank_info,
        isActive=False,
        validation=offers_models.OfferValidationStatus.REJECTED.value,
    )

    return approved_offers + [rejected_offer]


@pytest.fixture(name="offerer_active_collective_offers")
def offerer_active_collective_offers_fixture(offerer, venue_with_accepted_bank_info):
    approved_offers = educational_factories.CollectiveOfferFactory.create_batch(
        4,
        venue=venue_with_accepted_bank_info,
        isActive=True,
        validation=offers_models.OfferValidationStatus.APPROVED.value,
    )

    rejected_offer = educational_factories.CollectiveOfferFactory(
        venue=venue_with_accepted_bank_info,
        isActive=True,
        validation=offers_models.OfferValidationStatus.REJECTED.value,
    )

    return approved_offers + [rejected_offer]


@pytest.fixture(name="offerer_inactive_collective_offers")
def offerer_inactive_collective_offers_fixture(offerer, venue_with_accepted_bank_info):
    approved_offers = educational_factories.CollectiveOfferFactory.create_batch(
        5,
        venue=venue_with_accepted_bank_info,
        isActive=False,
        validation=offers_models.OfferValidationStatus.APPROVED.value,
    )

    rejected_offer = educational_factories.CollectiveOfferFactory(
        venue=venue_with_accepted_bank_info,
        isActive=False,
        validation=offers_models.OfferValidationStatus.REJECTED.value,
    )

    return approved_offers + [rejected_offer]


@pytest.fixture(name="offerer_stocks")
def offerer_stocks_fixture(offerer_active_individual_offers):
    stocks = [offers_factories.StockFactory(offer=offer) for offer in offerer_active_individual_offers]
    return stocks


@pytest.fixture(name="individual_offerer_bookings")
def individual_offerer_bookings_fixture(offerer_stocks, venue_with_accepted_bank_info):
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


@pytest.fixture(name="collective_offerer_booking")
def collective_offerer_booking_fixture(venue_with_educational_status):
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


@pytest.fixture(name="collective_venue_booking")
def collective_venue_booking_fixture(venue_with_accepted_bank_info):
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


@pytest.fixture(name="offerer_tags")
def offerer_tags_fixture():
    tags = tuple(
        offerers_factories.OffererTagFactory(label=label)
        for label in ("Top acteur", "Collectivité", "Établissement public")
    )
    return tags


@pytest.fixture(name="offerers_to_be_validated")
def offerers_to_be_validated_fixture(offerer_tags):
    top_tag, collec_tag, public_tag = offerer_tags

    no_tag = offerers_factories.NotValidatedOffererFactory(name="A", siren="123001001", address=None)
    top = offerers_factories.NotValidatedOffererFactory(
        name="B", siren="123002002", validationStatus=offerers_models.ValidationStatus.PENDING
    )
    collec = offerers_factories.NotValidatedOffererFactory(name="C", siren="123003003")
    public = offerers_factories.NotValidatedOffererFactory(
        name="D", siren="123004004", validationStatus=offerers_models.ValidationStatus.PENDING
    )
    top_collec = offerers_factories.NotValidatedOffererFactory(name="E", siren="123005005")
    top_public = offerers_factories.NotValidatedOffererFactory(
        name="F", siren="123006006", validationStatus=offerers_models.ValidationStatus.PENDING
    )

    for offerer in (top, top_collec, top_public):
        offerers_factories.OffererTagMappingFactory(tagId=top_tag.id, offererId=offerer.id)
    for offerer in (collec, top_collec):
        offerers_factories.OffererTagMappingFactory(tagId=collec_tag.id, offererId=offerer.id)
    for offerer in (public, top_public):
        offerers_factories.OffererTagMappingFactory(tagId=public_tag.id, offererId=offerer.id)

    # Other statuses
    offerers_factories.OffererFactory(name="G")
    offerers_factories.NotValidatedOffererFactory(name="H", validationStatus=offerers_models.ValidationStatus.REJECTED)

    return (no_tag, top, collec, public, top_collec, top_public)


@pytest.fixture(name="user_offerer_to_be_validated")
def user_offerer_to_be_validated_fixture(offerer_tags):
    top_tag, collec_tag, public_tag = offerer_tags

    no_tag = offerers_factories.NotValidatedUserOffererFactory(user__email="a@example.com")
    top = offerers_factories.NotValidatedUserOffererFactory(
        user__email="b@example.com", validationStatus=offerers_models.ValidationStatus.PENDING
    )
    collec = offerers_factories.NotValidatedUserOffererFactory(user__email="c@example.com")
    public = offerers_factories.NotValidatedUserOffererFactory(
        user__email="d@example.com", validationStatus=offerers_models.ValidationStatus.PENDING
    )
    top_collec = offerers_factories.NotValidatedUserOffererFactory(user__email="e@example.com")
    top_public = offerers_factories.NotValidatedUserOffererFactory(
        user__email="f@example.com", validationStatus=offerers_models.ValidationStatus.PENDING
    )

    for user_offerer in (top, top_collec, top_public):
        offerers_factories.OffererTagMappingFactory(tagId=top_tag.id, offererId=user_offerer.offererId)
    for user_offerer in (collec, top_collec):
        offerers_factories.OffererTagMappingFactory(tagId=collec_tag.id, offererId=user_offerer.offererId)
    for user_offerer in (public, top_public):
        offerers_factories.OffererTagMappingFactory(tagId=public_tag.id, offererId=user_offerer.offererId)

    # Other status
    offerers_factories.UserOffererFactory(user__email="g@example.com")

    return (no_tag, top, collec, public, top_collec, top_public)
