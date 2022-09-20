from datetime import date
from datetime import datetime
import random
import string
import uuid

from dateutil.relativedelta import relativedelta
from factory.declarations import LazyAttribute
import factory.fuzzy
import pytz

from pcapi.core import testing
import pcapi.core.fraud.ubble.models as ubble_fraud_models
from pcapi.core.users import models as users_models
import pcapi.core.users.factories as users_factories

from . import models


USERPROFILING_RATING = [rating.value for rating in models.UserProfilingRiskRating]
USERPROFILING_RESULTS = ["sucess", "failure"]
USERPROFILING_BOOL = ["yes", "no"]


class UserProfilingFraudDataFactory(factory.Factory):
    class Meta:
        model = models.UserProfilingFraudData

    account_email = factory.Sequence("user.email-{0}@example.com".format)
    account_email_result = "success"
    account_email_score = 0
    account_telephone_result = "success"
    account_telephone_score = factory.Faker("pyint")
    account_telephone_is_valid = "yes"
    bb_bot_rating = "low"
    bb_bot_score = factory.Faker("pyfloat", min_value=-100.0, max_value=100.0)
    bb_fraud_rating = "low"
    bb_fraud_score = factory.Faker("pyfloat", min_value=-100.0, max_value=100.0)
    digital_id = factory.Faker("pystr")
    digital_id_result = "success"
    digital_id_trust_score = factory.Faker("pyfloat", min_value=-100.0, max_value=100.0)
    digital_id_trust_score_rating = "low"
    digital_id_trust_score_reason_code = factory.List(factory.Sequence("Reason code #{0}".format) for x in range(1))
    digital_id_confidence = factory.Faker("pyint")
    digital_id_confidence_rating = "low"
    event_datetime = factory.Faker("date_time")
    policy_score = factory.Faker("pyint")
    reason_code = factory.List((factory.Sequence("Reason code #{0}".format) for x in range(2)))
    request_id = factory.Faker("pystr")
    risk_rating = "low"
    session_id = factory.Faker("pystr")
    tmx_risk_rating = "low"
    tmx_summary_reason_code = factory.List(factory.Sequence("Reason code #{0}".format) for x in range(1))
    summary_risk_score = factory.Faker("pyint")
    unknown_session = "yes"


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
    registration_datetime = LazyAttribute(
        lambda _: datetime.utcnow().replace(tzinfo=pytz.utc).strftime("%Y-%m-%dT%H:%M:%S%z")
    )


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

    activity = "Étudiant"
    city = factory.Faker("city")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    origin = "In app"
    postalCode = factory.Faker("postcode")
    school_type = None


FRAUD_CHECK_TYPE_MODEL_ASSOCIATION = {
    models.FraudCheckType.DMS: DMSContentFactory,
    models.FraudCheckType.USER_PROFILING: UserProfilingFraudDataFactory,
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
    def _create(cls, model_class, *args, **kwargs):  # type: ignore [no-untyped-def]
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
