from datetime import datetime
from decimal import Decimal

from dateutil.relativedelta import relativedelta
import pytest
import time_machine

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.factories import CancelledBookingFactory
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.external.attributes.api import TRACKED_PRODUCT_IDS
from pcapi.core.external.attributes.api import get_bookings_categories_and_subcategories
from pcapi.core.external.attributes.api import get_most_favorite_subcategories
from pcapi.core.external.attributes.api import get_user_attributes
from pcapi.core.external.attributes.api import get_user_bookings
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.external.attributes.models import BookingsAttributes
from pcapi.core.external.attributes.models import UserAttributes
import pcapi.core.finance.conf as finance_conf
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.offers.factories import EventOfferFactory
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.factories import ProductFactory
from pcapi.core.subscription import api as subscription_api
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.users import models as users_models
from pcapi.core.users import testing as sendinblue_testing
from pcapi.core.users.factories import BeneficiaryGrant18Factory
from pcapi.core.users.factories import FavoriteFactory
from pcapi.core.users.factories import ProFactory
from pcapi.core.users.factories import UnderageBeneficiaryFactory
from pcapi.core.users.factories import UserFactory
from pcapi.core.users.models import Credit
from pcapi.core.users.models import DomainsCredit
from pcapi.core.users.models import EligibilityType
from pcapi.core.users.models import PhoneValidationStatusType
from pcapi.core.users.models import User
from pcapi.core.users.models import UserRole
from pcapi.notifications.push import testing as batch_testing


MAX_BATCH_PARAMETER_SIZE = 30

pytestmark = pytest.mark.usefixtures("db_session")


@pytest.mark.parametrize("marketing_subscription", [True, False])
def test_update_external_user(marketing_subscription):
    user = BeneficiaryGrant18Factory(
        email="jeanne@example.com",
        notificationSubscriptions={"marketing_push": marketing_subscription, "marketing_email": marketing_subscription},
    )
    BookingFactory(user=user)

    with assert_no_duplicated_queries():
        update_external_user(user)

    assert len(batch_testing.requests) == 2
    assert batch_testing.requests[0].get("user_id") == user.id
    assert (
        batch_testing.requests[0].get("attribute_values", {}).get("u.marketing_email_subscription")
        is marketing_subscription
    )
    assert (
        batch_testing.requests[0].get("attribute_values", {}).get("u.marketing_push_subscription")
        is marketing_subscription
    )
    assert batch_testing.requests[1].get("user_id") == user.id
    assert (
        batch_testing.requests[1].get("attribute_values", {}).get("u.marketing_email_subscription")
        is marketing_subscription
    )
    assert (
        batch_testing.requests[1].get("attribute_values", {}).get("u.marketing_push_subscription")
        is marketing_subscription
    )
    assert len(sendinblue_testing.sendinblue_requests) == 1
    assert sendinblue_testing.sendinblue_requests[0].get("email") == "jeanne@example.com"
    assert sendinblue_testing.sendinblue_requests[0].get("emailBlacklisted") is not marketing_subscription


def test_email_should_not_be_blacklisted_in_sendinblue_by_default():
    user = BeneficiaryGrant18Factory(
        email="jeanne@example.com",
        notificationSubscriptions={},
    )
    BookingFactory(user=user)

    update_external_user(user)

    assert len(sendinblue_testing.sendinblue_requests) == 1
    assert sendinblue_testing.sendinblue_requests[0].get("email") == "jeanne@example.com"
    assert sendinblue_testing.sendinblue_requests[0].get("emailBlacklisted") is False


def test_update_external_pro_user():
    user = ProFactory()

    with assert_no_duplicated_queries():
        update_external_user(user)

    assert len(batch_testing.requests) == 0
    assert len(sendinblue_testing.sendinblue_requests) == 1


