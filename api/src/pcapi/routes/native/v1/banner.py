from flask_login import current_user
from sqlalchemy.orm import selectinload

import pcapi.core.banner.api as banner_api
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.routes.native import blueprint
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.routes.native.v1.serialization import banner as serializers
from pcapi.serialization.decorator import spectree_serialize


@blueprint.native_route("/banner", methods=["GET"])
@spectree_serialize(on_success_status=200, api=blueprint.api, response_model=serializers.BannerResponse)
@authenticated_and_active_user_required
def get_banner(query: serializers.BannerQueryParams) -> serializers.BannerResponse | None:
    joined_user = (
        db.session.query(users_models.User)
        .filter_by(id=current_user.id)
        .options(
            selectinload(users_models.User.beneficiaryFraudChecks).load_only(
                subscription_models.BeneficiaryFraudCheck.dateCreated,
                subscription_models.BeneficiaryFraudCheck.eligibilityType,
                subscription_models.BeneficiaryFraudCheck.type,
                subscription_models.BeneficiaryFraudCheck.status,
                subscription_models.BeneficiaryFraudCheck.userId,
                subscription_models.BeneficiaryFraudCheck.reasonCodes,
                subscription_models.BeneficiaryFraudCheck.updatedAt,
            ),
            selectinload(users_models.User.beneficiaryFraudReviews).load_only(
                subscription_models.BeneficiaryFraudReview.dateReviewed,
                subscription_models.BeneficiaryFraudReview.review,
            ),
            selectinload(users_models.User.deposits),
        )
        .one()
    )

    subscription_state = subscription_api.get_user_subscription_state(joined_user)

    banner = banner_api.get_banner(subscription_state, joined_user, query.is_geolocated)
    return serializers.BannerResponse(banner=banner)
