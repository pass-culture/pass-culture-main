import random
import string
import typing
import urllib.parse
import uuid
from datetime import date
from datetime import datetime
from datetime import time

import factory.fuzzy
from dateutil.relativedelta import relativedelta
from factory.declarations import LazyAttribute

import pcapi.core.users.factories as users_factories
from pcapi import settings
from pcapi.core import factories
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import schemas as subscription_schemas
from pcapi.core.subscription.bonus import schemas as bonus_schemas
from pcapi.core.subscription.dms import schemas as dms_schemas
from pcapi.core.subscription.educonnect import schemas as educonnect_schemas
from pcapi.core.subscription.ubble import schemas as ubble_schemas
from pcapi.core.users import constants as users_constants
from pcapi.core.users import models as users_models
from pcapi.models.feature import FeatureToggle
from pcapi.utils import countries as countries_utils
from pcapi.utils import date as date_utils


# This factory is here instead of in the `pcapi.core.users.factories` module because it needs both UserFactory and BeneficiaryFraudCheckFactory.
# Also it should mainly be used in fraud- and subscription- related tests.
class UserEligibleAtIdentityCheckStepFactory(users_factories.UserFactory):
    class Params:
        age = 18

    dateOfBirth = LazyAttribute(
        lambda o: datetime.combine(date.today(), time(0, 0)) - relativedelta(years=o.age, months=5)
    )
    isEmailValidated = True
    phoneValidationStatus = users_models.PhoneValidationStatusType.VALIDATED

    @factory.post_generation
    def profile_completion_fraud_check(
        self,
        create: bool,
        extracted: subscription_models.BeneficiaryFraudCheck | None,
        **kwargs: typing.Any,
    ) -> subscription_models.BeneficiaryFraudCheck | None:
        if not create:
            return None

        return BeneficiaryFraudCheckFactory.create(
            user=self,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
        )

    @factory.post_generation
    def phone_validation_fraud_check(
        self,
        create: bool,
        extracted: subscription_models.BeneficiaryFraudCheck | None,
        **kwargs: typing.Any,
    ) -> subscription_models.BeneficiaryFraudCheck | None:
        if not create:
            return None

        return BeneficiaryFraudCheckFactory.create(
            user=self,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
            status=subscription_models.FraudCheckStatus.OK,
        )


class DMSContentFactory(factory.Factory):
    class Meta:
        model = dms_schemas.DMSContent

    activity = "Étudiant"
    address = factory.Faker("address")
    annotation: dms_schemas.DmsAnnotation | None = None
    application_number = factory.Faker("pyint")
    birth_date = LazyAttribute(lambda _: (datetime.today() - relativedelta(years=18)).date())
    city = "Funky Town"
    civility = users_models.GenderEnum.F
    departement = factory.Sequence("{}".format)
    email = factory.Faker("ascii_safe_email")
    first_name = factory.Faker("first_name")
    id_piece_number = factory.Sequence(lambda _: "".join(random.choices(string.digits, k=12)))
    last_name = factory.Faker("last_name")
    phone = factory.Sequence("+33612{:06}".format)
    postal_code = "75008"
    procedure_number = factory.Faker("pyint")
    registration_datetime = LazyAttribute(lambda _: date_utils.get_naive_utc_now().strftime("%Y-%m-%dT%H:%M:%S"))


class UbbleContentFactory(factory.Factory):
    class Meta:
        model = ubble_schemas.UbbleContent

    status: ubble_schemas.UbbleIdentificationStatus | None = None
    birth_date = (date.today() - relativedelta(years=18, months=4)).isoformat()
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    gender = users_models.GenderEnum.M
    document_type: str | None = None
    id_document_number: str | None = None
    score: float | None = None
    ove_score: float | None = None
    reason_codes: list[subscription_models.FraudReasonCode] | None = None
    comment: str | None = None
    reference_data_check_score: float | None = None
    expiry_date_score: float | None = None
    supported: float | None = None
    identification_id: str | None = None
    identification_url: str | None = None
    registration_datetime = factory.LazyFunction(date_utils.get_naive_utc_now)


