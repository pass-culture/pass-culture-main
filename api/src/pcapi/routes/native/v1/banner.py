from sqlalchemy.orm import selectinload

import pcapi.core.banner.api as banner_api
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import api as subscription_api
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.routes.native import blueprint
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.routes.native.v1.serialization import banner as serializers
from pcapi.serialization.decorator import spectree_serialize


@blueprint.native_route("/banner", methods=["GET"])
@spectree_serialize(on_success_status=200, api=blueprint.api, response_model=serializers.BannerResponse)
@authenticated_and_active_user_required
def get_banner(user: users_models.User, query: serializers.BannerQueryParams) -> serializers.BannerResponse | None:
    joined_user = (
        db.session.query(users_models.User)
        .filter_by(id=user.id)
        .options(
            selectinload(users_models.User.beneficiaryFraudChecks).load_only(
                fraud_models.BeneficiaryFraudCheck.dateCreated,
                fraud_models.BeneficiaryFraudCheck.eligibilityType,
                fraud_models.BeneficiaryFraudCheck.type,
                fraud_models.BeneficiaryFraudCheck.status,
                fraud_models.BeneficiaryFraudCheck.userId,
                fraud_models.BeneficiaryFraudCheck.reasonCodes,
                fraud_models.BeneficiaryFraudCheck.updatedAt,
            ),
            selectinload(users_models.User.beneficiaryFraudReviews).load_only(
                fraud_models.BeneficiaryFraudReview.dateReviewed,
                fraud_models.BeneficiaryFraudReview.review,
            ),
            selectinload(users_models.User.deposits),
        )
        .one()
    )

    subscription_state = subscription_api.get_user_subscription_state(joined_user)

    banner = banner_api.get_banner(subscription_state, joined_user, query.is_geolocated)
    return serializers.BannerResponse(banner=banner)