def test_get_user_attributes_beneficiary_with_v1_deposit():
    user = BeneficiaryGrant18Factory(
        deposit__version=1,
        deposit__amount=500,
        departementCode="75",
        phoneNumber="0746050403",
        phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
    )
    offer = OfferFactory(
        product=ProductFactory(id=list(TRACKED_PRODUCT_IDS.keys())[0]),
        subcategoryId=subcategories.SEANCE_CINE.id,
        extraData={"genres": ["THRILLER"]},
    )
    b1 = BookingFactory(user=user, amount=10, dateCreated=datetime(2023, 12, 6, 10), stock__offer=offer)
    b2 = BookingFactory(
        user=user,
        amount=10,
        dateCreated=datetime(2023, 12, 6, 11),
        dateUsed=datetime(2023, 12, 7),
        stock__offer=offer,
    )
    BookingFactory(user=user, amount=5, dateCreated=datetime(2023, 12, 6, 11), stock__offer__venue=offer.venue)
    BookingFactory(
        user=user, amount=100, dateCreated=datetime(2023, 12, 6, 12), status=BookingStatus.CANCELLED
    )  # should be ignored
    FavoriteFactory(
        user=user,
        offer=OfferFactory(subcategoryId=subcategories.VISITE.id),
        dateCreated=datetime.utcnow() - relativedelta(days=3),
    )
    FavoriteFactory(
        user=user,
        offer=OfferFactory(subcategoryId=subcategories.LIVRE_PAPIER.id),
        dateCreated=datetime.utcnow() - relativedelta(days=2),
    )
    last_favorite = FavoriteFactory(
        user=user,
        offer=OfferFactory(subcategoryId=subcategories.LIVRE_PAPIER.id),
        dateCreated=datetime.utcnow() - relativedelta(days=1),
    )

    last_date_created = max(booking.dateCreated for booking in [b1, b2])

    with assert_no_duplicated_queries():
        attributes = get_user_attributes(user)

    assert attributes == UserAttributes(
        domains_credit=DomainsCredit(
            all=Credit(initial=Decimal("500"), remaining=Decimal("475.00")),
            digital=Credit(initial=Decimal("200"), remaining=Decimal("200")),
            physical=Credit(initial=200, remaining=Decimal("195.00")),
        ),
        booking_categories=["CINEMA", "FILM"],
        booking_venues_count=1,  # three bookings on the same venue
        city="Paris",
        date_created=user.dateCreated,
        date_of_birth=user.dateOfBirth,
        departement_code="75",
        deposits_count=1,
        deposit_expiration_date=user.deposit_expiration_date,
        eligibility=EligibilityType.AGE18,
        first_name="Jeanne",
        is_active=True,
        is_beneficiary=True,
        is_current_beneficiary=True,
        is_former_beneficiary=False,
        is_pro=False,
        last_booking_date=last_date_created,
        last_name="Doux",
        marketing_push_subscription=True,
        phone_number="+33746050403",
        postal_code=None,
        products_use_date={"product_brut_x_use": datetime(2023, 12, 7, 0, 0)},
        booking_count=3,
        booking_subcategories=["SEANCE_CINE", "SUPPORT_PHYSIQUE_FILM"],
        deposit_activation_date=user.deposit_activation_date,
        has_completed_id_check=True,
        user_id=user.id,
        is_eligible=True,
        is_email_validated=True,
        is_phone_validated=True,
        last_favorite_creation_date=last_favorite.dateCreated,
        last_visit_date=user.lastConnectionDate,
        marketing_email_subscription=True,
        most_booked_subcategory="SEANCE_CINE",
        most_booked_movie_genre="THRILLER",
        most_booked_music_type=None,
        most_favorite_offer_subcategories=["LIVRE_PAPIER"],
        roles=[UserRole.BENEFICIARY.value],
        subscribed_themes=[],
        suspension_date=None,
        suspension_reason=None,
    )


def test_get_user_attributes_ex_beneficiary_because_of_expiration():
    with time_machine.travel(datetime.utcnow() - relativedelta(years=2, days=2)):
        user = BeneficiaryGrant18Factory(
            departementCode="75",
            phoneNumber="+33605040302",
            phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
        )

    with assert_no_duplicated_queries():
        attributes = get_user_attributes(user)

    assert attributes == UserAttributes(
        domains_credit=DomainsCredit(
            all=Credit(initial=Decimal("300.00"), remaining=Decimal("0")),
            digital=Credit(initial=Decimal("100"), remaining=Decimal("0")),
            physical=None,
        ),
        booking_categories=[],
        booking_venues_count=0,
        city=user.city,
        date_created=user.dateCreated,
        date_of_birth=user.dateOfBirth,
        departement_code="75",
        deposits_count=1,
        deposit_expiration_date=user.deposit_expiration_date,
        eligibility=None,
        first_name=user.firstName,
        is_active=True,
        is_beneficiary=True,
        is_current_beneficiary=False,
        is_former_beneficiary=True,
        is_pro=False,
        last_booking_date=None,
        last_name=user.lastName,
        marketing_push_subscription=True,
        phone_number=user.phoneNumber,
        postal_code=None,
        products_use_date={},
        booking_count=0,
        booking_subcategories=[],
        deposit_activation_date=user.deposit_activation_date,
        has_completed_id_check=True,
        user_id=user.id,
        is_eligible=False,
        is_email_validated=True,
        is_phone_validated=True,
        last_favorite_creation_date=None,
        last_visit_date=user.lastConnectionDate,
        marketing_email_subscription=True,
        most_booked_subcategory=None,
        most_booked_movie_genre=None,
        most_booked_music_type=None,
        most_favorite_offer_subcategories=None,
        roles=[UserRole.BENEFICIARY.value],
        subscribed_themes=[],
        suspension_date=None,
        suspension_reason=None,
    )


