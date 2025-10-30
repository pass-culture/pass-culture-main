import datetime

from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.bonus import schemas as bonus_schemas
from pcapi.core.users import models as users_models
from pcapi.models import db


def create_bonus_credit_fraud_check(
    user: users_models.User,
    *,
    last_name: str,
    common_name: str | None = None,
    first_names: list[str],
    birth_date: datetime.date,
    gender: users_models.GenderEnum,
    birth_country_cog_code: str,
    birth_city_cog_code: str | None = None,
    origin: str,
) -> None:
    custodian = bonus_schemas.QuotientFamilialCustodian(
        last_name=last_name,
        common_name=common_name,
        first_names=first_names,
        birth_date=birth_date,
        gender=gender,
        birth_country_cog_code=birth_country_cog_code,
        birth_city_cog_code=birth_city_cog_code,
    )
    fraud_check_content = bonus_schemas.BonusCreditContent(custodian=custodian)

    fraud_check = subscription_models.BeneficiaryFraudCheck(
        user=user,
        type=subscription_models.FraudCheckType.BONUS_CREDIT,
        status=subscription_models.FraudCheckStatus.STARTED,
        reason=origin,
        thirdPartyId=f"bonus-credit-{user.id}",
        resultContent=fraud_check_content.dict(),
        eligibilityType=user.eligibility,
    )
    db.session.add(fraud_check)
