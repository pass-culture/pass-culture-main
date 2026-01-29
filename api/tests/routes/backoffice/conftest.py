import datetime
from typing import TYPE_CHECKING

import factory
import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import factories as educational_factories
from pcapi.core.finance import factories as finance_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import api as perm_api
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers import factories as providers_factories
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users.backoffice import api as backoffice_api
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.utils import date as date_utils


if TYPE_CHECKING:
    from pcapi.tests.conftest import TestClient


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


ROLE_PERMISSIONS: dict[str, list[perm_models.Permissions]] = {
    "admin": [
        perm_models.Permissions.READ_PERMISSIONS,
        perm_models.Permissions.READ_ADMIN_ACCOUNTS,
        perm_models.Permissions.MANAGE_ADMIN_ACCOUNTS,
        perm_models.Permissions.READ_TAGS,
        perm_models.Permissions.MANAGE_TAGS_N2,
        perm_models.Permissions.MANAGE_ACCOUNT_TAGS_N2,
        perm_models.Permissions.MANAGE_OFFERER_TAG,
        perm_models.Permissions.MANAGE_OFFERS_AND_VENUES_TAGS,
        perm_models.Permissions.PRO_FRAUD_ACTIONS,
        perm_models.Permissions.BENEFICIARY_FRAUD_ACTIONS,
        perm_models.Permissions.ANONYMIZE_PUBLIC_ACCOUNT,
        perm_models.Permissions.READ_USER_PROFILE_REFRESH_CAMPAIGN,
        perm_models.Permissions.MANAGE_USER_PROFILE_REFRESH_CAMPAIGN,
    ],
    "support_n1": [
        perm_models.Permissions.READ_PUBLIC_ACCOUNT,
    ],
    "support_n2": [
        perm_models.Permissions.READ_PUBLIC_ACCOUNT,
        perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT,
        perm_models.Permissions.BENEFICIARY_MANUAL_REVIEW,
        perm_models.Permissions.READ_BENEFICIARY_BONUS_CREDIT,
        perm_models.Permissions.REQUEST_BENEFICIARY_BONUS_CREDIT,
        perm_models.Permissions.SUSPEND_USER,
        perm_models.Permissions.EXTRACT_PUBLIC_ACCOUNT,
        perm_models.Permissions.MANAGE_ACCOUNT_UPDATE_REQUEST,
        perm_models.Permissions.CREATE_INCIDENTS,
        perm_models.Permissions.READ_FRAUDULENT_BOOKING_INFO,
    ],
    "support_n3": [
        perm_models.Permissions.ANONYMIZE_PUBLIC_ACCOUNT,
    ],
    "support_pro": [
        perm_models.Permissions.READ_PRO_ENTITY,
        perm_models.Permissions.READ_PRO_ENTREPRISE_INFO,
        perm_models.Permissions.READ_PRO_AE_INFO,
        perm_models.Permissions.MANAGE_PRO_ENTITY,
        perm_models.Permissions.DELETE_PRO_ENTITY,
        perm_models.Permissions.CREATE_PRO_ENTITY,
        perm_models.Permissions.CONNECT_AS_PRO,
        perm_models.Permissions.MANAGE_BOOKINGS,
        perm_models.Permissions.READ_BOOKINGS,
        perm_models.Permissions.READ_OFFERS,
        perm_models.Permissions.READ_REIMBURSEMENT_RULES,
        perm_models.Permissions.READ_INCIDENTS,
        perm_models.Permissions.READ_TECH_PARTNERS,
        perm_models.Permissions.CREATE_INCIDENTS,
        perm_models.Permissions.READ_FRAUDULENT_BOOKING_INFO,
        perm_models.Permissions.CLOSE_OFFERER,
        perm_models.Permissions.READ_NON_PAYMENT_NOTICES,
    ],
    "support_pro_n2": [
        perm_models.Permissions.MOVE_SIRET,
        perm_models.Permissions.ADVANCED_PRO_SUPPORT,
        perm_models.Permissions.MANAGE_OFFERS_AND_VENUES_TAGS,
        perm_models.Permissions.CREATE_INCIDENTS,
        perm_models.Permissions.MANAGE_INCIDENTS,
        perm_models.Permissions.READ_NON_PAYMENT_NOTICES,
        perm_models.Permissions.MANAGE_NON_PAYMENT_NOTICES,
    ],
    "support_partenaires_techniques": [
        perm_models.Permissions.READ_PRO_ENTITY,
        perm_models.Permissions.MANAGE_PRO_ENTITY,
        perm_models.Permissions.CONNECT_AS_PRO,
        perm_models.Permissions.READ_BOOKINGS,
        perm_models.Permissions.READ_OFFERS,
        perm_models.Permissions.READ_REIMBURSEMENT_RULES,
        perm_models.Permissions.READ_INCIDENTS,
        perm_models.Permissions.READ_TECH_PARTNERS,
        perm_models.Permissions.MANAGE_TECH_PARTNERS,
    ],
    "fraude_conformite": [
        perm_models.Permissions.PRO_FRAUD_ACTIONS,
        perm_models.Permissions.READ_FRAUDULENT_BOOKING_INFO,
        perm_models.Permissions.MANAGE_FRAUDULENT_BOOKING_INFO,
        perm_models.Permissions.READ_PUBLIC_ACCOUNT,
        perm_models.Permissions.READ_PRO_ENTITY,
        perm_models.Permissions.READ_PRO_ENTREPRISE_INFO,
        perm_models.Permissions.READ_PRO_SENSITIVE_INFO,
        perm_models.Permissions.READ_PRO_AE_INFO,
        perm_models.Permissions.VALIDATE_OFFERER,
        perm_models.Permissions.MANAGE_BOOKINGS,
        perm_models.Permissions.READ_BOOKINGS,
        perm_models.Permissions.MANAGE_OFFERS,
        perm_models.Permissions.READ_OFFERS,
        perm_models.Permissions.MULTIPLE_OFFERS_ACTIONS,
        perm_models.Permissions.CREATE_INCIDENTS,
    ],
    "fraude_jeunes": [
        perm_models.Permissions.READ_PUBLIC_ACCOUNT,
        perm_models.Permissions.SUSPEND_USER,
        perm_models.Permissions.UNSUSPEND_USER,
        perm_models.Permissions.BENEFICIARY_FRAUD_ACTIONS,
        perm_models.Permissions.BENEFICIARY_MANUAL_REVIEW,
        perm_models.Permissions.READ_BENEFICIARY_BONUS_CREDIT,
        perm_models.Permissions.REQUEST_BENEFICIARY_BONUS_CREDIT,
        perm_models.Permissions.MANAGE_BOOKINGS,
        perm_models.Permissions.READ_BOOKINGS,
        perm_models.Permissions.READ_FRAUDULENT_BOOKING_INFO,
        perm_models.Permissions.MANAGE_FRAUDULENT_BOOKING_INFO,
    ],
    "daf": [
        perm_models.Permissions.READ_REIMBURSEMENT_RULES,
        perm_models.Permissions.READ_INCIDENTS,
        perm_models.Permissions.CREATE_INCIDENTS,
        perm_models.Permissions.MANAGE_INCIDENTS,
    ],
    "responsable_daf": [
        perm_models.Permissions.READ_REIMBURSEMENT_RULES,
        perm_models.Permissions.CREATE_REIMBURSEMENT_RULES,
    ],
    "partenaire_technique": [
        perm_models.Permissions.READ_TECH_PARTNERS,
        perm_models.Permissions.MANAGE_TECH_PARTNERS,
    ],
    "programmation_market": [
        perm_models.Permissions.MANAGE_ACCOUNT_TAGS,
        perm_models.Permissions.READ_PUBLIC_ACCOUNT,
        perm_models.Permissions.READ_PRO_ENTITY,
        perm_models.Permissions.MANAGE_PRO_ENTITY,
        perm_models.Permissions.CONNECT_AS_PRO,
        perm_models.Permissions.VALIDATE_OFFERER,
        perm_models.Permissions.MANAGE_OFFERS,
        perm_models.Permissions.READ_OFFERS,
        perm_models.Permissions.MULTIPLE_OFFERS_ACTIONS,
        perm_models.Permissions.READ_TAGS,
        perm_models.Permissions.MANAGE_OFFERS_AND_VENUES_TAGS,
        perm_models.Permissions.READ_CHRONICLE,
        perm_models.Permissions.MANAGE_CHRONICLE,
        perm_models.Permissions.READ_HIGHLIGHT,
        perm_models.Permissions.MANAGE_HIGHLIGHT,
    ],
    "homologation": [
        perm_models.Permissions.READ_PRO_ENTITY,
        perm_models.Permissions.READ_PRO_ENTREPRISE_INFO,
        perm_models.Permissions.READ_PRO_SENSITIVE_INFO,
        perm_models.Permissions.MANAGE_PRO_ENTITY,
        perm_models.Permissions.CONNECT_AS_PRO,
        perm_models.Permissions.VALIDATE_OFFERER,
        perm_models.Permissions.READ_OFFERS,
    ],
    "homologation_pro": [
        perm_models.Permissions.CREATE_PRO_ENTITY,
    ],
    "product_management": [
        perm_models.Permissions.FEATURE_FLIPPING,
        perm_models.Permissions.CONNECT_AS_PRO,
    ],
    "charge_developpement": [
        perm_models.Permissions.READ_PRO_ENTITY,
        perm_models.Permissions.MANAGE_OFFERS_AND_VENUES_TAGS,
        perm_models.Permissions.READ_SPECIAL_EVENTS,
        perm_models.Permissions.MANAGE_SPECIAL_EVENTS,
        perm_models.Permissions.READ_TECH_PARTNERS,
    ],
    "lecture_seule": [
        perm_models.Permissions.READ_ADMIN_ACCOUNTS,
        perm_models.Permissions.READ_PUBLIC_ACCOUNT,
        perm_models.Permissions.READ_PRO_ENTITY,
        perm_models.Permissions.READ_BOOKINGS,
        perm_models.Permissions.READ_OFFERS,
        perm_models.Permissions.READ_SPECIAL_EVENTS,
        perm_models.Permissions.READ_TAGS,
        perm_models.Permissions.READ_TECH_PARTNERS,
        perm_models.Permissions.READ_USER_PROFILE_REFRESH_CAMPAIGN,
    ],
    "qa": [],
    "global_access": [
        perm_models.Permissions.READ_PERMISSIONS,
        perm_models.Permissions.READ_ADMIN_ACCOUNTS,
        perm_models.Permissions.MANAGE_ADMIN_ACCOUNTS,
        perm_models.Permissions.FEATURE_FLIPPING,
        perm_models.Permissions.PRO_FRAUD_ACTIONS,
        perm_models.Permissions.BENEFICIARY_FRAUD_ACTIONS,
        perm_models.Permissions.BENEFICIARY_MANUAL_REVIEW,
        perm_models.Permissions.READ_BENEFICIARY_BONUS_CREDIT,
        perm_models.Permissions.REQUEST_BENEFICIARY_BONUS_CREDIT,
        perm_models.Permissions.READ_PUBLIC_ACCOUNT,
        perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT,
        perm_models.Permissions.SUSPEND_USER,
        perm_models.Permissions.UNSUSPEND_USER,
        perm_models.Permissions.READ_PRO_ENTITY,
        perm_models.Permissions.READ_PRO_ENTREPRISE_INFO,
        perm_models.Permissions.READ_PRO_SENSITIVE_INFO,
        perm_models.Permissions.READ_PRO_AE_INFO,
        perm_models.Permissions.MANAGE_PRO_ENTITY,
        perm_models.Permissions.DELETE_PRO_ENTITY,
        perm_models.Permissions.CREATE_PRO_ENTITY,
        perm_models.Permissions.CONNECT_AS_PRO,
        perm_models.Permissions.MOVE_SIRET,
        perm_models.Permissions.ADVANCED_PRO_SUPPORT,
        perm_models.Permissions.MANAGE_BOOKINGS,
        perm_models.Permissions.READ_BOOKINGS,
        perm_models.Permissions.READ_OFFERS,
        perm_models.Permissions.MANAGE_OFFERS,
        perm_models.Permissions.MULTIPLE_OFFERS_ACTIONS,
        perm_models.Permissions.VALIDATE_OFFERER,
        perm_models.Permissions.READ_TAGS,
        perm_models.Permissions.MANAGE_OFFERER_TAG,
        perm_models.Permissions.MANAGE_TAGS_N2,
        perm_models.Permissions.MANAGE_ACCOUNT_TAGS_N2,
        perm_models.Permissions.MANAGE_OFFERS_AND_VENUES_TAGS,
        perm_models.Permissions.READ_REIMBURSEMENT_RULES,
        perm_models.Permissions.CREATE_REIMBURSEMENT_RULES,
        perm_models.Permissions.READ_TECH_PARTNERS,
        perm_models.Permissions.MANAGE_TECH_PARTNERS,
        perm_models.Permissions.READ_SPECIAL_EVENTS,
        perm_models.Permissions.MANAGE_SPECIAL_EVENTS,
        perm_models.Permissions.MANAGE_ACCOUNT_UPDATE_REQUEST,
        perm_models.Permissions.MANAGE_INCIDENTS,
        perm_models.Permissions.CREATE_INCIDENTS,
        perm_models.Permissions.CLOSE_OFFERER,
        perm_models.Permissions.READ_NON_PAYMENT_NOTICES,
        perm_models.Permissions.MANAGE_NON_PAYMENT_NOTICES,
        perm_models.Permissions.READ_USER_PROFILE_REFRESH_CAMPAIGN,
        perm_models.Permissions.MANAGE_USER_PROFILE_REFRESH_CAMPAIGN,
    ],
    "dpo": [
        perm_models.Permissions.READ_PUBLIC_ACCOUNT,
        perm_models.Permissions.ANONYMIZE_PUBLIC_ACCOUNT,
        perm_models.Permissions.EXTRACT_PUBLIC_ACCOUNT,
    ],
    "codir_admin": [
        perm_models.Permissions.READ_INCIDENTS,
        perm_models.Permissions.VALIDATE_COMMERCIAL_GESTURE,
    ],
    "gestionnaire_des_droits": [
        perm_models.Permissions.READ_PERMISSIONS,
        perm_models.Permissions.MANAGE_PERMISSIONS,
    ],
    "connect_as_pro": [
        perm_models.Permissions.CONNECT_AS_PRO,
    ],
}