def test_get_user_attributes_beneficiary_because_of_credit():
    user = BeneficiaryGrant18Factory(
        departementCode="75",
        phoneNumber="+33607080901",
        phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
    )
    offer1 = OfferFactory(product=ProductFactory(id=list(TRACKED_PRODUCT_IDS.keys())[0]))
    offer2 = EventOfferFactory(venue=offer1.venue, isDuo=True)
    offer3 = OfferFactory()
    BookingFactory(user=user, amount=100, dateCreated=datetime(2022, 12, 6, 11), stock__offer=offer1)
    BookingFactory(user=user, amount=120, dateCreated=datetime(2023, 12, 6, 12), stock__offer=offer2)
    last_booking = BookingFactory(user=user, amount=80, dateCreated=datetime(2023, 12, 6, 13), stock__offer=offer3)
    favorite = FavoriteFactory(user=user, offer=OfferFactory(subcategoryId=subcategories.CONCERT.id))

    with assert_no_duplicated_queries():
        attributes = get_user_attributes(user)

    assert attributes == UserAttributes(
        domains_credit=DomainsCredit(
            all=Credit(initial=Decimal("300"), remaining=Decimal("0.00")),
            digital=Credit(initial=Decimal("100"), remaining=Decimal("0.00")),
            physical=None,
        ),
        booking_categories=["CINEMA", "FILM"],
        booking_venues_count=2,
        city=user.city,
        date_created=user.dateCreated,
        date_of_birth=user.dateOfBirth,
        departement_code="75",
        deposits_count=1,
        deposit_expiration_date=user.deposit_expiration_date,
        eligibility=EligibilityType.AGE18,
        first_name=user.firstName,
        is_active=True,
        is_beneficiary=True,
        is_current_beneficiary=False,
        is_former_beneficiary=True,
        is_pro=False,
        last_booking_date=last_booking.dateCreated,
        last_name=user.lastName,
        marketing_push_subscription=True,
        phone_number=user.phoneNumber,
        postal_code=None,
        products_use_date={},
        booking_count=3,
        booking_subcategories=["SEANCE_CINE", "SUPPORT_PHYSIQUE_FILM"],
        deposit_activation_date=user.deposit_activation_date,
        has_completed_id_check=True,
        user_id=user.id,
        is_eligible=True,
        is_email_validated=True,
        is_phone_validated=True,
        last_favorite_creation_date=favorite.dateCreated,
        last_visit_date=user.lastConnectionDate,
        marketing_email_subscription=True,
        most_booked_subcategory="SUPPORT_PHYSIQUE_FILM",
        most_booked_movie_genre=None,
        most_booked_music_type=None,
        most_favorite_offer_subcategories=["CONCERT"],
        roles=[UserRole.BENEFICIARY.value],
        subscribed_themes=[],
        suspension_date=None,
        suspension_reason=None,
    )


@pytest.mark.parametrize("credit_spent", [False, True])
def test_get_user_attributes_underage_beneficiary_before_18(credit_spent: bool):
    # At 17 years old
    with time_machine.travel(datetime.utcnow() - relativedelta(months=6)):
        user = UnderageBeneficiaryFactory(subscription_age=17)

    if credit_spent:
        offer = OfferFactory(product=ProductFactory(id=list(TRACKED_PRODUCT_IDS.keys())[0]))
        BookingFactory(user=user, amount=finance_conf.GRANTED_DEPOSIT_AMOUNT_17, stock__offer=offer)

    # Before 18 years old
    user = User.query.filter_by(id=user.id).one_or_none()
    attributes = get_user_attributes(user)

    assert attributes.is_beneficiary
    assert attributes.is_current_beneficiary is not credit_spent
    assert not attributes.is_former_beneficiary  # even if underage credit is spent
    assert attributes.roles == [UserRole.UNDERAGE_BENEFICIARY.value]
    assert attributes.deposits_count == 1


