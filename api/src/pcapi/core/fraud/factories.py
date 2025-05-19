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
from pcapi.connectors.serialization import ubble_serializers
from pcapi.core import factories
from pcapi.core.users import constants as users_constants
from pcapi.core.users import models as users_models
from pcapi.models.feature import FeatureToggle

from . import models


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
        extracted: models.BeneficiaryFraudCheck | None,
        **kwargs: typing.Any,
    ) -> models.BeneficiaryFraudCheck | None:
        if not create:
            return None

        return BeneficiaryFraudCheckFactory.create(
            user=self, type=models.FraudCheckType.PROFILE_COMPLETION, status=models.FraudCheckStatus.OK
        )

    @factory.post_generation
    def phone_validation_fraud_check(
        self,
        create: bool,
        extracted: models.BeneficiaryFraudCheck | None,
        **kwargs: typing.Any,
    ) -> models.BeneficiaryFraudCheck | None:
        if not create:
            return None

        return BeneficiaryFraudCheckFactory.create(
            user=self, type=models.FraudCheckType.PHONE_VALIDATION, status=models.FraudCheckStatus.OK
        )


class DMSContentFactory(factory.Factory):
    class Meta:
        model = models.DMSContent

    activity = "Étudiant"
    address = factory.Faker("address")
    annotation: models.DmsAnnotation | None = None
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
    registration_datetime = LazyAttribute(lambda _: datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"))


class UbbleContentFactory(factory.Factory):
    class Meta:
        model = models.UbbleContent

    status: ubble_serializers.UbbleIdentificationStatus | None = None
    birth_date = (date.today() - relativedelta(years=18, months=4)).isoformat()
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    document_type: str | None = None
    id_document_number: str | None = None
    score: float | None = None
    ove_score: float | None = None
    reason_codes: list[models.FraudReasonCode] | None = None
    comment: str | None = None
    reference_data_check_score: float | None = None
    expiry_date_score: float | None = None
    supported: float | None = None
    identification_id: str | None = None
    identification_url: str | None = None
    registration_datetime = factory.LazyFunction(datetime.utcnow)


class EduconnectContentFactory(factory.Factory):
    class Meta:
        model = models.EduconnectContent

    class Params:
        age = 15

    birth_date = factory.LazyAttribute(lambda o: date.today() - relativedelta(years=o.age, months=4))
    educonnect_id = factory.Faker("lexify", text="id-?????????????????")
    first_name = factory.Faker("first_name")
    ine_hash = factory.Sequence(lambda _: "".join(random.choices(string.ascii_lowercase + string.digits, k=32)))
    last_name = factory.Faker("last_name")
    registration_datetime = factory.LazyFunction(datetime.utcnow)
    civility = users_models.GenderEnum.F


class ProfileCompletionContentFactory(factory.Factory):
    class Meta:
        model = models.ProfileCompletionContent

    activity = "Lycéen"
    address = factory.Faker("address", locale="fr_FR")
    city = factory.Faker("city")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    origin = "In app"
    postal_code = factory.Faker("postcode", locale="fr_FR")
    school_type: users_models.SchoolTypeEnum | None = None


FRAUD_CHECK_TYPE_MODEL_ASSOCIATION: dict[models.FraudCheckType, type[factory.Factory] | None] = {
    models.FraudCheckType.DMS: DMSContentFactory,
    models.FraudCheckType.UBBLE: UbbleContentFactory,
    models.FraudCheckType.EDUCONNECT: EduconnectContentFactory,
    models.FraudCheckType.HONOR_STATEMENT: None,
    models.FraudCheckType.PROFILE_COMPLETION: ProfileCompletionContentFactory,
}


class BeneficiaryFraudCheckFactory(factories.BaseFactory):
    class Meta:
        model = models.BeneficiaryFraudCheck

    user = factory.SubFactory(users_factories.BeneficiaryGrant18Factory)
    type = models.FraudCheckType.UBBLE
    thirdPartyId = factory.LazyFunction(lambda: str(uuid.uuid4()))
    status = models.FraudCheckStatus.PENDING
    dateCreated = factory.LazyFunction(datetime.utcnow)

    @factory.lazy_attribute
    def eligibilityType(  # type: ignore[misc]
        obj: models.BeneficiaryFraudCheck,
    ) -> users_models.EligibilityType:
        if FeatureToggle.WIP_ENABLE_CREDIT_V3.is_active() and obj.dateCreated >= settings.CREDIT_V3_DECREE_DATETIME:
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
        model_class: typing.Type[models.BeneficiaryFraudCheck],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.BeneficiaryFraudCheck:
        """Override the default ``_create`` with our custom call."""
        factory_class = FRAUD_CHECK_TYPE_MODEL_ASSOCIATION.get(kwargs["type"])
        if not factory_class:
            kwargs["resultContent"] = None
            return super()._create(model_class, *args, **kwargs)

        first_registration_datetime = None
        if kwargs.get("dateCreated") and kwargs.get("type") in (
            models.FraudCheckType.DMS,
            models.FraudCheckType.UBBLE,
            models.FraudCheckType.EDUCONNECT,
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
        model = models.OrphanDmsApplication


class BeneficiaryFraudReviewFactory(factories.BaseFactory):
    class Meta:
        model = models.BeneficiaryFraudReview

    user = factory.SubFactory(users_factories.BeneficiaryGrant18Factory)
    author = factory.SubFactory(users_factories.AdminFactory)
    reason = factory.Sequence("Fraud validation reason #{0}".format)


class OrphanDmsApplicationFactory(factories.BaseFactory):
    class Meta:
        model = models.OrphanDmsApplication

    email = factory.Sequence("jean.neige{}@example.com".format)
    application_id = factory.Sequence(lambda n: n)
    process_id = factory.Sequence(lambda n: n)


class ProfileCompletionFraudCheckFactory(BeneficiaryFraudCheckFactory):
    type = models.FraudCheckType.PROFILE_COMPLETION
    resultContent = factory.SubFactory(ProfileCompletionContentFactory)
    status = models.FraudCheckStatus.OK


class PhoneValidationFraudCheckFactory(BeneficiaryFraudCheckFactory):
    type = models.FraudCheckType.PHONE_VALIDATION
    status = models.FraudCheckStatus.OK


class HonorStatementFraudCheckFactory(BeneficiaryFraudCheckFactory):
    type = models.FraudCheckType.HONOR_STATEMENT
    status = models.FraudCheckStatus.OK


class UbbleRetryFraudCheckFactory(BeneficiaryFraudCheckFactory):
    type = models.FraudCheckType.UBBLE
    resultContent = factory.SubFactory(UbbleContentFactory)
    status = models.FraudCheckStatus.KO
    reasonCodes = [models.FraudReasonCode.ID_CHECK_UNPROCESSABLE]


class BlacklistedDomainNameFactory(factories.BaseFactory):
    class Meta:
        model = models.BlacklistedDomainName

    domain = factory.Sequence("my-domain-{}.com".format)


class ProductWhitelistFactory(factories.BaseFactory):
    class Meta:
        model = models.ProductWhitelist

    comment = factory.Sequence("OK {} !".format)
    title = factory.Sequence("Ducobu #{} !".format)
    ean = factory.fuzzy.FuzzyText(length=13)
    dateCreated = factory.LazyFunction(datetime.utcnow)
    author = factory.SubFactory(users_factories.AdminFactory)
