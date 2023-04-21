from datetime import date
from datetime import datetime
from datetime import time
import random
import string
import typing
import uuid

from dateutil.relativedelta import relativedelta
from factory.declarations import LazyAttribute
import factory.fuzzy

from pcapi.core import testing
import pcapi.core.fraud.ubble.models as ubble_fraud_models
from pcapi.core.users import models as users_models
import pcapi.core.users.factories as users_factories

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

        if extracted:
            return extracted

        return BeneficiaryFraudCheckFactory(
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

        if extracted:
            return extracted

        return BeneficiaryFraudCheckFactory(
            user=self, type=models.FraudCheckType.PHONE_VALIDATION, status=models.FraudCheckStatus.OK
        )


class DMSContentFactory(factory.Factory):
    class Meta:
        model = models.DMSContent

    activity = "Étudiant"
    address = factory.Faker("address")
    annotation = None
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
    registration_datetime = LazyAttribute(lambda _: datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S%z"))


class UbbleContentFactory(factory.Factory):
    class Meta:
        model = ubble_fraud_models.UbbleContent

    status = None
    birth_date = (date.today() - relativedelta(years=18, months=4)).isoformat()
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    document_type = None
    id_document_number = None
    score = None
    ove_score = None
    comment = None
    reference_data_check_score = None
    expiry_date_score = None
    supported = None
    identification_id = None
    identification_url = None
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
    address = factory.Faker("address")
    city = factory.Faker("city")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    origin = "In app"
    postal_code = factory.Faker("postcode")
    school_type = None


FRAUD_CHECK_TYPE_MODEL_ASSOCIATION: dict[models.FraudCheckType, factory.Factory | None] = {
    models.FraudCheckType.DMS: DMSContentFactory,
    models.FraudCheckType.UBBLE: UbbleContentFactory,
    models.FraudCheckType.EDUCONNECT: EduconnectContentFactory,
    models.FraudCheckType.HONOR_STATEMENT: None,
    models.FraudCheckType.PROFILE_COMPLETION: ProfileCompletionContentFactory,
}


class BeneficiaryFraudCheckFactory(testing.BaseFactory):
    class Meta:
        model = models.BeneficiaryFraudCheck

    user = factory.SubFactory(users_factories.BeneficiaryGrant18Factory)
    type = models.FraudCheckType.UBBLE
    thirdPartyId = factory.LazyFunction(lambda: str(uuid.uuid4()))
    status = models.FraudCheckStatus.PENDING
    eligibilityType = users_models.EligibilityType.AGE18

    @classmethod
    def _create(
        cls,
        model_class: typing.Type[models.BeneficiaryFraudCheck],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.BeneficiaryFraudCheck:
        """Override the default ``_create`` with our custom call."""
        factory_class = FRAUD_CHECK_TYPE_MODEL_ASSOCIATION.get(kwargs["type"])
        content = {}
        if factory_class and "resultContent" not in kwargs:
            content = factory_class().dict(by_alias=True)
        if factory_class and isinstance(kwargs.get("resultContent"), factory_class._meta.get_model_class()):
            content = kwargs["resultContent"].dict(by_alias=True)

        kwargs["resultContent"] = content or None
        return super()._create(model_class, *args, **kwargs)


class OrphanDmsFraudCheckFactory(testing.BaseFactory):
    class Meta:
        model = models.OrphanDmsApplication


class BeneficiaryFraudReviewFactory(testing.BaseFactory):
    class Meta:
        model = models.BeneficiaryFraudReview

    user = factory.SubFactory(users_factories.BeneficiaryGrant18Factory)
    author = factory.SubFactory(users_factories.AdminFactory)
    reason = factory.Sequence("Fraud validation reason #{0}".format)


class OrphanDmsApplicationFactory(testing.BaseFactory):
    class Meta:
        model = models.OrphanDmsApplication

    email = factory.Sequence("jean.neige{}@example.com".format)
    application_id = factory.Sequence(lambda n: n)
    process_id = factory.Sequence(lambda n: n)


class ProfileCompletionFraudCheckFactory(BeneficiaryFraudCheckFactory):
    type = models.FraudCheckType.PROFILE_COMPLETION
    resultContent = factory.SubFactory(ProfileCompletionContentFactory)
    status = models.FraudCheckStatus.OK


class UbbleRetryFraudCheckFactory(BeneficiaryFraudCheckFactory):
    type = models.FraudCheckType.UBBLE
    resultContent = factory.SubFactory(UbbleContentFactory)
    status = models.FraudCheckStatus.KO
    reasonCodes = [models.FraudReasonCode.ID_CHECK_UNPROCESSABLE]
