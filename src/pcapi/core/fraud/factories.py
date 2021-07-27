import random

import factory

from pcapi.core import testing
import pcapi.core.users.factories as users_factories

from . import models


JOUVE_CTRL_VALUES = ["OK", "KO"]


class JouveContentFactory(factory.Factory):
    class Meta:
        model = models.JouveContent

    activity = random.choice(["Etudiant"])
    address = "25 rue du moulin vert"
    birthDateTxt = factory.Faker("date", pattern="%d/%m/%Y")
    birthLocationCtrl = random.choice(JOUVE_CTRL_VALUES)
    bodyBirthDateCtrl = random.choice(JOUVE_CTRL_VALUES)
    bodyBirthDateLevel = factory.Faker("pyint", max_value=100)
    bodyFirstnameCtrl = random.choice(JOUVE_CTRL_VALUES)
    bodyFirstnameLevel = factory.Faker("pyint", max_value=100)
    bodyNameLevel = factory.Faker("pyint", max_value=100)
    bodyNameCtrl = random.choice(JOUVE_CTRL_VALUES)
    bodyPieceNumber = factory.Faker("pyint")
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


USERPROFILING_RATING = ["neutral", "low", "good"]
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
    birth_date = factory.Faker("date")
    phone = factory.Faker("phone_number")
    postal_code = "75008"
    activity = "Étudiant"
    address = factory.Faker("address")
    id_piece_number = factory.Sequence("{}".format)


FRAUD_CHECK_TYPE_MODEL_ASSOCIATION = {
    models.FraudCheckType.DMS: DMSContentFactory,
    models.FraudCheckType.JOUVE: JouveContentFactory,
    models.FraudCheckType.USER_PROFILING: UserProfilingFraudDataFactory,
}


class BeneficiaryFraudCheckFactory(testing.BaseFactory):
    class Meta:
        model = models.BeneficiaryFraudCheck

    user = factory.SubFactory(users_factories.UserFactory)
    type = factory.LazyAttribute(lambda o: random.choice(list(models.FraudCheckType)))
    thirdPartyId = factory.Sequence("ThirdPartyIdentifier-{0}".format)
    resultContent = factory.SubFactory(JouveContentFactory)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default ``_create`` with our custom call."""
        factory_class = FRAUD_CHECK_TYPE_MODEL_ASSOCIATION.get(kwargs["type"])
        content = {}
        if factory_class:
            content = factory_class()
        if factory_class and not isinstance(kwargs["resultContent"], factory_class._meta.get_model_class()):
            kwargs["resultContent"] = content

        return super()._create(model_class, *args, **kwargs)


class BeneficiaryFraudResultFactory(testing.BaseFactory):
    class Meta:
        model = models.BeneficiaryFraudResult

    user = factory.SubFactory(users_factories.UserFactory)
    status = factory.LazyAttribute(lambda o: random.choice(list(models.FraudStatus)).value)
    reason = factory.Sequence("Fraud Result excuse #{0}".format)


class BeneficiaryFraudReviewFactory(testing.BaseFactory):
    class Meta:
        model = models.BeneficiaryFraudReview

    user = factory.SubFactory(users_factories.BeneficiaryFactory)
    author = factory.SubFactory(users_factories.AdminFactory)
    reason = factory.Sequence("Fraud validation reason #{0}".format)