class EduconnectContentFactory(factory.Factory):
    class Meta:
        model = educonnect_schemas.EduconnectContent

    class Params:
        age = 15

    birth_date = factory.LazyAttribute(lambda o: date.today() - relativedelta(years=o.age, months=4))
    educonnect_id = factory.Faker("lexify", text="id-?????????????????")
    first_name = factory.Faker("first_name")
    ine_hash = factory.Sequence(lambda _: "".join(random.choices(string.ascii_lowercase + string.digits, k=32)))
    last_name = factory.Faker("last_name")
    registration_datetime = factory.LazyFunction(date_utils.get_naive_utc_now)
    civility = users_models.GenderEnum.F


class ProfileCompletionContentFactory(factory.Factory):
    class Meta:
        model = subscription_schemas.ProfileCompletionContent

    activity = "Lycéen"
    address = factory.Faker("address", locale="fr_FR")
    city = factory.Faker("city")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    origin = "In app"
    postal_code = factory.Faker("postcode", locale="fr_FR")
    school_type: users_models.SchoolTypeEnum | None = None


class QuotientFamilialCustodianFactory(factory.Factory):
    class Meta:
        model = bonus_schemas.QuotientFamilialCustodian

    last_name = factory.Faker("last_name")
    first_names = factory.Faker("random_elements", elements=["Jérôme", "Charles", "Bernard"])
    common_name: str | None = None
    birth_date = factory.Faker("date_of_birth", minimum_age=20)
    gender = users_models.GenderEnum.F
    birth_country_cog_code = countries_utils.FRANCE_INSEE_CODE
    birth_city_cog_code = "08480"


class QuotientFamilialContentFactory(factory.Factory):
    class Meta:
        model = bonus_schemas.QuotientFamilialContent

    provider = "CNAF"
    value = 2550
    year = 2023
    month = 6
    computation_year = 2024
    computation_month = 12


class QuotientFamilialBonusCreditContentFactory(factory.Factory):
    class Meta:
        model = bonus_schemas.QuotientFamilialBonusCreditContent

    custodian = factory.SubFactory(QuotientFamilialCustodianFactory)
    quotient_familial = factory.SubFactory(QuotientFamilialContentFactory)


FRAUD_CHECK_TYPE_MODEL_ASSOCIATION: dict[subscription_models.FraudCheckType, type[factory.Factory] | None] = {
    subscription_models.FraudCheckType.DMS: DMSContentFactory,
    subscription_models.FraudCheckType.UBBLE: UbbleContentFactory,
    subscription_models.FraudCheckType.EDUCONNECT: EduconnectContentFactory,
    subscription_models.FraudCheckType.HONOR_STATEMENT: None,
    subscription_models.FraudCheckType.PROFILE_COMPLETION: ProfileCompletionContentFactory,
    subscription_models.FraudCheckType.QF_BONUS_CREDIT: QuotientFamilialBonusCreditContentFactory,
}


