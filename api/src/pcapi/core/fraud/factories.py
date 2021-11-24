from datetime import date
from datetime import datetime
import random
import string

from dateutil.relativedelta import relativedelta
import factory
from factory.declarations import LazyAttribute
import factory.fuzzy

from pcapi.core import testing
import pcapi.core.users.factories as users_factories

from . import models


JOUVE_CTRL_VALUES = ["OK", "KO"]


class JouveContentFactory(factory.Factory):
    class Meta:
        model = models.JouveContent

    activity = random.choice(["Etudiant"])
    address = "25 rue du moulin vert"
    birthDateTxt = LazyAttribute(lambda _: (datetime.utcnow() - relativedelta(years=18)).strftime("%d/%m/%Y"))
    birthLocationCtrl = random.choice(JOUVE_CTRL_VALUES)
    bodyBirthDateCtrl = random.choice(JOUVE_CTRL_VALUES)
    bodyBirthDateLevel = factory.Faker("pyint", max_value=100)
    bodyFirstnameCtrl = random.choice(JOUVE_CTRL_VALUES)
    bodyFirstnameLevel = factory.Faker("pyint", max_value=100)
    bodyNameLevel = factory.Faker("pyint", max_value=100)
    bodyNameCtrl = random.choice(JOUVE_CTRL_VALUES)
    bodyPieceNumber = factory.fuzzy.FuzzyText(length=12, chars=string.digits)
    bodyPieceNumberCtrl = random.choice(JOUVE_CTRL_VALUES)
    bodyPieceNumberLevel = factory.Faker("pyint", max_value=100)
    city = "Paris"
    creatorCtrl = random.choice(JOUVE_CTRL_VALUES)
    id = factory.Faker("pyint")
    email = factory.Sequence("jeanne.doux{}@example.com".format)
    firstName = factory.Sequence("Jeanne{}".format)
    gender = random.choice(["Male", "Female"])
    initialNumberCtrl = factory.Faker("pyint")
    initialSizeCtrl = random.choice(JOUVE_CTRL_VALUES)
    lastName = factory.Sequence("doux{}".format)
    phoneNumber = factory.Sequence("+3361212121{}".format)
    postalCode = "75008"
    posteCodeCtrl = "75"
    serviceCodeCtrl = factory.Faker("pystr")
    registrationDate = datetime.utcnow()


USERPROFILING_RATING = [rating.value for rating in models.UserProfilingRiskRating]
USERPROFILING_RESULTS = ["sucess", "failure"]
USERPROFILING_BOOL = ["yes", "no"]


class UserProfilingFraudDataFactory(factory.Factory):
    class Meta:
        model = models.UserProfilingFraudData

    account_email = factory.Sequence("user.email-{0}@example.com".format)
    account_email_result = random.choice(USERPROFILING_RESULTS)
    account_email_score = factory.Faker("pyint")
    account_telephone_result = random.choice(USERPROFILING_RESULTS)
    account_telephone_score = factory.Faker("pyint")
    account_telephone_is_valid = random.choice(USERPROFILING_BOOL)
    bb_bot_rating = random.choice(USERPROFILING_RATING)
    bb_bot_score = factory.Faker("pyfloat", min_value=-100.0, max_value=100.0)
    bb_fraud_rating = random.choice(USERPROFILING_RATING)
    bb_fraud_score = factory.Faker("pyfloat", min_value=-100.0, max_value=100.0)
    digital_id = factory.Faker("pystr")
    digital_id_result = random.choice(USERPROFILING_RESULTS)
    digital_id_trust_score = factory.Faker("pyfloat", min_value=-100.0, max_value=100.0)
    digital_id_trust_score_rating = random.choice(USERPROFILING_RATING)
    digital_id_trust_score_reason_code = factory.List(factory.Sequence("Reason code #{0}".format) for x in range(1))
    digital_id_confidence = factory.Faker("pyint")
    digital_id_confidence_rating = random.choice(USERPROFILING_RATING)
    event_datetime = factory.Faker("date_time")
    policy_score = factory.Faker("pyint")
    reason_code = factory.List((factory.Sequence("Reason code #{0}".format) for x in range(2)))
    request_id = factory.Faker("pystr")
    risk_rating = random.choice(USERPROFILING_RATING)
    session_id = factory.Faker("pystr")
    tmx_risk_rating = random.choice(USERPROFILING_RATING)
    tmx_summary_reason_code = factory.List(factory.Sequence("Reason code #{0}".format) for x in range(1))
    summary_risk_score = factory.Faker("pyint")
    unknown_session = random.choice(USERPROFILING_BOOL)