@pytest.fixture(scope="function", name="roles_with_permissions")
def roles_with_permissions_fixture():
    # Roles have already been created from enum in sync_db_roles()
    roles = db.session.query(perm_models.Role).all()
    roles_in_db = {role.name: role for role in roles}
    perms_in_db = {perm.name: perm for perm in db.session.query(perm_models.Permission).all()}

    for role_name, perms in ROLE_PERMISSIONS.items():
        role = roles_in_db[role_name]
        role.permissions = [perms_in_db[perm.name] for perm in perms]
        db.session.add(role)

    db.session.flush()
    return roles


@pytest.fixture(name="user_with_no_permissions")
def user_with_no_permissions_fixture():
    user = users_factories.UserFactory(
        firstName="Hercule",
        lastName="Poirot",
        roles=["ADMIN"],
    )

    perm_api.create_backoffice_profile(user)
    user.backoffice_profile.dsInstructorId = "legit=user=instructor=="
    return user


@pytest.fixture(scope="function", name="legit_user")
def legit_user_fixture(roles_with_permissions: None) -> users_models.User:
    user = users_factories.UserFactory(
        firstName="Hercule",
        lastName="Poirot",
        roles=["ADMIN"],
    )

    perm_api.create_backoffice_profile(user)
    user.backoffice_profile.dsInstructorId = "legit=user=instructor=="
    backoffice_api.upsert_roles(user, list(perm_models.Roles))

    db.session.flush()

    return user