def test_get_user_attributes_ex_underage_beneficiary_who_did_not_claim_credit_18_yet():
    # At 17 years old
    with time_machine.travel(datetime.utcnow() - relativedelta(years=1)):
        user = UnderageBeneficiaryFactory(subscription_age=17)

    # At 18 years old
    user = User.query.filter_by(id=user.id).one_or_none()
    attributes = get_user_attributes(user)

    assert attributes.is_beneficiary
    assert not attributes.is_current_beneficiary
    assert not attributes.is_former_beneficiary  # even if underage credit is expired
    assert attributes.roles == [UserRole.UNDERAGE_BENEFICIARY.value]
    assert attributes.deposits_count == 1


def test_get_user_attributes_ex_underage_beneficiary_who_did_not_claim_credit_18_on_time():
    # At 17 years old
    with time_machine.travel(datetime.utcnow() - relativedelta(years=2)):
        user = UnderageBeneficiaryFactory(subscription_age=17)

    # At 19 years old
    user = User.query.filter_by(id=user.id).one_or_none()
    attributes = get_user_attributes(user)

    assert attributes.is_beneficiary
    assert not attributes.is_current_beneficiary
    assert attributes.is_former_beneficiary  # because it's too late to claim any credit
    assert attributes.roles == [UserRole.UNDERAGE_BENEFICIARY.value]
    assert attributes.deposits_count == 1


def test_get_user_attributes_double_beneficiary():
    # At 17 years old
    with time_machine.travel(datetime.utcnow() - relativedelta(years=1)):
        user = UnderageBeneficiaryFactory(subscription_age=17)

    # At 18 years old
    user = User.query.filter_by(id=user.id).one_or_none()
    fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(user=user, status=fraud_models.FraudCheckStatus.OK)
    user = subscription_api.activate_beneficiary_for_eligibility(user, fraud_check, users_models.EligibilityType.AGE18)
    attributes = get_user_attributes(user)

    assert attributes.is_beneficiary
    assert attributes.is_current_beneficiary
    assert not attributes.is_former_beneficiary
    assert attributes.roles == [UserRole.BENEFICIARY.value]
    assert attributes.deposits_count == 2


def test_get_user_attributes_not_beneficiary():
    user = UserFactory(
        dateOfBirth=datetime.utcnow() - relativedelta(years=18, months=3),
        firstName="Cou",
        lastName="Zin",
        city="Nice",
        phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
    )

    fraud_factories.BeneficiaryFraudCheckFactory(
        user=user, type=fraud_models.FraudCheckType.PROFILE_COMPLETION, status=fraud_models.FraudCheckStatus.OK
    )
    fraud_factories.BeneficiaryFraudCheckFactory(
        user=user, type=fraud_models.FraudCheckType.DMS, status=fraud_models.FraudCheckStatus.PENDING
    )

    with assert_no_duplicated_queries():
        attributes = get_user_attributes(user)

    assert attributes == UserAttributes(
        booking_categories=[],
        booking_venues_count=0,
        city="Nice",
        date_created=user.dateCreated,
        date_of_birth=datetime.combine(user.birth_date, datetime.min.time()),
        departement_code=None,
        deposits_count=0,
        deposit_expiration_date=None,
        domains_credit=None,
        eligibility=EligibilityType.AGE18,
        first_name="Cou",
        is_active=True,
        is_beneficiary=False,
        is_current_beneficiary=False,
        is_former_beneficiary=False,
        is_pro=False,
        last_booking_date=None,
        last_name="Zin",
        marketing_push_subscription=True,
        phone_number=None,
        postal_code=user.postalCode,
        products_use_date={},
        booking_count=0,
        booking_subcategories=[],
        deposit_activation_date=None,
        has_completed_id_check=True,
        user_id=user.id,
        is_eligible=True,
        is_email_validated=True,
        is_phone_validated=True,
        last_favorite_creation_date=None,
        last_visit_date=user.lastConnectionDate,
        marketing_email_subscription=True,
        most_booked_subcategory=None,
        most_booked_movie_genre=None,
        most_booked_music_type=None,
        most_favorite_offer_subcategories=None,
        roles=[],
        subscribed_themes=[],
        suspension_date=None,
        suspension_reason=None,
    )


