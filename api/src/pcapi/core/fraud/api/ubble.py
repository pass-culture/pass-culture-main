import typing

from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import models as fraud_models
from pcapi.core.users import models as users_models
from pcapi.models import db


def on_ubble_result(fraud_check: fraud_models.BeneficiaryFraudCheck) -> None:
    fraud_api.on_identity_fraud_check_result(fraud_check.user, fraud_check)


def _ubble_result_fraud_item(content: fraud_models.ubble.UbbleContent) -> fraud_models.FraudItem:
    if content.score == fraud_models.ubble.UbbleScore.VALID.value:
        return fraud_models.FraudItem(status=fraud_models.FraudStatus.OK, detail=f"Ubble score {content.score}")

    return fraud_models.FraudItem(
        status=fraud_models.FraudStatus.KO,
        detail=f"Ubble score {content.score}: {content.comment}",
        reason_code=(
            fraud_models.FraudReasonCode.ID_CHECK_INVALID
            if content.score == fraud_models.ubble.UbbleScore.INVALID.value
            else fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE
        ),
    )


def ubble_fraud_checks(
    user: users_models.User, beneficiary_fraud_check: fraud_models.BeneficiaryFraudCheck
) -> list[fraud_models.FraudItem]:
    content = fraud_models.ubble.UbbleContent(**beneficiary_fraud_check.resultContent)

    fraud_items = [
        _ubble_result_fraud_item(content),
        # TODO: factorise in fraud_api.on_identity_fraud_check_result for the 4 *_fraud_checks
        fraud_api._duplicate_user_fraud_item(
            first_name=content.first_name,
            last_name=content.last_name,
            birth_date=content.birth_date,
            excluded_user_id=user.id,
        ),
        fraud_api.validate_id_piece_number_format_fraud_item(content.id_document_number),
        fraud_api._duplicate_id_piece_number_fraud_item(user, content.id_document_number),
    ]

    return fraud_items


def start_ubble_fraud_check(user: users_models.User, ubble_content: fraud_models.ubble.UbbleContent) -> None:
    fraud_check = fraud_models.BeneficiaryFraudCheck(
        user=user,
        type=fraud_models.FraudCheckType.UBBLE,
        thirdPartyId=str(ubble_content.identification_id),
        resultContent=ubble_content,
        status=fraud_models.FraudCheckStatus.PENDING,
    )
    db.session.add(fraud_check)
    db.session.commit()


def get_ubble_fraud_check(identification_id: str) -> typing.Optional[fraud_models.BeneficiaryFraudCheck]:
    fraud_check = (
        fraud_models.BeneficiaryFraudCheck.query.filter(
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.UBBLE
        )
        .filter(fraud_models.BeneficiaryFraudCheck.thirdPartyId == identification_id)
        .one_or_none()
    )
    return fraud_check