@pytest.fixture(scope="function", name="authenticated_client")
def authenticated_client_fixture(client, legit_user) -> "TestClient":
    return client.with_bo_session_auth(legit_user)


@pytest.fixture(scope="function", name="read_only_bo_user")
def read_only_bo_user_fixture(roles_with_permissions: None) -> users_models.User:
    user = users_factories.AdminFactory()
    backoffice_api.upsert_roles(user, {perm_models.Roles.LECTURE_SEULE})
    db.session.flush()
    return user


@pytest.fixture(scope="function", name="support_pro_n2_admin")
def support_pro_n2_fixture(roles_with_permissions: None) -> users_models.User:
    user = users_factories.AdminFactory()
    backoffice_api.upsert_roles(user, {perm_models.Roles.SUPPORT_PRO, perm_models.Roles.SUPPORT_PRO_N2})
    db.session.flush()
    return user


@pytest.fixture(scope="function", name="pro_fraud_admin")
def pro_fraud_admin_fixture(roles_with_permissions: None) -> users_models.User:
    user = users_factories.AdminFactory()
    backoffice_api.upsert_roles(user, {perm_models.Roles.FRAUDE_CONFORMITE})
    db.session.flush()
    return user


@pytest.fixture(scope="function", name="homologation_admin")
def homologation_admin_fixture(roles_with_permissions: None) -> users_models.User:
    user = users_factories.AdminFactory()
    backoffice_api.upsert_roles(user, {perm_models.Roles.HOMOLOGATION})
    db.session.flush()
    return user