def test_get_bookings_categories_and_subcategories():
    user = BeneficiaryGrant18Factory()
    offer = OfferFactory(product=ProductFactory(id=list(TRACKED_PRODUCT_IDS.keys())[0]))

    assert get_bookings_categories_and_subcategories(get_user_bookings(user)) == BookingsAttributes(
        booking_categories=[],
        booking_subcategories=[],
        most_booked_subcategory=None,
    )

    BookingFactory(user=user, stock__offer=offer)
    BookingFactory(user=user, stock__offer=offer)
    CancelledBookingFactory(user=user)

    assert get_bookings_categories_and_subcategories(get_user_bookings(user)) == BookingsAttributes(
        booking_categories=["FILM"],
        booking_subcategories=["SUPPORT_PHYSIQUE_FILM"],
        most_booked_subcategory="SUPPORT_PHYSIQUE_FILM",
    )


def test_get_bookings_categories_and_subcategories_most_booked():
    user = BeneficiaryGrant18Factory()
    offer1 = OfferFactory(product=ProductFactory(id=list(TRACKED_PRODUCT_IDS.keys())[0]))
    BookingFactory(user=user, stock__offer=offer1)
    BookingFactory(user=user, stock__offer=offer1)
    CancelledBookingFactory(user=user)
    offer2 = OfferFactory(subcategoryId=subcategories.CINE_PLEIN_AIR.id)
    BookingFactory(user=user, stock__offer=offer2)

    booking_attributes = get_bookings_categories_and_subcategories(get_user_bookings(user))

    # 2xFILM, 1xCINE => FILM is the most booked
    assert booking_attributes.booking_categories == ["CINEMA", "FILM"]
    assert booking_attributes.booking_subcategories == ["CINE_PLEIN_AIR", "SUPPORT_PHYSIQUE_FILM"]
    assert booking_attributes.most_booked_subcategory == "SUPPORT_PHYSIQUE_FILM"
    assert booking_attributes.most_booked_movie_genre is None
    assert booking_attributes.most_booked_music_type is None


def test_get_bookings_categories_and_subcategories_most_booked_on_price():
    user = BeneficiaryGrant18Factory()
    offer1 = OfferFactory(product=ProductFactory(id=list(TRACKED_PRODUCT_IDS.keys())[0]))
    BookingFactory(user=user, stock__offer=offer1, stock__price=15.00)
    BookingFactory(user=user, stock__offer=offer1, stock__price=15.00)
    CancelledBookingFactory(user=user)
    offer2 = OfferFactory(subcategoryId=subcategories.CINE_PLEIN_AIR.id)
    BookingFactory(user=user, stock__offer=offer2, stock__price=8.00)
    BookingFactory(user=user, stock__offer=offer2, stock__price=8.00)

    booking_attributes = get_bookings_categories_and_subcategories(get_user_bookings(user))

    # 2xFILM, 2xCINE, but FILM has the highest credit spent => FILM is the most booked
    assert booking_attributes.booking_categories == ["CINEMA", "FILM"]
    assert booking_attributes.booking_subcategories == ["CINE_PLEIN_AIR", "SUPPORT_PHYSIQUE_FILM"]
    assert booking_attributes.most_booked_subcategory == "SUPPORT_PHYSIQUE_FILM"
    assert booking_attributes.most_booked_movie_genre is None
    assert booking_attributes.most_booked_music_type is None


def test_get_bookings_categories_and_subcategories_most_booked_on_count():
    user = BeneficiaryGrant18Factory()
    offer1 = OfferFactory(product=ProductFactory(id=list(TRACKED_PRODUCT_IDS.keys())[0]))
    BookingFactory(user=user, stock__offer=offer1, stock__price=15.00)
    BookingFactory(user=user, stock__offer=offer1, stock__price=15.00)
    CancelledBookingFactory(user=user)
    offer2 = OfferFactory(subcategoryId=subcategories.CINE_PLEIN_AIR.id)
    offer3 = OfferFactory(subcategoryId=subcategories.CINE_PLEIN_AIR.id, extraData={"genres": ["DRAMA", "HISTORICAL"]})
    offer4 = OfferFactory(subcategoryId=subcategories.CINE_PLEIN_AIR.id, extraData={"genres": ["DRAMA", "THRILLER"]})
    BookingFactory(user=user, stock__offer=offer2, stock__price=8.00)
    BookingFactory(user=user, stock__offer=offer3, stock__price=8.00)
    BookingFactory(user=user, stock__offer=offer4, stock__price=8.00)

    booking_attributes = get_bookings_categories_and_subcategories(get_user_bookings(user))

    # 2xFILM, 3xCINE => CINE is the most booked, even if the highest credit spent is still FILM
    assert booking_attributes.booking_categories == ["CINEMA", "FILM"]
    assert booking_attributes.booking_subcategories == ["CINE_PLEIN_AIR", "SUPPORT_PHYSIQUE_FILM"]
    assert booking_attributes.most_booked_subcategory == "CINE_PLEIN_AIR"
    assert booking_attributes.most_booked_movie_genre == "DRAMA"
    assert booking_attributes.most_booked_music_type is None


