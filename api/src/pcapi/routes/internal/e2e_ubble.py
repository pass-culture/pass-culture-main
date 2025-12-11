import enum
import urllib.parse
import uuid

from flask_login import current_user

from pcapi import settings
from pcapi.connectors.serialization import ubble_serializers
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import factories as subscription_factories
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.ubble import fraud_check_api as ubble_fraud_api
from pcapi.core.subscription.ubble import schemas as ubble_schemas
from pcapi.core.users import models as users_models
from pcapi.routes.native import blueprint
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic


class UbbleError(enum.Enum):
    NETWORK_CONNECTION_ISSUE = 1201
    BLURRY_DOCUMENT_VIDEO = 1301
    LACK_OF_LUMINOSITY = 1320
    ID_CHECK_EXPIRED = 2101
    ID_CHECK_NOT_SUPPORTED = 2102
    DOCUMENT_DAMAGED = 2103
    ID_CHECK_NOT_AUTHENTIC = 2201


class E2EUbbleIdCheck(BaseModel):
    errors: list[UbbleError] | None = None


@blueprint.native_route("/ubble_identification/e2e", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@authenticated_and_active_user_required
@atomic()
def ubble_identification(body: E2EUbbleIdCheck) -> None:
    content = make_identification_response(current_user, body.errors)
    fraud_check = subscription_api.initialize_identity_fraud_check(
        eligibility_type=current_user.eligibility,
        fraud_check_type=subscription_models.FraudCheckType.UBBLE,
        identity_content=content,
        third_party_id=str(content.identification_id),
        user=current_user,
    )
    ubble_fraud_api.on_ubble_result(fraud_check)
    subscription_api.activate_beneficiary_if_no_missing_step(user=current_user)


def make_identification_response(
    user: users_models.User, errors: list[UbbleError] | None
) -> ubble_schemas.UbbleContent:
    identification_id = str(uuid.uuid4())
    identification_url = urllib.parse.urljoin(settings.UBBLE_API_URL, f"/identifications/{identification_id}")
    assert user.birth_date is not None  # always the case here

    return subscription_factories.UbbleContentFactory.create(
        first_name=user.firstName,
        last_name=user.lastName,
        birth_date=user.birth_date.isoformat(),
        identification_id=identification_id,
        identification_url=identification_url,
        id_document_number="123456789012",
        reason_codes=[ubble_schemas.UBBLE_REASON_CODE_MAPPING[error.value] for error in errors] if errors else None,
        status=ubble_schemas.UbbleIdentificationStatus.PROCESSED,
        score=ubble_serializers.UbbleScore.INVALID.value if errors else ubble_serializers.UbbleScore.VALID.value,
    )