@pytest.fixture
def codir_admin(roles_with_permissions):
    user = users_factories.AdminFactory()
    backoffice_api.upsert_roles(user, {perm_models.Roles.CODIR_ADMIN})
    db.session.flush()
    return user


@pytest.fixture(name="offerer")
def offerer_fixture():
    offerer = offerers_factories.OffererFactory()
    return offerer


@pytest.fixture(name="pro_user")
def pro_user_fixture():
    user = offerers_factories.UserOffererFactory().user
    return user


@pytest.fixture(name="venue_with_accepted_bank_account")
def venue_with_accepted_bank_account_fixture(offerer):
    venue = offerers_factories.VenueFactory(managingOfferer=offerer)
    offerers_factories.VenuePricingPointLinkFactory(venue=venue, pricingPoint=venue)
    offerers_factories.VenueBankAccountLinkFactory(venue=venue, bankAccount=finance_factories.BankAccountFactory())
    return venue


@pytest.fixture(name="venue_with_educational_status")
def venue_with_educational_status_fixture(offerer):
    educational_status = offerers_factories.VenueEducationalStatusFactory()
    venue = offerers_factories.VenueFactory(
        managingOfferer=offerer,
        venueEducationalStatusId=educational_status.id,
    )
    return venue


@pytest.fixture(name="venue_with_nor_contact_or_booking_email")
def venue_with_nor_contact_or_booking_email_fixture():
    venue = offerers_factories.VenueFactory(contact=None, bookingEmail=None)
    return venue