def test_get_bookings_categories_and_subcategories_music_first():
    user = BeneficiaryGrant18Factory()
    offer1 = OfferFactory(product=ProductFactory(id=list(TRACKED_PRODUCT_IDS.keys())[0]))
    BookingFactory(user=user, stock__offer=offer1, stock__price=15.00)
    BookingFactory(user=user, stock__offer=offer1, stock__price=15.00)
    CancelledBookingFactory(user=user)
    offer2 = OfferFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id, extraData={"musicType": "600"})
    BookingFactory(user=user, stock__offer=offer2, stock__price=10.00)
    offer3 = OfferFactory(subcategoryId=subcategories.TELECHARGEMENT_MUSIQUE.id, extraData={"musicType": "800"})
    BookingFactory(user=user, stock__offer=offer3, stock__price=5.00)
    offer4 = OfferFactory(subcategoryId=subcategories.CAPTATION_MUSIQUE.id, extraData={"musicType": "900"})
    BookingFactory(user=user, stock__offer=offer4, stock__price=12.00)
    offer5 = OfferFactory(subcategoryId=subcategories.CONCERT.id, extraData={"musicType": "800"})
    BookingFactory(user=user, stock__offer=offer5, stock__price=35.00)
    offer6 = OfferFactory(subcategoryId=subcategories.EVENEMENT_MUSIQUE.id, extraData={"musicType": "800"})
    BookingFactory(user=user, stock__offer=offer6, stock__price=25.00)

    booking_attributes = get_bookings_categories_and_subcategories(get_user_bookings(user))

    # most booked subcategory is SUPPORT_PHYSIQUE_FILM, which category is FILM
    # but most booked category is MUSIQUE_ENREGISTREE, so most_booked_music_type is computed among 2 categories
    assert booking_attributes.booking_categories == ["FILM", "MUSIQUE_ENREGISTREE", "MUSIQUE_LIVE"]
    assert booking_attributes.booking_subcategories == [
        "CAPTATION_MUSIQUE",
        "CONCERT",
        "EVENEMENT_MUSIQUE",
        "SUPPORT_PHYSIQUE_FILM",
        "SUPPORT_PHYSIQUE_MUSIQUE_CD",
        "TELECHARGEMENT_MUSIQUE",
    ]
    assert booking_attributes.most_booked_subcategory == "SUPPORT_PHYSIQUE_FILM"
    assert booking_attributes.most_booked_movie_genre is None
    assert booking_attributes.most_booked_music_type == "800"


def test_get_most_favorite_subcategories_none():
    assert get_most_favorite_subcategories([]) is None


def test_get_most_favorite_subcategories_one():
    user = UserFactory()
    favorites = FavoriteFactory.create_batch(3, user=user, offer__subcategoryId=subcategories.SEANCE_CINE.id)

    assert get_most_favorite_subcategories(favorites) == [subcategories.SEANCE_CINE.id]


def test_get_most_favorite_subcategories_two_equal():
    user = UserFactory()
    favorites = [
        FavoriteFactory(user=user, offer__subcategoryId=subcategories.SEANCE_CINE.id),
        FavoriteFactory(user=user, offer__subcategoryId=subcategories.MATERIEL_ART_CREATIF.id),
        FavoriteFactory(user=user, offer__subcategoryId=subcategories.FESTIVAL_MUSIQUE.id),
        FavoriteFactory(user=user, offer__subcategoryId=subcategories.SEANCE_CINE.id),
        FavoriteFactory(user=user, offer__subcategoryId=subcategories.FESTIVAL_MUSIQUE.id),
    ]

    assert set(get_most_favorite_subcategories(favorites)) == {
        subcategories.SEANCE_CINE.id,
        subcategories.FESTIVAL_MUSIQUE.id,
    }