class BeneficiaryFraudCheckFactory(factories.BaseFactory):
    class Meta:
        model = subscription_models.BeneficiaryFraudCheck

    user = factory.SubFactory(users_factories.BeneficiaryGrant18Factory)
    type = subscription_models.FraudCheckType.UBBLE
    thirdPartyId = factory.LazyFunction(lambda: str(uuid.uuid4()))
    status = subscription_models.FraudCheckStatus.PENDING
    dateCreated = factory.LazyFunction(date_utils.get_naive_utc_now)

    @factory.lazy_attribute
    def eligibilityType(
        obj: subscription_models.BeneficiaryFraudCheck,
    ) -> users_models.EligibilityType:
        if obj.dateCreated >= settings.CREDIT_V3_DECREE_DATETIME:
            if FeatureToggle.WIP_FREE_ELIGIBILITY.is_active() and obj.user.age in [15, 16]:
                return users_models.EligibilityType.FREE
            return users_models.EligibilityType.AGE17_18
        if obj.user.age in users_constants.ELIGIBILITY_UNDERAGE_RANGE:
            return users_models.EligibilityType.UNDERAGE
        return users_models.EligibilityType.AGE18

    @classmethod
    def generate_content_from_user(
        cls,
        factory_class: typing.Type[factory.Factory],
        user: users_models.User,
        date_created: datetime | None = None,
    ) -> dict:
        identification_id = str(uuid.uuid4())
        identification_url = urllib.parse.urljoin(settings.UBBLE_API_URL, f"/identifications/{identification_id}")
        kwargs = dict(identification_id=identification_id, identification_url=identification_url)
        if user.firstName:
            kwargs.update(first_name=user.firstName)
        if user.lastName:
            kwargs.update(last_name=user.lastName)
        if user.birth_date:
            kwargs.update(birth_date=user.birth_date.isoformat())
        if date_created:
            kwargs.update(registration_datetime=date_created.isoformat())
        return factory_class.create(**kwargs).dict(by_alias=True)

    @classmethod
    def _create(
        cls,
        model_class: typing.Type[subscription_models.BeneficiaryFraudCheck],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> subscription_models.BeneficiaryFraudCheck:
        """Override the default ``_create`` with our custom call."""
        factory_class = FRAUD_CHECK_TYPE_MODEL_ASSOCIATION.get(kwargs["type"])
        if not factory_class:
            kwargs["resultContent"] = None
            return super()._create(model_class, *args, **kwargs)

        first_registration_datetime = None
        if kwargs.get("dateCreated") and kwargs.get("type") in (
            subscription_models.FraudCheckType.DMS,
            subscription_models.FraudCheckType.UBBLE,
            subscription_models.FraudCheckType.EDUCONNECT,
        ):
            first_registration_datetime = datetime.combine(kwargs["dateCreated"], datetime.min.time())

        content = None
        if "resultContent" not in kwargs:
            content = (
                cls.generate_content_from_user(factory_class, kwargs["user"], first_registration_datetime)
                if "user" in kwargs
                else factory_class.create().dict(by_alias=True)
            )
        elif isinstance(kwargs.get("resultContent"), dict):
            content = factory_class.create(**kwargs["resultContent"]).dict(by_alias=True)
        elif isinstance(kwargs.get("resultContent"), factory_class._meta.get_model_class()):
            content = kwargs["resultContent"].dict(by_alias=True)

        kwargs["resultContent"] = content
        return super()._create(model_class, *args, **kwargs)


class OrphanDmsFraudCheckFactory(factories.BaseFactory):
    class Meta:
        model = subscription_models.OrphanDmsApplication


class BeneficiaryFraudReviewFactory(factories.BaseFactory):
    class Meta:
        model = subscription_models.BeneficiaryFraudReview

    user = factory.SubFactory(users_factories.BeneficiaryGrant18Factory)
    author = factory.SubFactory(users_factories.AdminFactory)
    reason = factory.Sequence("Fraud validation reason #{0}".format)


class OrphanDmsApplicationFactory(factories.BaseFactory):
    class Meta:
        model = subscription_models.OrphanDmsApplication

    email = factory.Sequence("jean.neige{}@example.com".format)
    application_id = factory.Sequence(lambda n: n)
    process_id = factory.Sequence(lambda n: n)


class ProfileCompletionFraudCheckFactory(BeneficiaryFraudCheckFactory):
    type = subscription_models.FraudCheckType.PROFILE_COMPLETION
    resultContent = factory.SubFactory(ProfileCompletionContentFactory)
    status = subscription_models.FraudCheckStatus.OK


class PhoneValidationFraudCheckFactory(BeneficiaryFraudCheckFactory):
    type = subscription_models.FraudCheckType.PHONE_VALIDATION
    status = subscription_models.FraudCheckStatus.OK


class HonorStatementFraudCheckFactory(BeneficiaryFraudCheckFactory):
    type = subscription_models.FraudCheckType.HONOR_STATEMENT
    status = subscription_models.FraudCheckStatus.OK


class UbbleRetryFraudCheckFactory(BeneficiaryFraudCheckFactory):
    type = subscription_models.FraudCheckType.UBBLE
    resultContent = factory.SubFactory(UbbleContentFactory)
    status = subscription_models.FraudCheckStatus.KO
    reasonCodes = [subscription_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE]


class BonusFraudCheckFactory(BeneficiaryFraudCheckFactory):
    type = subscription_models.FraudCheckType.QF_BONUS_CREDIT
    status = subscription_models.FraudCheckStatus.OK