@pytest.fixture(name="venue_provider_with_last_sync")
def venue_provider_with_last_sync_fixture(venue_with_accepted_bank_account):
    venue_provider = providers_factories.VenueProviderFactory(
        venue=venue_with_accepted_bank_account,
        lastSyncDate=date_utils.get_naive_utc_now(),
    )
    return venue_provider


@pytest.fixture(name="offerer_active_individual_offers")
def offerer_active_individual_offers_fixture(offerer, venue_with_accepted_bank_account):
    approved_offers = offers_factories.OfferFactory.create_batch(
        2,
        venue=venue_with_accepted_bank_account,
        validation=offers_models.OfferValidationStatus.APPROVED.value,
    )
    rejected_offer = offers_factories.OfferFactory(
        venue=venue_with_accepted_bank_account,
        validation=offers_models.OfferValidationStatus.REJECTED.value,
    )
    pending_offer = offers_factories.OfferFactory(
        venue=venue_with_accepted_bank_account,
        validation=offers_models.OfferValidationStatus.PENDING.value,
    )
    draft_offer = offers_factories.OfferFactory(
        venue=venue_with_accepted_bank_account,
        validation=offers_models.OfferValidationStatus.DRAFT.value,
    )
    return approved_offers + [rejected_offer, pending_offer, draft_offer]


@pytest.fixture(name="offerer_inactive_individual_offers")
def offerer_inactive_individual_offers_fixture(offerer, venue_with_accepted_bank_account):
    approved_offers = offers_factories.OfferFactory.create_batch(
        3,
        venue=venue_with_accepted_bank_account,
        isActive=False,
        validation=offers_models.OfferValidationStatus.APPROVED.value,
    )
    rejected_offer = offers_factories.OfferFactory(
        venue=venue_with_accepted_bank_account,
        isActive=False,
        validation=offers_models.OfferValidationStatus.REJECTED.value,
    )
    pending_offer = offers_factories.OfferFactory(
        venue=venue_with_accepted_bank_account,
        isActive=False,
        validation=offers_models.OfferValidationStatus.PENDING.value,
    )
    draft_offer = offers_factories.OfferFactory(
        venue=venue_with_accepted_bank_account,
        isActive=False,
        validation=offers_models.OfferValidationStatus.DRAFT.value,
    )
    return approved_offers + [rejected_offer, pending_offer, draft_offer]


@pytest.fixture(name="offerer_active_collective_offers")
def offerer_active_collective_offers_fixture(offerer, venue_with_accepted_bank_account):
    approved_offers = educational_factories.CollectiveOfferFactory.create_batch(
        4,
        venue=venue_with_accepted_bank_account,
        validation=offers_models.OfferValidationStatus.APPROVED.value,
    )
    rejected_offer = educational_factories.CollectiveOfferFactory(
        venue=venue_with_accepted_bank_account,
        validation=offers_models.OfferValidationStatus.REJECTED.value,
    )
    pending_offer = educational_factories.CollectiveOfferFactory(
        venue=venue_with_accepted_bank_account,
        validation=offers_models.OfferValidationStatus.PENDING.value,
    )
    draft_offer = educational_factories.CollectiveOfferFactory(
        venue=venue_with_accepted_bank_account,
        validation=offers_models.OfferValidationStatus.DRAFT.value,
    )
    return approved_offers + [rejected_offer, pending_offer, draft_offer]