class DMSContentFactory(factory.Factory):
    class Meta:
        model = models.DMSContent

    last_name = factory.Faker("last_name")
    first_name = factory.Faker("first_name")
    civility = random.choice(["M.", "Mme"])
    email = factory.Faker("ascii_safe_email")
    application_id = factory.Faker("pyint")
    procedure_id = factory.Faker("pyint")
    departement = factory.Sequence("{}".format)
    birth_date = LazyAttribute(lambda _: (datetime.today() - relativedelta(years=18)).date())
    phone = factory.Sequence("+3361212121{}".format)
    postal_code = "75008"
    activity = "Étudiant"
    address = factory.Faker("address")
    id_piece_number = factory.Sequence(lambda _: "".join(random.choices(string.digits, k=12)))
    registration_datetime = datetime.utcnow()


class UbbleIdentificationResponseFactory(factory.Factory):
    class Meta:
        model = models.UbbleIdentificationResponse
        rename = {
            "created_at": "created-at",
            "ended_at": "ended-at",
            "identification_id": "identification-id",
            "identification_url": "identification-url",
            "number_of_attempts": "number-of-attempts",
            "redirect_url": "redirect-url",
            "started_at": "started-at",
            "updated_at": "updated-at",
            "status_updated_at": "status-updated-at",
            "user_agent": "user-agent",
            "user_ip_address": "user-ip-address",
        }

    comment = factory.Faker("sentence", nb_words=3)
    created_at = factory.Faker("date_time")
    ended_at = factory.Faker("date_time")
    identification_id = factory.Faker("pystr")
    identification_url = factory.Faker("url")
    number_of_attempts = factory.Faker("pyint")
    redirect_url = factory.Faker("url")
    score = factory.Faker("pyfloat")
    started_at = factory.Faker("date_time")
    status = factory.Faker("pystr")  # swith to enum
    updated_at = factory.Faker("date_time")
    status_updated_at = factory.Faker("date_time")
    user_agent = factory.Faker("user_agent")
    user_ip_address = factory.Faker("ipv4")
    webhook = factory.Faker("url")


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
    registration_datetime = datetime.now()


FRAUD_CHECK_TYPE_MODEL_ASSOCIATION = {
    models.FraudCheckType.DMS: DMSContentFactory,
    models.FraudCheckType.JOUVE: JouveContentFactory,
    models.FraudCheckType.USER_PROFILING: UserProfilingFraudDataFactory,
    models.FraudCheckType.UBBLE: UbbleIdentificationResponseFactory,
    models.FraudCheckType.EDUCONNECT: EduconnectContentFactory,
}


class BeneficiaryFraudCheckFactory(testing.BaseFactory):
    class Meta:
        model = models.BeneficiaryFraudCheck

    user = factory.SubFactory(users_factories.BeneficiaryGrant18Factory)
    type = models.FraudCheckType.JOUVE
    thirdPartyId = factory.Sequence("ThirdPartyIdentifier-{0}".format)
    status = models.FraudCheckStatus.PENDING

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default ``_create`` with our custom call."""
        factory_class = FRAUD_CHECK_TYPE_MODEL_ASSOCIATION.get(kwargs["type"])
        content = {}
        if "resultContent" not in kwargs:
            content = factory_class().dict(by_alias=True)
        if isinstance(kwargs.get("resultContent"), factory_class._meta.get_model_class()):
            content = kwargs["resultContent"].dict(by_alias=True)

        kwargs["resultContent"] = content
        return super()._create(model_class, *args, **kwargs)


class BeneficiaryFraudResultFactory(testing.BaseFactory):
    class Meta:
        model = models.BeneficiaryFraudResult

    user = factory.SubFactory(users_factories.BeneficiaryGrant18Factory)
    status = models.FraudStatus.OK
    reason = factory.Sequence("Fraud Result excuse #{0}".format)


class BeneficiaryFraudReviewFactory(testing.BaseFactory):
    class Meta:
        model = models.BeneficiaryFraudReview

    user = factory.SubFactory(users_factories.BeneficiaryGrant18Factory)
    author = factory.SubFactory(users_factories.AdminFactory)
    reason = factory.Sequence("Fraud validation reason #{0}".format)


### TODO: remove after 15-17 test phase ###
class IneHashWhitelistFactory(testing.BaseFactory):
    class Meta:
        model = models.IneHashWhitelist


### END ###
