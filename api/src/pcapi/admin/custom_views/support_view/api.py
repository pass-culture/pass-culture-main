import enum
import logging
from typing import Optional

import flask

from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.common import models as common_fraud_models
from pcapi.core.mails.transactional.users.subscription_document_error import send_subscription_document_error_email
from pcapi.core.payments import exceptions as payment_exceptions
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import exceptions as subscription_exceptions
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.models import SubscriptionItemStatus
from pcapi.core.users import api as users_api
from pcapi.core.users import models as users_models
from pcapi.models import db

from . import exceptions


logger = logging.getLogger(__name__)


class BeneficiaryActivationStatus(enum.Enum):
    INCOMPLETE = "incomplete"
    KO = "ko"
    NOT_APPLICABLE = "n/a"
    OK = "ok"
    SUSPICIOUS = "suspicious"


SUBSCRIPTION_ITEM_METHODS = [
    subscription_api.get_email_validation_subscription_item,
    subscription_api.get_phone_validation_subscription_item,
    subscription_api.get_user_profiling_subscription_item,
    subscription_api.get_profile_completion_subscription_item,
    subscription_api.get_identity_check_subscription_item,
    subscription_api.get_honor_statement_subscription_item,
]


def get_subscription_items_by_eligibility(
    user: users_models.User,
) -> list[dict[str, subscription_models.SubscriptionItem]]:
    subscription_items = []
    for method in SUBSCRIPTION_ITEM_METHODS:
        subscription_items.append(
            {
                users_models.EligibilityType.UNDERAGE.name: method(user, users_models.EligibilityType.UNDERAGE),
                users_models.EligibilityType.AGE18.name: method(user, users_models.EligibilityType.AGE18),
            },
        )

    return subscription_items


def get_beneficiary_activation_status(user: users_models.User) -> BeneficiaryActivationStatus:
    if user.is_beneficiary and not users_api.is_eligible_for_beneficiary_upgrade(user, user.eligibility):
        return BeneficiaryActivationStatus.OK

    # even if the user is above 18, we want to know the status in case subscription steps were performed
    eligibility = user.eligibility or users_models.EligibilityType.AGE18

    subscription_items = [method(user, eligibility) for method in SUBSCRIPTION_ITEM_METHODS]
    if any(item.status == SubscriptionItemStatus.KO for item in subscription_items):
        return BeneficiaryActivationStatus.KO
    if any(item.status == SubscriptionItemStatus.SUSPICIOUS for item in subscription_items):
        return BeneficiaryActivationStatus.SUSPICIOUS
    if any(item.status in (SubscriptionItemStatus.TODO, SubscriptionItemStatus.PENDING) for item in subscription_items):
        return BeneficiaryActivationStatus.INCOMPLETE

    return BeneficiaryActivationStatus.NOT_APPLICABLE


def on_admin_review(review: fraud_models.BeneficiaryFraudReview, user: users_models.User, data: dict) -> None:
    if review.review == fraud_models.FraudReviewStatus.OK.value:
        fraud_check = fraud_api.get_last_filled_identity_fraud_check(user)
        if not fraud_check:
            flask.flash("Pas de vérification d'identité effectuée", "error")
            return

        source_data: common_fraud_models.IdentityCheckContent = fraud_check.source_data()  # type: ignore [assignment]

        try:
            _check_id_piece_number_unicity(user, source_data.get_id_piece_number())
            _check_ine_hash_unicity(user, source_data.get_ine_hash())
        except exceptions.DuplicateIdPieceNumber as e:
            flask.flash(
                f"Le numéro de CNI {e.id_piece_number} est déjà utilisé par l'utilisateur {e.duplicate_user_id}",
                "error",
            )
            return
        except exceptions.DuplicateIneHash as e:
            flask.flash(
                f"Le numéro INE {e.ine_hash} est déjà utilisé par l'utilisateur {e.duplicate_user_id}",
                "error",
            )
            return

        users_api.update_user_information_from_external_source(user, source_data)
        if data["eligibility"] == "Par défaut":
            eligibility = fraud_api.decide_eligibility(
                user, source_data.get_birth_date(), source_data.get_registration_datetime()
            )

            if not eligibility:
                flask.flash(
                    "Aucune éligibilité trouvée. Veuillez choisir une autre Eligibilité que 'Par défaut'", "error"
                )
                return
        else:
            eligibility = users_models.EligibilityType[data["eligibility"]]
        try:
            subscription_api.activate_beneficiary_for_eligibility(user, fraud_check.get_detailed_source(), eligibility)
            flask.flash(f"L'utilisateur a bien été activé en tant que bénéficiaire '{eligibility.value}'", "success")

        except subscription_exceptions.InvalidEligibilityTypeException:
            flask.flash(f"L'égibilité '{eligibility.value}' n'existe pas !", "error")
            return
        except subscription_exceptions.InvalidAgeException as exc:
            if exc.age is None:
                flask.flash("L'âge de l'utilisateur à l'inscription n'a pas pu être déterminé", "error")
            else:
                flask.flash(
                    f"L'âge de l'utilisateur à l'inscription ({exc.age} ans) est incompatible avec l'éligibilité choisie",
                    "error",
                )
            return
        except subscription_exceptions.CannotUpgradeBeneficiaryRole:
            flask.flash(f"L'utilisateur ne peut pas être promu au rôle {eligibility.value}", "error")
            return
        except payment_exceptions.UserHasAlreadyActiveDeposit:
            flask.flash(f"L'utilisateur bénéficie déjà d'un déposit non expiré du type '{eligibility.value}'", "error")
            return
        except payment_exceptions.DepositTypeAlreadyGrantedException:
            flask.flash("Un déposit de ce type a déjà été créé", "error")
            return

    elif review.review == fraud_models.FraudReviewStatus.REDIRECTED_TO_DMS.value:
        review.reason += " ; Redirigé vers DMS"  # type: ignore [operator]

        send_subscription_document_error_email(user.email, "unread-document")
        flask.flash("L'utilisateur  à été redirigé vers DMS")
        subscription_messages.on_redirect_to_dms_from_idcheck(user)
    elif review.review == fraud_models.FraudReviewStatus.KO.value:
        subscription_messages.on_fraud_review_ko(user)

    db.session.add(review)
    db.session.commit()

    flask.flash("Une revue manuelle ajoutée pour l'utilisateur")


def _check_id_piece_number_unicity(user: users_models.User, id_piece_number: Optional[str]) -> None:
    if not id_piece_number:
        return

    duplicate_user = fraud_api.find_duplicate_id_piece_number_user(id_piece_number, user.id)

    if duplicate_user:
        raise exceptions.DuplicateIdPieceNumber(id_piece_number, duplicate_user.id)


def _check_ine_hash_unicity(user: users_models.User, ine_hash: Optional[str]) -> None:
    if not ine_hash:
        return

    duplicate_user = fraud_api.find_duplicate_ine_hash_user(ine_hash, user.id)

    if duplicate_user:
        raise exceptions.DuplicateIneHash(ine_hash, duplicate_user.id)