@pytest.fixture
def offerer_expired_offers(offerer, venue_with_accepted_bank_account):
    offers = offers_factories.OfferFactory.create_batch(
        size=4,
        venue=venue_with_accepted_bank_account,
        validation=offers_models.OfferValidationStatus.APPROVED.value,
    )
    offers_factories.StockFactory.create_batch(
        size=4,
        offer=factory.Iterator(offers),
        isSoftDeleted=False,
        bookingLimitDatetime=date_utils.get_naive_utc_now() - datetime.timedelta(days=10),
    )
    return offers


@pytest.fixture
def offerer_expired_collective_offers(offerer, venue_with_accepted_bank_account):
    stocks = educational_factories.CollectiveStockFactory.create_batch(
        size=4,
        price=1337,
        startDatetime=date_utils.get_naive_utc_now() - datetime.timedelta(days=10),
    )
    return educational_factories.CollectiveOfferFactory.create_batch(
        size=4,
        venue=venue_with_accepted_bank_account,
        collectiveStock=factory.Iterator(stocks),
    )


@pytest.fixture(name="offerer_inactive_collective_offers")
def offerer_inactive_collective_offers_fixture(offerer, venue_with_accepted_bank_account):
    approved_offers = educational_factories.CollectiveOfferFactory.create_batch(
        5,
        venue=venue_with_accepted_bank_account,
        isActive=False,
        validation=offers_models.OfferValidationStatus.APPROVED.value,
    )
    rejected_offer = educational_factories.CollectiveOfferFactory(
        venue=venue_with_accepted_bank_account,
        isActive=False,
        validation=offers_models.OfferValidationStatus.REJECTED.value,
    )
    pending_offer = educational_factories.CollectiveOfferFactory(
        venue=venue_with_accepted_bank_account,
        isActive=False,
        validation=offers_models.OfferValidationStatus.PENDING.value,
    )
    draft_offer = educational_factories.CollectiveOfferFactory(
        venue=venue_with_accepted_bank_account,
        isActive=False,
        validation=offers_models.OfferValidationStatus.DRAFT.value,
    )
    return approved_offers + [rejected_offer, pending_offer, draft_offer]


@pytest.fixture(name="offerer_active_collective_offer_templates")
def offerer_active_collective_offer_templates_fixture(offerer, venue_with_accepted_bank_account):
    approved_offers = educational_factories.CollectiveOfferTemplateFactory(
        venue=venue_with_accepted_bank_account,
        validation=offers_models.OfferValidationStatus.APPROVED.value,
    )

    rejected_offer = educational_factories.CollectiveOfferTemplateFactory(
        venue=venue_with_accepted_bank_account,
        validation=offers_models.OfferValidationStatus.REJECTED.value,
    )

    pending_offer = educational_factories.CollectiveOfferTemplateFactory(
        venue=venue_with_accepted_bank_account,
        validation=offers_models.OfferValidationStatus.PENDING.value,
    )

    draft_offer = educational_factories.CollectiveOfferTemplateFactory(
        venue=venue_with_accepted_bank_account,
        validation=offers_models.OfferValidationStatus.DRAFT.value,
    )
    return [approved_offers, rejected_offer, pending_offer, draft_offer]


@pytest.fixture(name="offerer_inactive_collective_offer_templates")
def offerer_inactive_collective_offer_templates_fixture(offerer, venue_with_accepted_bank_account):
    approved_offers = educational_factories.CollectiveOfferTemplateFactory.create_batch(
        2,
        venue=venue_with_accepted_bank_account,
        isActive=False,
        validation=offers_models.OfferValidationStatus.APPROVED.value,
    )

    rejected_offer = educational_factories.CollectiveOfferTemplateFactory(
        venue=venue_with_accepted_bank_account,
        isActive=False,
        validation=offers_models.OfferValidationStatus.REJECTED.value,
    )

    pending_offer = educational_factories.CollectiveOfferTemplateFactory(
        venue=venue_with_accepted_bank_account,
        isActive=False,
        validation=offers_models.OfferValidationStatus.PENDING.value,
    )

    draft_offer = educational_factories.CollectiveOfferTemplateFactory(
        venue=venue_with_accepted_bank_account,
        isActive=False,
        validation=offers_models.OfferValidationStatus.DRAFT.value,
    )

    return approved_offers + [rejected_offer, pending_offer, draft_offer]


@pytest.fixture(name="offerer_stocks")
def offerer_stocks_fixture(offerer_active_individual_offers):
    stocks = [offers_factories.StockFactory(offer=offer) for offer in offerer_active_individual_offers]
    return stocks


@pytest.fixture(name="individual_offerer_bookings")
def individual_offerer_bookings_fixture(offerer_stocks, today):
    used_simple = bookings_factories.UsedBookingFactory(
        dateUsed=today,
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
    cancelled = bookings_factories.CancelledBookingFactory(stock=offerer_stocks[2])
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


@pytest.fixture(name="today", scope="module")
def today_fixture():
    # Disable datetime-now custom rule, here we use the timezone aware datetime at UTC
    return datetime.datetime.now(datetime.timezone.utc)


@pytest.fixture(name="collective_venue_booking")
def collective_venue_booking_fixture(venue_with_accepted_bank_account, today):
    educational_status = offerers_factories.VenueEducationalStatusFactory()
    venue_with_accepted_bank_account.venueEducationalStatusId = educational_status.id
    stock = educational_factories.CollectiveStockFactory(price=42)
    used = educational_factories.UsedCollectiveBookingFactory(
        dateUsed=today,
        collectiveStock=stock,
        venue=venue_with_accepted_bank_account,
    )
    cancelled = educational_factories.CancelledCollectiveBookingFactory(
        collectiveStock=stock,
        venue=venue_with_accepted_bank_account,
    )
    return used, cancelled


@pytest.fixture(name="adage_tag")
def adage_tag_fixture():
    category = offerers_factories.OffererTagCategoryFactory(name="homologation", label="Homologation")
    return offerers_factories.OffererTagFactory(name="adage", label="ADAGE", categories=[category])


@pytest.fixture(name="offerer_tags")
def offerer_tags_fixture():
    category = offerers_factories.OffererTagCategoryFactory(name="homologation", label="Homologation")
    other_category = offerers_factories.OffererTagCategoryFactory(name="comptage", label="Comptage partenaires")
    tags = tuple(
        offerers_factories.OffererTagFactory(label=label, categories=[category])
        for label in ("Top acteur", "Collectivité", "Établissement public")
    )
    tags = tags + tuple([offerers_factories.OffererTagFactory(label="Festival", categories=[other_category])])
    return tags


@pytest.fixture(name="offerers_to_be_validated")
def offerers_to_be_validated_fixture(offerer_tags):
    top_tag, collec_tag, public_tag, festival_tag = offerer_tags

    no_tag = offerers_factories.NewOffererFactory(name="A", siren="123001000")
    offerers_factories.VenueFactory(
        managingOfferer=no_tag,
        offererAddress__address__postalCode="35000",
        offererAddress__address__departmentCode="35",
        offererAddress__address__city="Rennes",
    )

    top = offerers_factories.PendingOffererFactory(name="B", siren="123002008")
    offerers_factories.VenueFactory(
        managingOfferer=top,
        offererAddress__address__postalCode="29000",
        offererAddress__address__departmentCode="29",
        offererAddress__address__city="Quimper",
    )

    collec = offerers_factories.NewOffererFactory(name="C", siren="123003006")
    offerers_factories.VenueFactory(
        managingOfferer=collec,
        offererAddress__address__postalCode="50170",
        offererAddress__address__departmentCode="50",
        offererAddress__address__city="Le Mont-Saint-Michel",
    )

    public = offerers_factories.PendingOffererFactory(name="D", siren="123004004")
    offerers_factories.VenueFactory(
        managingOfferer=public,
        offererAddress__address__postalCode="29300",
        offererAddress__address__departmentCode="29",
        offererAddress__address__city="Quimperlé",
    )

    top_collec = offerers_factories.NewOffererFactory(name="E", siren="123005001")
    offerers_factories.VenueFactory(
        managingOfferer=top_collec,
        offererAddress__address__postalCode="35400",
        offererAddress__address__departmentCode="35",
        offererAddress__address__city="Saint-Malo",
    )

    top_public = offerers_factories.PendingOffererFactory(name="F", siren="123006009")
    offerers_factories.VenueFactory(
        managingOfferer=top_public,
        offererAddress__address__postalCode="44000",
        offererAddress__address__departmentCode="44",
        offererAddress__address__city="Nantes",
    )

    for offerer in (top, top_collec, top_public):
        offerers_factories.OffererTagMappingFactory(tagId=top_tag.id, offererId=offerer.id)
    for offerer in (collec, top_collec):
        offerers_factories.OffererTagMappingFactory(tagId=collec_tag.id, offererId=offerer.id)
    for offerer in (public, top_public):
        offerers_factories.OffererTagMappingFactory(tagId=public_tag.id, offererId=offerer.id)
        offerers_factories.OffererTagMappingFactory(tagId=festival_tag.id, offererId=offerer.id)

    offerers_factories.UserOffererFactory(
        offerer=top, user__firstName="Sadi", user__lastName="Carnot", user__email="sadi@example.com"
    )
    offerers_factories.UserOffererFactory(
        offerer=collec, user__firstName="Félix", user__lastName="Faure", user__email="felix@example.com"
    )
    offerers_factories.UserOffererFactory(
        offerer=public, user__firstName="Émile", user__lastName="Loubet", user__email="emile@example.com"
    )

    # Other statuses
    offerers_factories.OffererFactory(name="G")
    offerers_factories.RejectedOffererFactory(name="H")

    # DMS ADAGE statuses
    educational_factories.CollectiveDmsApplicationFactory(venue__managingOfferer=no_tag, state="accepte")
    educational_factories.CollectiveDmsApplicationFactory(venue__managingOfferer=no_tag, state="refuse")
    educational_factories.CollectiveDmsApplicationFactory(venue__managingOfferer=top, state="en_instruction")
    educational_factories.CollectiveDmsApplicationFactory(venue__managingOfferer=collec, state="en_construction")
    educational_factories.CollectiveDmsApplicationFactory(venue__managingOfferer=public, state="sans_suite")
    educational_factories.CollectiveDmsApplicationFactory(venue__managingOfferer=top_collec, state="accepte")

    return (no_tag, top, collec, public, top_collec, top_public)


@pytest.fixture(name="user_offerer_to_be_validated")
def user_offerer_to_be_validated_fixture(offerer_tags):
    top_tag, collec_tag, public_tag, _ = offerer_tags

    no_tag = offerers_factories.NewUserOffererFactory(
        user__email="a@example.com",
        offerer__validationStatus=ValidationStatus.NEW,
    )
    offerers_factories.VenueFactory(
        managingOfferer=no_tag.offerer,
        offererAddress__address__postalCode="97200",
        offererAddress__address__departmentCode="972",
        offererAddress__address__city="Fort-de-France",
    )

    top = offerers_factories.PendingUserOffererFactory(
        user__email="b@example.com",
        offerer__validationStatus=ValidationStatus.NEW,
    )
    offerers_factories.VenueFactory(
        managingOfferer=top.offerer,
        offererAddress__address__postalCode="97100",
        offererAddress__address__departmentCode="971",
        offererAddress__address__city="Basse-Terre",
    )

    collec = offerers_factories.NewUserOffererFactory(
        user__email="c@example.com",
    )
    offerers_factories.VenueFactory(
        managingOfferer=collec.offerer,
        offererAddress__address__postalCode="29200",
        offererAddress__address__departmentCode="29",
        offererAddress__address__city="Brest",
    )

    public = offerers_factories.PendingUserOffererFactory(
        user__email="d@example.com",
        offerer__validationStatus=ValidationStatus.PENDING,
    )
    offerers_factories.VenueFactory(
        managingOfferer=public.offerer,
        offererAddress__address__postalCode="97290",
        offererAddress__address__departmentCode="972",
        offererAddress__address__city="Le Marin",
    )

    top_collec = offerers_factories.NewUserOffererFactory(
        user__email="e@example.com",
        offerer__validationStatus=ValidationStatus.PENDING,
    )
    offerers_factories.VenueFactory(
        managingOfferer=top_collec.offerer,
        offererAddress__address__postalCode="06400",
        offererAddress__address__departmentCode="06",
        offererAddress__address__city="Cannes",
    )

    top_public = offerers_factories.PendingUserOffererFactory(
        user__email="f@example.com",
    )
    offerers_factories.VenueFactory(
        managingOfferer=top_public.offerer,
        offererAddress__address__postalCode="97400",
        offererAddress__address__departmentCode="974",
        offererAddress__address__city="Saint-Denis",
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
